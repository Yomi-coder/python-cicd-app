import pytest
from app import app

@pytest.fixture
def client():
    # Creates a test client — no real server needed
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_home_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200

def test_home_returns_message(client):
    response = client.get("/")
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Hello from CI/CD Pipeline!"

def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "OK"

def test_info_endpoint(client):
    response = client.get("/info")
    assert response.status_code == 200
    data = response.get_json()
    assert data["language"] == "Python + Flask" 