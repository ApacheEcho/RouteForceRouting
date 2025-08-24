import uuid
import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import create_app, db
from app.models.database import User
from werkzeug.security import generate_password_hash

@pytest.fixture(scope="module")
def test_client():
    app = create_app("testing")
    testing_client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    # Ensure a clean DB for each test module
    db.drop_all()
    db.create_all()

    yield testing_client

    db.session.remove()
    db.drop_all()
    ctx.pop()

@pytest.fixture(scope="function")
def new_user(test_client):
    """Setup: create a user before each test; Teardown: delete after test."""
    from app import db
    from app.models.database import User
    with test_client.application.app_context():
        user = User.query.filter_by(email="test@example.com").first()
        if not user:
            user = User(
                username="testuser",
                email="test@example.com",
                is_active=True,
            )
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()

def login(client, email, password):
    return client.post("/api/v1/login", json={"email": email, "password": password})

def test_login_success(test_client, new_user):
    response = login(test_client, "test@example.com", "password123")
    data = response.get_json()
    assert response.status_code == 200
    assert "access_token" in data

def test_login_invalid_credentials(test_client):
    response = login(test_client, "wrong@example.com", "wrongpass")
    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid credentials"

def test_login_missing_fields(test_client):
    response = test_client.post("/api/v1/login", json={"email": "test@example.com"})
    assert response.status_code == 400

def test_protected_endpoint_requires_token(test_client):
    response = test_client.get("/api/v1/routes")
    assert response.status_code == 401  # Unauthorized

def test_protected_endpoint_with_token(test_client, new_user):
    login_resp = login(test_client, "test@example.com", "password123")
    token = login_resp.get_json()["access_token"]
    response = test_client.get(
        "/api/v1/routes", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]  # 404 if no routes exist

def test_refresh_token_flow(test_client, new_user):
    login_resp = login(test_client, "test@example.com", "password123")
    refresh_token = login_resp.get_json().get("refresh_token")
    assert refresh_token

    response = test_client.post(
        "/api/v1/refresh", headers={"Authorization": f"Bearer {refresh_token}"}, json={}
    )
    assert response.status_code == 200
    assert "access_token" in response.get_json()

def test_logout_revokes_token(test_client, new_user):
    login_resp = login(test_client, "test@example.com", "password123")
    token = login_resp.get_json()["access_token"]

    response = test_client.post(
        "/api/v1/logout", headers={"Authorization": f"Bearer {token}"}, json={}
    )
    assert response.status_code == 200

    # Token should now be invalid
    protected_resp = test_client.get(
        "/api/v1/routes", headers={"Authorization": f"Bearer {token}"}
    )
    assert protected_resp.status_code == 401
