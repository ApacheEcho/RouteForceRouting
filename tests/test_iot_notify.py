"""
Test push notification API for IoT devices
"""
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app("testing", testing=True)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_push_notification(client):
    # Register a device
    reg = client.post("/api/iot/register", json={"device_type": "sensor", "owner": "user_notify"})
    device_id = reg.get_json()["device_id"]
    # Send notification
    resp = client.post("/api/iot/notify", json={
        "device_id": device_id,
        "title": "Test Alert",
        "body": "This is a test notification.",
        "data": {"foo": "bar"}
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["message"] == "Notification sent"

    # Try with missing fields
    resp2 = client.post("/api/iot/notify", json={"device_id": device_id, "title": "Missing body"})
    assert resp2.status_code == 400
    data2 = resp2.get_json()
    assert data2["success"] is False
    assert "body required" in data2["error"]

    # Try with unregistered device
    resp3 = client.post("/api/iot/notify", json={"device_id": "not_a_device", "title": "X", "body": "Y"})
    assert resp3.status_code == 400
    data3 = resp3.get_json()
    assert data3["success"] is False
    assert "not registered" in data3["error"]
