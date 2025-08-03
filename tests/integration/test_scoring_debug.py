import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.mark.parametrize("preset", ["balanced", "traffic_aware", "priority_focused"])
def test_scoring_debug_output(client, preset):
    payload = {
        "route": [
            {"name": "Store A", "lat": 40.7128, "lon": -74.0060, "priority": 8},
            {"name": "Store B", "lat": 40.7589, "lon": -73.9851, "priority": 6},
            {"name": "Store C", "lat": 40.7505, "lon": -73.9934, "priority": 9}
        ],
        "preset": preset
    }
    resp = client.post("/api/route/score?debug=true", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "debug" in data
    debug = data["debug"]
    assert "total_score" in debug
    assert "components" in debug
    assert "formula" in debug or "notes" in debug
