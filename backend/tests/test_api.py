import json
from backend import app


def test_health():
    client = app.test_client()
    resp = client.get('/health')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data.get('status') == 'ok'


def test_routes():
    client = app.test_client()
    resp = client.get('/api/routes')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert isinstance(data, list)
    assert len(data) >= 1
