"""
Monitoring and Metrics Collection for MS-Passengers Database Ingestion
Prometheus metrics and performance monitoring
"""

import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from collections import defaultdict, deque

from prometheus_client import Counter, Histogram, Gauge, start_http_server, CollectorRegistry
from utils.logger import get_logger


class MetricsCollector:
    """Prometheus metrics collector for ingestion monitoring"""
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or CollectorRegistry()
        self.logger = get_logger(self.__class__.__name__)
        
        # Metrics server
        self._metrics_server = None
        self._metrics_port = 8091
        
        # Performance tracking
        self._recent_operations = deque(maxlen=1000)
        self._start_time = time.time()
        
        # Initialize Prometheus metrics
        self._init_metrics()
        
    def _init_metrics(self):
        """Initialize Prometheus metrics"""
        
        # Extraction metrics
        self.records_extracted_total = Counter(
            'ingestion_records_extracted_total',
            'Total number of records extracted',
            ['operation_type', 'table'],
            registry=self.registry
        )
        
        self.extraction_duration_seconds = Histogram(
            'ingestion_extraction_duration_seconds',
            'Time spent extracting data',
            ['operation_type', 'table'],
            registry=self.registry
        )
        
        self.extraction_errors_total = Counter(
            'ingestion_extraction_errors_total',
            'Total extraction errors',
            ['operation_type', 'table', 'error_type'],
            registry=self.registry
        )
        
        # Database metrics
        self.database_connections_active = Gauge(
            'ingestion_database_connections_active',
            'Number of active database connections',
            registry=self.registry
        )
        
        self.database_query_duration_seconds = Histogram(
            'ingestion_database_query_duration_seconds',
            'Database query execution time',
            ['query_type'],
            registry=self.registry
        )
        
        self.database_records_count = Gauge(
            'ingestion_database_records_count',
            'Current number of records in source table',
            ['table'],
            registry=self.registry
        )
        
        # Storage metrics
        self.storage_operations_total = Counter(
            'ingestion_storage_operations_total',
            'Total storage operations',
            ['operation', 'provider', 'status'],
            registry=self.registry
        )
        
        self.storage_operation_duration_seconds = Histogram(
            'ingestion_storage_operation_duration_seconds',
            'Storage operation duration',
            ['operation', 'provider'],
            registry=self.registry
        )
        
        self.storage_bytes_transferred = Counter(
            'ingestion_storage_bytes_transferred_total',
            'Total bytes transferred to storage',
            ['operation', 'provider'],
            registry=self.registry
        )
        
        # CDC metrics
        self.cdc_changes_processed_total = Counter(
            'ingestion_cdc_changes_processed_total',
            'Total CDC changes processed',
            ['change_type', 'table'],
            registry=self.registry
        )
        
        self.cdc_lag_seconds = Gauge(
            'ingestion_cdc_lag_seconds',
            'CDC replication lag in seconds',
            registry=self.registry
        )
        
        # Data quality metrics
        self.data_quality_score = Gauge(
            'ingestion_data_quality_score',
            'Data quality score (0-1)',
            ['table'],
            registry=self.registry
        )
        
        self.validation_failures_total = Counter(
            'ingestion_validation_failures_total',
            'Total validation failures',
            ['table', 'failure_type'],
            registry=self.registry
        )
        
        # System metrics
        self.ingestion_uptime_seconds = Gauge(
            'ingestion_uptime_seconds',
            'Ingestion service uptime in seconds',
            registry=self.registry
        )
        
        self.ingestion_health_status = Gauge(
            'ingestion_health_status',
            'Health status (1=healthy, 0=unhealthy)',
            registry=self.registry
        )
    
    async def start(self, port: int = 8091):
        """Start metrics collection and HTTP server"""
        self._metrics_port = port
        
        try:
            # Start Prometheus HTTP server
            start_http_server(port, registry=self.registry)
            self.logger.info(f"Metrics server started on port {port}")
            
            # Start background metrics collection
            asyncio.create_task(self._collect_system_metrics())
            
        except Exception as e:
            self.logger.error(f"Failed to start metrics server: {str(e)}")
            raise
    
    async def _collect_system_metrics(self):
        """Continuously collect system metrics"""
        while True:
            try:
                # Update uptime
                uptime = time.time() - self._start_time
                self.ingestion_uptime_seconds.set(uptime)
                
                # Sleep before next collection
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error collecting system metrics: {str(e)}")
                await asyncio.sleep(60)
    
    def record_extraction(
        self,
        operation_type: str,
        table: str,
        records_count: int,
        duration: float,
        error: Optional[str] = None
    ):
        """Record extraction operation metrics"""
        try:
            if error:
                self.extraction_errors_total.labels(
                    operation_type=operation_type,
                    table=table,
                    error_type=error
                ).inc()
            else:
                self.records_extracted_total.labels(
                    operation_type=operation_type,
                    table=table
                ).inc(records_count)
                
                self.extraction_duration_seconds.labels(
                    operation_type=operation_type,
                    table=table
                ).observe(duration)
            
            # Track recent operations
            self._recent_operations.append({
                'timestamp': datetime.now(timezone.utc),
                'operation_type': operation_type,
                'table': table,
                'records_count': records_count,
                'duration': duration,
                'error': error
            })
            
        except Exception as e:
            self.logger.error(f"Failed to record extraction metrics: {str(e)}")
    
    def record_database_operation(
        self,
        query_type: str,
        duration: float,
        active_connections: Optional[int] = None
    ):
        """Record database operation metrics"""
        try:
            self.database_query_duration_seconds.labels(
                query_type=query_type
            ).observe(duration)
            
            if active_connections is not None:
                self.database_connections_active.set(active_connections)
                
        except Exception as e:
            self.logger.error(f"Failed to record database metrics: {str(e)}")
    
    def record_storage_operation(
        self,
        operation: str,
        provider: str,
        duration: float,
        bytes_transferred: int = 0,
        success: bool = True
    ):
        """Record storage operation metrics"""
        try:
            status = "success" if success else "error"
            
            self.storage_operations_total.labels(
                operation=operation,
                provider=provider,
                status=status
            ).inc()
            
            if success:
                self.storage_operation_duration_seconds.labels(
                    operation=operation,
                    provider=provider
                ).observe(duration)
                
                if bytes_transferred > 0:
                    self.storage_bytes_transferred.labels(
                        operation=operation,
                        provider=provider
                    ).inc(bytes_transferred)
                    
        except Exception as e:
            self.logger.error(f"Failed to record storage metrics: {str(e)}")
    
    def record_cdc_change(self, change_type: str, table: str, lag_seconds: Optional[float] = None):
        """Record CDC change metrics"""
        try:
            self.cdc_changes_processed_total.labels(
                change_type=change_type,
                table=table
            ).inc()
            
            if lag_seconds is not None:
                self.cdc_lag_seconds.set(lag_seconds)
                
        except Exception as e:
            self.logger.error(f"Failed to record CDC metrics: {str(e)}")
    
    def record_data_quality(self, table: str, quality_score: float, validation_failures: int = 0):
        """Record data quality metrics"""
        try:
            self.data_quality_score.labels(table=table).set(quality_score)
            
            if validation_failures > 0:
                self.validation_failures_total.labels(
                    table=table,
                    failure_type="quality_check"
                ).inc(validation_failures)
                
        except Exception as e:
            self.logger.error(f"Failed to record quality metrics: {str(e)}")
    
    def update_table_count(self, table: str, count: int):
        """Update table record count metric"""
        try:
            self.database_records_count.labels(table=table).set(count)
        except Exception as e:
            self.logger.error(f"Failed to update table count: {str(e)}")
    
    def set_health_status(self, healthy: bool):
        """Update health status metric"""
        try:
            self.ingestion_health_status.set(1 if healthy else 0)
        except Exception as e:
            self.logger.error(f"Failed to set health status: {str(e)}")
    
    def get_recent_operations(self, limit: int = 100) -> list:
        """Get recent operations for monitoring"""
        return list(self._recent_operations)[-limit:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        try:
            recent_ops = list(self._recent_operations)
            
            if not recent_ops:
                return {
                    "total_operations": 0,
                    "average_duration": 0,
                    "total_records": 0,
                    "operations_per_minute": 0,
                    "error_rate": 0
                }
            
            # Calculate metrics from recent operations
            total_ops = len(recent_ops)
            total_records = sum(op.get('records_count', 0) for op in recent_ops)
            total_duration = sum(op.get('duration', 0) for op in recent_ops)
            errors = sum(1 for op in recent_ops if op.get('error'))
            
            # Time window analysis
            now = datetime.now(timezone.utc)
            recent_window = [op for op in recent_ops 
                           if (now - op['timestamp']).total_seconds() <= 300]  # Last 5 minutes
            
            ops_per_minute = len(recent_window) / 5 if recent_window else 0
            
            return {
                "total_operations": total_ops,
                "average_duration": total_duration / total_ops if total_ops > 0 else 0,
                "total_records": total_records,
                "operations_per_minute": ops_per_minute,
                "error_rate": errors / total_ops if total_ops > 0 else 0,
                "uptime_seconds": time.time() - self._start_time
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get performance summary: {str(e)}")
            return {}
    
    def reset_metrics(self):
        """Reset metrics (mainly for testing)"""
        try:
            self._recent_operations.clear()
            self._start_time = time.time()
            self.logger.info("Metrics reset completed")
        except Exception as e:
            self.logger.error(f"Failed to reset metrics: {str(e)}")
