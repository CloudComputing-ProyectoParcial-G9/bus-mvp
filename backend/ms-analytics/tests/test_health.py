"""
Test health endpoints
"""

import pytest
from fastapi import status


def test_health_check(client, mock_env):
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "status" in data
    assert "environment" in data
    assert "services" in data
    assert data["environment"] == "local"


def test_readiness_check(client, mock_env):
    """Test readiness probe endpoint"""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["status"] == "ready"
    assert "timestamp" in data


def test_liveness_check(client, mock_env):
    """Test liveness probe endpoint"""
    response = client.get("/api/v1/health/live")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["status"] == "alive"
    assert "timestamp" in data
