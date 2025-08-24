import pytest
from flask_jwt_extended import create_access_token
from app import create_app
from app.models.database import db, User
import json

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        # Create admin user
        admin = User(id=1, email='admin@example.com', role='admin')
        admin.set_password('adminpass')
        db.session.add(admin)
        # Create regular user
        user = User(id=2, email='user@example.com', role='user')
        user.set_password('userpass')
        db.session.add(user)
        db.session.commit()
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_token(app):
    with app.app_context():
        return create_access_token(identity=1)

@pytest.fixture
def user_token(app):
    with app.app_context():
        return create_access_token(identity=2)

def test_dashboard_analytics_success(client, admin_token):
    response = client.get(
        '/api/analytics/dashboard',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'data' in data
    assert 'overview' in data['data']
    assert 'routing_performance' in data['data']

def test_dashboard_analytics_unauthorized(client):
    response = client.get('/api/analytics/dashboard')
    assert response.status_code == 401

def test_dashboard_analytics_non_admin(client, user_token):
    response = client.get(
        '/api/analytics/dashboard',
        headers={'Authorization': f'Bearer {user_token}'}
    )
    assert response.status_code == 403

def test_user_activity_success(client, user_token):
    response = client.get(
        '/api/analytics/user-activity',
        headers={'Authorization': f'Bearer {user_token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'data' in data
    d = data['data']
    assert 'user_id' in d
    assert 'monthly_usage' in d
    assert 'favorite_routes' in d
    assert 'performance_stats' in d
    mu = d['monthly_usage']
    assert 'routes_created' in mu
    assert 'api_calls' in mu
    assert 'avg_routes_per_day' in mu
    assert 'peak_usage_day' in mu
    fr = d['favorite_routes']
    assert isinstance(fr, list)
    if fr:
        assert 'route_name' in fr[0]
        assert 'frequency' in fr[0]
        assert 'last_used' in fr[0]
    ps = d['performance_stats']
    assert 'optimization_achievements' in ps
    assert 'routes_shared' in ps
    assert 'collaboration_score' in ps

def test_user_activity_unauthorized(client):
    response = client.get('/api/analytics/user-activity')
    assert response.status_code == 401


def test_route_efficiency_success(client, admin_token):
    response = client.get(
        '/api/analytics/route-efficiency?route_id=route_001',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['route_id'] == 'route_001'
    assert 'efficiency_data' in data
    eff = data['efficiency_data']
    assert 'efficiency_score' in eff
    assert isinstance(eff['efficiency_score'], (int, float))
    assert 'improvement_opportunities' in eff
    assert isinstance(eff['improvement_opportunities'], list)
    assert 'historical_comparison' in eff
    hist = eff['historical_comparison']
    assert 'current_period' in hist
    assert 'previous_period' in hist
    assert 'improvement' in hist


def test_analytics_export_success(client, admin_token):
    response = client.get(
        '/api/analytics/export?type=summary&format=json',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['report_type'] == 'summary'
    assert data['format'] == 'json'
    assert 'data' in data
    d = data['data']
    assert 'period' in d
    assert 'summary' in d
    assert 'key_insights' in d
    assert isinstance(d['key_insights'], list)
    assert 'generated_at' in data
    assert isinstance(data['generated_at'], str)
