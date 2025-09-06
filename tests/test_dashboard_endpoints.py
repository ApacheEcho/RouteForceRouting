import pytest


@pytest.fixture
def client():
    from app import create_app

    app = create_app('testing', testing=True)
    with app.test_client() as c:
        yield c


def test_system_status(client):
    resp = client.get('/dashboard/api/system/status')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)
    assert data.get('success') is True


def test_performance_history(client):
    resp = client.get('/dashboard/api/performance/history')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)
    assert data.get('success') is True


def test_performance_alerts(client):
    resp = client.get('/dashboard/api/performance/alerts')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)
    assert data.get('success') is True


def test_ml_insights(client):
    resp = client.get('/dashboard/api/ml/insights')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)
    assert data.get('success') is True


def test_predictive_analytics(client):
    resp = client.get('/dashboard/api/analytics/predictive')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)
    assert data.get('success') is True


def test_optimization_insights(client):
    resp = client.get('/dashboard/api/optimization/insights')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)
    assert data.get('success') is True


def test_recent_routes(client):
    resp = client.get('/dashboard/api/routes/recent')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)
    assert 'routes' in data

