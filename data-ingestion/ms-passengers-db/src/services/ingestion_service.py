"""
Ingestion Service for MS-Passengers Database
Main orchestration service for data extraction and processing
"""

import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from enum import Enum

from utils.logger import get_logger, log_ingestion_metrics


class IngestionStatus(Enum):
    """Ingestion service status"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    IDLE = "idle"
    ERROR = "error"
    STOPPING = "stopping"
    STOPPED = "stopped"


class IngestionService:
    """Main ingestion orchestration service"""
    
    def __init__(self, extractor, settings, metrics):
        self.extractor = extractor
        self.settings = settings
        self.metrics = metrics
        self.logger = get_logger(self.__class__.__name__)
        
        # Service state
        self._status = IngestionStatus.INITIALIZING
        self._start_time = time.time()
        self._last_operation_time: Optional[datetime] = None
        self._stop_event = asyncio.Event()
        
        # Operation counters
        self._operations_completed = 0
        self._total_records_processed = 0
        self._errors = 0
        
        # Task management
        self._background_tasks = set()
        self._scheduler_task: Optional[asyncio.Task] = None
        self._cdc_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the ingestion service"""
        try:
            self.logger.info("Starting MS-Passengers ingestion service")
            self._status = IngestionStatus.RUNNING
            self._start_time = time.time()
            
            # Initialize extractor metrics
            self.metrics.set_health_status(True)
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.logger.info("Ingestion service started successfully")
            
            # Main service loop
            await self._run_service_loop()
            
        except Exception as e:
            self._status = IngestionStatus.ERROR
            self.metrics.set_health_status(False)
            self.logger.error(f"Ingestion service failed: {str(e)}", exc_info=True)
            raise
        finally:
            await self._cleanup()
    
    async def stop(self):
        """Stop the ingestion service"""
        self.logger.info("Stopping ingestion service")
        self._status = IngestionStatus.STOPPING
        self._stop_event.set()
        
        # Cancel background tasks
        if self._scheduler_task:
            self._scheduler_task.cancel()
        if self._cdc_task:
            self._cdc_task.cancel()
        
        # Cancel all background tasks
        for task in self._background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        self._status = IngestionStatus.STOPPED
        self.logger.info("Ingestion service stopped")
    
    async def _start_background_tasks(self):
        """Start background processing tasks"""
        # Scheduler task for regular operations
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        self._background_tasks.add(self._scheduler_task)
        
        # CDC task if enabled
        if self.settings.ingestion.cdc_enabled:
            self._cdc_task = asyncio.create_task(self._cdc_loop())
            self._background_tasks.add(self._cdc_task)
        
        # Metrics update task
        metrics_task = asyncio.create_task(self._metrics_loop())
        self._background_tasks.add(metrics_task)
    
    async def _run_service_loop(self):
        """Main service loop"""
        try:
            while not self._stop_event.is_set():
                try:
                    # Update status
                    if self._status == IngestionStatus.RUNNING:
                        self._status = IngestionStatus.IDLE
                    
                    # Wait for stop signal or timeout
                    await asyncio.wait_for(self._stop_event.wait(), timeout=30)
                    
                except asyncio.TimeoutError:
                    # Timeout is expected, continue loop
                    continue
                except Exception as e:
                    self.logger.error(f"Error in service loop: {str(e)}")
                    await asyncio.sleep(5)
                    
        except Exception as e:
            self.logger.error(f"Service loop failed: {str(e)}", exc_info=True)
            self._status = IngestionStatus.ERROR
            raise
    
    async def _scheduler_loop(self):
        """Background scheduler for regular extractions"""
        try:
            self.logger.info("Starting extraction scheduler")
            
            # Initial full sync if needed
            if self.extractor.should_perform_full_sync():
                await self._perform_full_sync()
            
            while not self._stop_event.is_set():
                try:
                    # Check if full sync is needed
                    if self.extractor.should_perform_full_sync():
                        self.logger.info("Scheduled full sync required")
                        await self._perform_full_sync()
                    else:
                        # Perform incremental sync
                        await self._perform_incremental_sync()
                    
                    # Wait for next extraction interval
                    await asyncio.sleep(self.settings.ingestion.extraction_interval)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self._errors += 1
                    self.logger.error(f"Scheduler error: {str(e)}", exc_info=True)
                    await asyncio.sleep(60)  # Wait before retrying
                    
        except asyncio.CancelledError:
            self.logger.info("Scheduler loop cancelled")
        except Exception as e:
            self.logger.error(f"Scheduler loop failed: {str(e)}", exc_info=True)
    
    async def _cdc_loop(self):
        """Background CDC processing loop"""
        try:
            self.logger.info("Starting CDC processing loop")
            
            async for change in self.extractor.extract_cdc_changes():
                try:
                    if self._stop_event.is_set():
                        break
                    
                    # Process CDC change
                    await self._process_cdc_change(change)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self._errors += 1
                    self.logger.error(f"CDC processing error: {str(e)}", exc_info=True)
                    continue
                    
        except asyncio.CancelledError:
            self.logger.info("CDC loop cancelled")
        except Exception as e:
            self.logger.error(f"CDC loop failed: {str(e)}", exc_info=True)
    
    async def _metrics_loop(self):
        """Background metrics collection loop"""
        try:
            while not self._stop_event.is_set():
                try:
                    # Update service metrics
                    await self._update_service_metrics()
                    
                    # Wait before next update
                    await asyncio.sleep(30)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Metrics update error: {str(e)}")
                    await asyncio.sleep(60)
                    
        except asyncio.CancelledError:
            self.logger.info("Metrics loop cancelled")
    
    async def _perform_full_sync(self):
        """Perform complete data extraction"""
        start_time = time.time()
        total_records = 0
        batch_count = 0
        
        try:
            self.logger.info("Starting full data synchronization")
            self._status = IngestionStatus.RUNNING
            
            offset = 0
            has_more = True
            
            while has_more and not self._stop_event.is_set():
                # Extract batch
                result = await self.extractor.extract_full(
                    batch_size=self.settings.ingestion.batch_size,
                    offset=offset
                )
                
                # Process extracted data
                if result.records:
                    await self._process_extracted_data(result.records, "full_sync")
                    total_records += len(result.records)
                    batch_count += 1
                
                # Update pagination
                has_more = result.has_more
                offset = result.next_offset or (offset + len(result.records))
                
                # Record metrics for this batch
                self.metrics.record_extraction(
                    operation_type="full_sync",
                    table="passengers",
                    records_count=len(result.records),
                    duration=result.extraction_time
                )
                
                self.logger.info(
                    f"Full sync batch {batch_count} completed",
                    records=len(result.records),
                    total_records=total_records,
                    offset=offset,
                    has_more=has_more
                )
                
                # Brief pause between batches
                if has_more:
                    await asyncio.sleep(1)
            
            # Record overall operation
            total_time = time.time() - start_time
            self._operations_completed += 1
            self._total_records_processed += total_records
            self._last_operation_time = datetime.now(timezone.utc)
            
            log_ingestion_metrics(
                self.logger,
                operation="full_sync_complete",
                table="passengers",
                records_processed=total_records,
                processing_time=total_time,
                batches=batch_count
            )
            
        except Exception as e:
            self._errors += 1
            self.logger.error(f"Full sync failed: {str(e)}", exc_info=True)
            self.metrics.record_extraction(
                operation_type="full_sync",
                table="passengers",
                records_count=0,
                duration=time.time() - start_time,
                error="full_sync_error"
            )
            raise
    
    async def _perform_incremental_sync(self):
        """Perform incremental data extraction"""
        start_time = time.time()
        
        try:
            self._status = IngestionStatus.RUNNING
            
            # Extract incremental changes
            result = await self.extractor.extract_incremental()
            
            # Process extracted data
            if result.records:
                await self._process_extracted_data(result.records, "incremental_sync")
                
                self.logger.info(
                    "Incremental sync completed",
                    records=len(result.records),
                    processing_time=result.extraction_time
                )
            else:
                self.logger.debug("No new records in incremental sync")
            
            # Record metrics
            self.metrics.record_extraction(
                operation_type="incremental_sync",
                table="passengers",
                records_count=len(result.records),
                duration=result.extraction_time
            )
            
            # Update counters
            self._operations_completed += 1
            self._total_records_processed += len(result.records)
            self._last_operation_time = datetime.now(timezone.utc)
            
        except Exception as e:
            self._errors += 1
            self.logger.error(f"Incremental sync failed: {str(e)}", exc_info=True)
            self.metrics.record_extraction(
                operation_type="incremental_sync",
                table="passengers",
                records_count=0,
                duration=time.time() - start_time,
                error="incremental_sync_error"
            )
        finally:
            self._status = IngestionStatus.IDLE
    
    async def _process_cdc_change(self, change: Dict[str, Any]):
        """Process individual CDC change"""
        try:
            # Log change
            self.logger.debug(
                "Processing CDC change",
                change_type=change.get("change_type"),
                table=change.get("table")
            )
            
            # Record CDC metrics
            self.metrics.record_cdc_change(
                change_type=change.get("change_type", "unknown"),
                table=change.get("table", "passengers")
            )
            
            # Here you would typically send to storage or message queue
            # For now, we'll just log it
            self.logger.info("CDC change processed", change=change)
            
        except Exception as e:
            self.logger.error(f"Failed to process CDC change: {str(e)}")
    
    async def _process_extracted_data(self, records: list, operation_type: str):
        """Process extracted data records"""
        try:
            # Here you would typically:
            # 1. Send to object storage
            # 2. Send to message queue
            # 3. Transform data
            # 4. Validate data quality
            
            # For now, we'll just log the processing
            self.logger.info(
                f"Processing {len(records)} records from {operation_type}",
                operation=operation_type,
                record_count=len(records)
            )
            
            # Simulate processing time
            await asyncio.sleep(0.1)
            
        except Exception as e:
            self.logger.error(f"Failed to process extracted data: {str(e)}")
            raise
    
    async def _update_service_metrics(self):
        """Update service-level metrics"""
        try:
            # Update health status
            healthy = self._status not in [IngestionStatus.ERROR, IngestionStatus.STOPPED]
            self.metrics.set_health_status(healthy)
            
            # Update other metrics as needed
            # This could include database connection counts, etc.
            
        except Exception as e:
            self.logger.error(f"Failed to update service metrics: {str(e)}")
    
    async def _cleanup(self):
        """Cleanup resources"""
        try:
            self.logger.info("Cleaning up ingestion service resources")
            
            # Cancel any remaining tasks
            for task in self._background_tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete
            if self._background_tasks:
                await asyncio.gather(*self._background_tasks, return_exceptions=True)
            
            self._status = IngestionStatus.STOPPED
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {str(e)}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current service status"""
        return {
            "status": self._status.value,
            "uptime_seconds": time.time() - self._start_time,
            "operations_completed": self._operations_completed,
            "total_records_processed": self._total_records_processed,
            "errors": self._errors,
            "last_operation_time": self._last_operation_time.isoformat() if self._last_operation_time else None
        }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        status = await self.get_status()
        extractor_metrics = self.extractor.get_extraction_metrics()
        performance_summary = self.metrics.get_performance_summary()
        
        return {
            "service": status,
            "extraction": extractor_metrics,
            "performance": performance_summary
        }
    
    def get_uptime(self) -> float:
        """Get service uptime in seconds"""
        return time.time() - self._start_time
