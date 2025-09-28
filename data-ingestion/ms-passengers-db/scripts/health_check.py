#!/usr/bin/env python3
"""
Health Check Script for MS-Passengers Database Ingestion
Simple health check that can be run from Docker or command line
"""

import sys
import asyncio
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from config.settings import Settings
    from core.database import DatabaseManager
    from utils.logger import setup_logging
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


async def health_check():
    """Perform basic health check"""
    logger = setup_logging(log_level="INFO", log_format="text")
    
    try:
        # Load settings
        settings = Settings()
        
        # Create database manager
        db_manager = DatabaseManager(settings)
        await db_manager.initialize()
        
        # Perform health check
        health = await db_manager.health_check()
        
        # Close connections
        await db_manager.close()
        
        # Return status
        if health["status"] == "healthy":
            print("✓ Health check passed")
            print(f"✓ Database connection: OK")
            print(f"✓ Passenger count: {health.get('passenger_count', 'N/A')}")
            print(f"✓ Response time: {health.get('response_time_ms', 'N/A')}ms")
            return 0
        else:
            print("✗ Health check failed")
            print(f"✗ Error: {health.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"✗ Health check failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(health_check())
    sys.exit(exit_code)
