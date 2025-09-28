"""
Test configuration and fixtures
"""

import pytest
from fastapi.testclient import TestClient
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app


@pytest.fixture
def client():
    """Test client fixture"""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for testing"""
    monkeypatch.setenv("ENVIRONMENT", "local")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("LOG_LEVEL", "INFO")
