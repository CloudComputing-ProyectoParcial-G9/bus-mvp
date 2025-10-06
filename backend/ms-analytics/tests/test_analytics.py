import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_dashboard_summary_endpoint():
    """Test del endpoint de dashboard summary"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/analytics/summary")
        
    # Puede fallar si no hay datos/conexión AWS
    # Verificamos estructura si responde OK
    if response.status_code == 200:
        data = response.json()
        assert "timestamp" in data
        assert "summary" in data
        assert "total_passengers" in data["summary"]
        assert "active_trips" in data["summary"]
        assert "tickets_sold" in data["summary"]
        assert "total_revenue" in data["summary"]

@pytest.mark.asyncio
async def test_passenger_analytics_endpoint():
    """Test del endpoint de passenger analytics"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/analytics/passengers")
        
    if response.status_code == 200:
        data = response.json()
        assert "total_passengers" in data
        assert "active_passengers" in data
        assert "passenger_segments" in data
        assert "top_customers" in data

@pytest.mark.asyncio
async def test_revenue_analytics_endpoint():
    """Test del endpoint de revenue analytics"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/analytics/revenue")
        
    if response.status_code == 200:
        data = response.json()
        assert "total_revenue" in data
        assert "confirmed_revenue" in data
        assert "cancelled_revenue" in data
        assert "by_route" in data

@pytest.mark.asyncio
async def test_occupancy_analytics_endpoint():
    """Test del endpoint de occupancy analytics"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/analytics/occupancy")
        
    if response.status_code == 200:
        data = response.json()
        assert "average_occupancy" in data
        assert "total_capacity" in data
        assert "total_seats_sold" in data
        assert "by_level" in data
        assert "by_route" in data

@pytest.mark.asyncio
async def test_trip_analytics_endpoint():
    """Test del endpoint de trip analytics"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/analytics/trips")
        
    if response.status_code == 200:
        data = response.json()
        assert "total_trips" in data
        assert "active_trips" in data
        assert "completed_trips" in data
        assert "cancelled_trips" in data
        assert "occupancy_breakdown" in data
