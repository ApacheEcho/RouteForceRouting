"""
Test cases for IoT Device Integration API
"""
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app("testing", testing=True)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_register_device(client):
    resp = client.post("/api/iot/register", json={"device_type": "sensor", "owner": "user_1"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["success"] is True
    assert "device_id" in data

def test_ingest_telemetry(client):
    # Register device first
    reg = client.post("/api/iot/register", json={"device_type": "sensor", "owner": "user_2"})
    device_id = reg.get_json()["device_id"]
    # Send telemetry
    resp = client.post("/api/iot/telemetry", json={"device_id": device_id, "telemetry": {"temp": 22.5}})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "received_at" in data

def test_list_devices(client):
    client.post("/api/iot/register", json={"device_type": "sensor", "owner": "user_3"})
    resp = client.get("/api/iot/devices")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert isinstance(data["devices"], list)

def test_list_telemetry(client):
    reg = client.post("/api/iot/register", json={"device_type": "sensor", "owner": "user_4"})
    device_id = reg.get_json()["device_id"]
    client.post("/api/iot/telemetry", json={"device_id": device_id, "telemetry": {"humidity": 55}})
    resp = client.get("/api/iot/telemetry")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert isinstance(data["telemetry"], list)
