"""
Data Extractor for MS-Passengers Database
Handles full and incremental data extraction from PostgreSQL
"""

import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime, timezone, timedelta
import json
from dataclasses import dataclass

from utils.logger import get_logger, log_ingestion_metrics


@dataclass
class ExtractionResult:
    """Result of a data extraction operation"""
    records: List[Dict[str, Any]]
    total_count: int
    extraction_time: float
    has_more: bool = False
    next_offset: Optional[int] = None
    last_timestamp: Optional[datetime] = None


class PassengerDataExtractor:
    """PostgreSQL data extractor for passenger data"""
    
    def __init__(self, db_manager, settings):
        self.db_manager = db_manager
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__)
        
        # State tracking
        self._last_full_sync: Optional[datetime] = None
        self._last_cdc_timestamp: Optional[datetime] = None
        self._extraction_metrics = {
            "total_records_extracted": 0,
            "full_syncs_completed": 0,
            "incremental_syncs_completed": 0,
            "cdc_changes_processed": 0,
            "last_extraction_time": None,
            "errors": 0
        }
    
    async def extract_full(
        self,
        batch_size: Optional[int] = None,
        offset: int = 0
    ) -> ExtractionResult:
        """
        Perform full data extraction from passengers table
        
        Args:
            batch_size: Number of records per batch
            offset: Starting offset for pagination
            
        Returns:
            ExtractionResult with extracted data
        """
        start_time = datetime.now()
        batch_size = batch_size or self.settings.ingestion.batch_size
        
        try:
            self.logger.info(
                "Starting full data extraction",
                batch_size=batch_size,
                offset=offset
            )
            
            # Extract data from database
            records = await self.db_manager.get_passenger_data(
                limit=batch_size,
                offset=offset
            )
            
            # Get total count for pagination
            total_count = await self.db_manager.get_table_count()
            
            # Determine if there are more records
            has_more = len(records) == batch_size and (offset + batch_size) < total_count
            next_offset = offset + batch_size if has_more else None
            
            # Get last timestamp for CDC tracking
            last_timestamp = None
            if records:
                last_timestamp = max(
                    record.get('updated_at', record.get('created_at'))
                    for record in records
                    if record.get('updated_at') or record.get('created_at')
                )
            
            # Process records
            processed_records = self._process_records(records, "full_extraction")
            
            # Calculate metrics
            extraction_time = (datetime.now() - start_time).total_seconds()
            
            # Update metrics
            self._extraction_metrics["total_records_extracted"] += len(processed_records)
            self._extraction_metrics["last_extraction_time"] = datetime.now(timezone.utc)
            
            if offset == 0:  # First batch of full sync
                self._extraction_metrics["full_syncs_completed"] += 1
                self._last_full_sync = datetime.now(timezone.utc)
            
            # Log metrics
            log_ingestion_metrics(
                self.logger,
                operation="full_extraction",
                table="passengers",
                records_processed=len(processed_records),
                processing_time=extraction_time,
                total_count=total_count,
                offset=offset,
                has_more=has_more
            )
            
            return ExtractionResult(
                records=processed_records,
                total_count=total_count,
                extraction_time=extraction_time,
                has_more=has_more,
                next_offset=next_offset,
                last_timestamp=last_timestamp
            )
            
        except Exception as e:
            self._extraction_metrics["errors"] += 1
            self.logger.error(
                f"Full extraction failed: {str(e)}",
                batch_size=batch_size,
                offset=offset,
                exc_info=True
            )
            raise
    
    async def extract_incremental(
        self,
        since: Optional[datetime] = None,
        batch_size: Optional[int] = None
    ) -> ExtractionResult:
        """
        Perform incremental data extraction based on timestamp
        
        Args:
            since: Extract records modified since this timestamp
            batch_size: Number of records per batch
            
        Returns:
            ExtractionResult with extracted data
        """
        start_time = datetime.now()
        batch_size = batch_size or self.settings.ingestion.batch_size
        
        # Use provided timestamp or last known timestamp
        if since is None:
            since = self._last_cdc_timestamp or (datetime.now(timezone.utc) - timedelta(hours=1))
        
        try:
            self.logger.info(
                "Starting incremental extraction",
                since=since.isoformat(),
                batch_size=batch_size
            )
            
            # Extract data modified since timestamp
            records = await self.db_manager.get_passenger_data(
                limit=batch_size,
                since=since
            )
            
            # Process records
            processed_records = self._process_records(records, "incremental_extraction")
            
            # Get last timestamp for next incremental sync
            last_timestamp = since
            if records:
                last_timestamp = max(
                    record.get('updated_at', record.get('created_at', since))
                    for record in records
                    if record.get('updated_at') or record.get('created_at')
                )
                self._last_cdc_timestamp = last_timestamp
            
            # Calculate metrics
            extraction_time = (datetime.now() - start_time).total_seconds()
            
            # Update metrics
            self._extraction_metrics["total_records_extracted"] += len(processed_records)
            self._extraction_metrics["incremental_syncs_completed"] += 1
            self._extraction_metrics["last_extraction_time"] = datetime.now(timezone.utc)
            
            # Log metrics
            log_ingestion_metrics(
                self.logger,
                operation="incremental_extraction",
                table="passengers",
                records_processed=len(processed_records),
                processing_time=extraction_time,
                since=since.isoformat()
            )
            
            return ExtractionResult(
                records=processed_records,
                total_count=len(processed_records),
                extraction_time=extraction_time,
                last_timestamp=last_timestamp
            )
            
        except Exception as e:
            self._extraction_metrics["errors"] += 1
            self.logger.error(
                f"Incremental extraction failed: {str(e)}",
                since=since.isoformat() if since else None,
                exc_info=True
            )
            raise
    
    async def extract_cdc_changes(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Extract real-time changes using CDC
        
        Yields:
            Individual change events as they occur
        """
        if not self.settings.ingestion.cdc_enabled:
            self.logger.warning("CDC not enabled, skipping change stream")
            return
        
        try:
            self.logger.info("Starting CDC change extraction")
            
            async for change in self.db_manager.get_cdc_changes():
                try:
                    # Process change event
                    processed_change = self._process_cdc_change(change)
                    
                    if processed_change:
                        # Update metrics
                        self._extraction_metrics["cdc_changes_processed"] += 1
                        self._extraction_metrics["last_extraction_time"] = datetime.now(timezone.utc)
                        
                        # Update timestamp tracking
                        if change.get('timestamp'):
                            self._last_cdc_timestamp = change['timestamp']
                        
                        yield processed_change
                        
                except Exception as e:
                    self._extraction_metrics["errors"] += 1
                    self.logger.error(f"Failed to process CDC change: {str(e)}", exc_info=True)
                    continue
                    
        except Exception as e:
            self._extraction_metrics["errors"] += 1
            self.logger.error(f"CDC extraction failed: {str(e)}", exc_info=True)
            raise
    
    def _process_records(self, records: List[Dict[str, Any]], extraction_type: str) -> List[Dict[str, Any]]:
        """
        Process and transform raw database records
        
        Args:
            records: Raw records from database
            extraction_type: Type of extraction for metadata
            
        Returns:
            Processed records with metadata
        """
        processed = []
        
        for record in records:
            try:
                # Add extraction metadata
                processed_record = {
                    **record,
                    "_metadata": {
                        "source_system": "ms-passengers",
                        "source_table": "passengers",
                        "extraction_type": extraction_type,
                        "extracted_at": datetime.now(timezone.utc).isoformat(),
                        "extractor_version": "1.0.0"
                    }
                }
                
                # Convert datetime objects to ISO strings
                for key, value in processed_record.items():
                    if isinstance(value, datetime):
                        processed_record[key] = value.isoformat()
                
                # Data quality checks
                if self.settings.ingestion.enable_validation:
                    if self._validate_passenger_record(processed_record):
                        processed.append(processed_record)
                    else:
                        self.logger.warning(
                            "Record failed validation",
                            passenger_id=record.get('passenger_id'),
                            issues="validation_failed"
                        )
                else:
                    processed.append(processed_record)
                    
            except Exception as e:
                self.logger.error(
                    f"Failed to process record: {str(e)}",
                    passenger_id=record.get('passenger_id'),
                    exc_info=True
                )
                continue
        
        return processed
    
    def _process_cdc_change(self, change: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process CDC change event"""
        try:
            return {
                "change_type": change.get("operation"),
                "table": change.get("table"),
                "timestamp": change.get("timestamp", datetime.now(timezone.utc)).isoformat(),
                "payload": change.get("payload"),
                "_metadata": {
                    "source_system": "ms-passengers",
                    "change_source": "postgresql_cdc",
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                    "processor_version": "1.0.0"
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to process CDC change: {str(e)}")
            return None
    
    def _validate_passenger_record(self, record: Dict[str, Any]) -> bool:
        """
        Validate passenger record data quality
        
        Args:
            record: Passenger record to validate
            
        Returns:
            True if record is valid, False otherwise
        """
        try:
            # Required fields
            required_fields = ['passenger_id', 'full_name', 'email']
            for field in required_fields:
                if not record.get(field):
                    return False
            
            # Email format validation (basic)
            email = record.get('email', '').strip()
            if '@' not in email or '.' not in email.split('@')[-1]:
                return False
            
            # Phone format (if present)
            phone = record.get('phone')
            if phone and len(str(phone).replace('+', '').replace('-', '').replace(' ', '')) < 7:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Validation error: {str(e)}")
            return False
    
    def get_extraction_metrics(self) -> Dict[str, Any]:
        """Get current extraction metrics"""
        return {
            **self._extraction_metrics,
            "last_full_sync": self._last_full_sync.isoformat() if self._last_full_sync else None,
            "last_cdc_timestamp": self._last_cdc_timestamp.isoformat() if self._last_cdc_timestamp else None
        }
    
    def should_perform_full_sync(self) -> bool:
        """Determine if a full sync should be performed"""
        if not self.settings.ingestion.full_sync_enabled:
            return False
        
        if self._last_full_sync is None:
            return True
        
        # Check if it's time for scheduled full sync
        now = datetime.now(timezone.utc)
        time_since_last = now - self._last_full_sync
        
        return time_since_last.total_seconds() >= self.settings.ingestion.full_sync_interval
    
    def reset_metrics(self):
        """Reset extraction metrics"""
        self._extraction_metrics = {
            "total_records_extracted": 0,
            "full_syncs_completed": 0,
            "incremental_syncs_completed": 0,
            "cdc_changes_processed": 0,
            "last_extraction_time": None,
            "errors": 0
        }
