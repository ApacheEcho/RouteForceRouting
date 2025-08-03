import pytest
from app import app
from cryptography.fernet import Fernet
import os

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def encrypt_payload(data: bytes) -> bytes:
    key = os.environ.get("FERNET_KEY").encode()
    f = Fernet(key)
    return f.encrypt(data)

def test_successful_sync_from_rep(client):
    # Simulate encrypted payload
    payload = encrypt_payload(b'{"route_id": "r1", "stores": [1,2], "tasks": ["visit"]}')
    headers = {"Authorization": "Bearer VALID_REP_JWT"}
    resp = client.post("/api/sync", data=payload, headers=headers)
    assert resp.status_code == 200
    assert resp.json["status"] == "ok"

def test_duplicate_sync_conflict(client):
    payload = encrypt_payload(b'{"route_id": "r1", "stores": [1,2], "tasks": ["visit"]}')
    headers = {"Authorization": "Bearer VALID_REP_JWT"}
    client.post("/api/sync", data=payload, headers=headers)
    resp = client.post("/api/sync", data=payload, headers=headers)
    assert resp.status_code in (200, 409)

def test_malformed_encryption_blob(client):
    headers = {"Authorization": "Bearer VALID_REP_JWT"}
    resp = client.post("/api/sync", data=b'invalid', headers=headers)
    assert resp.status_code == 400
    assert "error" in resp.json
