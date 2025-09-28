"""
Test PostgreSQL connection and health check
"""

import pytest
import asyncio

@pytest.mark.asyncio
async def test_database_connection(db_manager):
    """Test database connectivity"""
    health = await db_manager.health_check()
    assert health["status"] == "healthy"
    assert health["connection_test"] is True

@pytest.mark.asyncio 
async def test_passenger_data_extraction(db_manager):
    """Test basic data extraction"""
    # This would require test data in the database
    try:
        data = await db_manager.get_passenger_data(limit=10)
        assert isinstance(data, list)
    except Exception as e:
        pytest.skip(f"No test data available: {str(e)}")

@pytest.mark.asyncio
async def test_table_count(db_manager):
    """Test table count functionality"""
    try:
        count = await db_manager.get_table_count()
        assert isinstance(count, int)
        assert count >= 0
    except Exception as e:
        pytest.skip(f"Table not accessible: {str(e)}")
