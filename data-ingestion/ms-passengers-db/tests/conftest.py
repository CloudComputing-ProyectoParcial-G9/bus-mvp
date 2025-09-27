"""
Test configuration for MS-Passengers Database Ingestion
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import os

# Test configuration
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://test:test@localhost:5432/test_passengers")
TEST_REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://localhost:6379/1")

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_settings():
    """Create mock settings for testing"""
    from config.settings import Settings
    
    # Override with test values
    os.environ["SQL1_HOST"] = "localhost"
    os.environ["SQL1_PORT"] = "5432"
    os.environ["SQL1_DB"] = "test_passengers"
    os.environ["SQL1_USER"] = "test"
    os.environ["SQL1_PASSWORD"] = "test"
    os.environ["ENVIRONMENT"] = "test"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    return Settings()

@pytest.fixture
async def db_manager(mock_settings):
    """Create database manager for testing"""
    from core.database import DatabaseManager
    
    manager = DatabaseManager(mock_settings)
    await manager.initialize()
    yield manager
    await manager.close()

@pytest.fixture
def metrics_collector():
    """Create metrics collector for testing"""
    from core.monitoring import MetricsCollector
    from prometheus_client import CollectorRegistry
    
    # Use separate registry for tests
    registry = CollectorRegistry()
    return MetricsCollector(registry=registry)
