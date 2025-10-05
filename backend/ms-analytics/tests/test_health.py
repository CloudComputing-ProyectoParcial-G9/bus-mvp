import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_root_endpoint():
    """Test del endpoint raíz"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Bus MVP Analytics API"
    assert data["status"] == "running"
    assert "version" in data
    assert "docs" in data

@pytest.mark.asyncio
async def test_health_check():
    """Test del health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["service"] == "ms-analytics"
    assert "version" in data
    assert "timestamp" in data
    assert "athena_connection" in data
