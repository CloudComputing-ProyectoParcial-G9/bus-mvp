"""
Logging utilities for MS-Passengers Database Ingestion
Structured logging with JSON format support
"""

import logging
import logging.config
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

import structlog


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.thread,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'message']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str, ensure_ascii=False)


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[str] = None,
    service_name: str = "ms-passengers-db-ingestion"
) -> logging.Logger:
    """
    Setup structured logging for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format type ('json' or 'text')
        log_file: Optional log file path
        service_name: Service name for logging context
    
    Returns:
        Configured logger instance
    """
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if log_format == "json" else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Setup standard logging
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    if log_format == "json":
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )
    handlers.append(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        if log_format == "json":
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(
                logging.Formatter(
                    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            )
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=handlers,
        force=True
    )
    
    # Create and configure application logger
    logger = structlog.get_logger(service_name)
    logger.info(
        "Logging configured",
        level=log_level,
        format=log_format,
        file=log_file,
        service=service_name
    )
    
    return logger


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a configured logger instance"""
    return structlog.get_logger(name)


def log_ingestion_metrics(
    logger: structlog.BoundLogger,
    operation: str,
    table: str,
    records_processed: int,
    processing_time: float,
    errors: int = 0,
    **kwargs
):
    """Log structured ingestion metrics"""
    logger.info(
        "Ingestion metrics",
        operation=operation,
        table=table,
        records_processed=records_processed,
        processing_time_seconds=processing_time,
        errors=errors,
        throughput_records_per_second=records_processed / processing_time if processing_time > 0 else 0,
        **kwargs
    )


def log_database_operation(
    logger: structlog.BoundLogger,
    operation: str,
    query_type: str,
    duration: float,
    rows_affected: int = 0,
    **kwargs
):
    """Log database operation metrics"""
    logger.info(
        "Database operation",
        operation=operation,
        query_type=query_type,
        duration_seconds=duration,
        rows_affected=rows_affected,
        **kwargs
    )


def log_storage_operation(
    logger: structlog.BoundLogger,
    operation: str,
    bucket: str,
    key: str,
    size_bytes: Optional[int] = None,
    duration: Optional[float] = None,
    **kwargs
):
    """Log object storage operation"""
    logger.info(
        "Storage operation",
        operation=operation,
        bucket=bucket,
        key=key,
        size_bytes=size_bytes,
        duration_seconds=duration,
        **kwargs
    )
