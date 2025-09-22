import os
from pathlib import Path

# Use a fresh sqlite file for tests to avoid conflicts with a persistent dev DB.
TEST_DB = Path(__file__).parent / "test_dev_passengers.db"
if TEST_DB.exists():
    try:
        TEST_DB.unlink()
    except Exception:
        pass

# Point the application to the test DB before importing the app so the engine
# and tables are created against the test database.
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'healthy'

def test_create_and_get_passenger():
    payload = {
        "full_name": "Test User",
        "email": "testuser@example.com",
        "phone": "+1000000000",
        "document_type": "DNI",
        "document_number": "00000000",
        "date_of_birth": "1990-01-01"
    }
    r = client.post('/passengers', json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data['email'] == payload['email']
    pid = data['passenger_id']

    r2 = client.get(f'/passengers/{pid}')
    assert r2.status_code == 200
    assert r2.json()['email'] == payload['email']
