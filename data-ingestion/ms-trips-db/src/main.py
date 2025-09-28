"""
MS-Trips Database Ingestion - Main Application
MySQL Binlog CDC and full extraction for Bus MVP trips and routes data
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent))

from config.settings import Settings
from core.database import MySQLManager
from core.extractor import TripsDataExtractor
from core.health import HealthCheckServer
from core.monitoring import MetricsCollector
from services.ingestion_service import TripsIngestionService
from utils.logger import setup_logging


async def main():
    """Main application entry point"""
    # Setup logging
    logger = setup_logging()
    logger.info("Starting MS-Trips Database Ingestion Service")
    
    try:
        # Load configuration
        settings = Settings()
        logger.info(f"Configuration loaded - Environment: {settings.environment}")
        
        # Initialize components
        db_manager = MySQLManager(settings)
        extractor = TripsDataExtractor(db_manager, settings)
        metrics_collector = MetricsCollector()
        
        # Initialize ingestion service
        ingestion_service = TripsIngestionService(
            extractor=extractor,
            settings=settings,
            metrics=metrics_collector
        )
        
        # Start health check server
        health_server = HealthCheckServer(
            port=settings.health_check_port,
            db_manager=db_manager,
            ingestion_service=ingestion_service
        )
        
        # Start all services concurrently
        logger.info("Starting all services...")
        await asyncio.gather(
            health_server.start(),
            ingestion_service.start(),
            metrics_collector.start(),
            return_exceptions=True
        )
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Shutting down MS-Trips Database Ingestion Service")


if __name__ == "__main__":
    # Set event loop policy for compatibility
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Run the main application
    asyncio.run(main())
