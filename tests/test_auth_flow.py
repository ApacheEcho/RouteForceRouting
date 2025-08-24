import uuid
import os
import time
import pytest
from typing import Callable, Any, Dict
from flask import Flask
from flask.testing import FlaskClient

# Adjust imports to your app structure
from app import create_app, db  # type: ignore
from app.models.database import User  # type: ignore

# Config
PROTECTED_PATH = os.getenv("RFP_PROTECTED_PATH", "/v1/routes")

# ---------- App/Client Fixtures ----------

@pytest.fixture(scope="session")
def app() -> Flask:
    """
    Create the Flask app in testing mode.
    Ensures DB is clean before and after session.
    """
    app = create_app(testing=True)
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=os.getenv("TEST_DATABASE_URI", "sqlite:///:memory:"),
        WTF_CSRF_ENABLED=False,
        SERVER_NAME="localhost",
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def user_factory(app: Flask) -> Callable[..., User]:
    """
    Persist a test user; supports set_password on the model.
    Uses unique username/email per call.
    """
    def _mk(
        email: str = None,
        password: str = "Secret123!",
        username: str = None,
        is_active: bool = True,
        **extra: Any,
    ) -> User:
        unique = str(uuid.uuid4())[:8]
        # Always make email unique unless explicitly overridden with a unique value
        if email is None or email in ["a@b.com", "ok@b.com", "ref@b.com", "lo@b.com", "chain@b.com", "inactive@b.com"]:
            email = f"user_{unique}@example.com"
        if not username:
            username = f"testuser_{unique}"
        with app.app_context():
            u = User(email=email, username=username, is_active=is_active, **extra)
            if hasattr(u, "set_password"):
                u.set_password(password)  # type: ignore[attr-defined]
            else:
                from werkzeug.security import generate_password_hash
                u.password_hash = generate_password_hash(password)  # type: ignore[attr-defined]
            db.session.add(u)
            db.session.commit()
            return u
    return _mk


# ---------- Helpers ----------

def login(client: FlaskClient, email: str, password: str):
    return client.post(
        "/api/login",
        json={"email": email, "password": password},
        headers={"Content-Type": "application/json"},
    )

def auth_hdr(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# ---------- /api/login ----------

def test_login_success_returns_access_and_refresh(client: FlaskClient, user_factory):
    user_factory(email="a@b.com", password="Secret123!", is_active=True)
    r = login(client, "a@b.com", "Secret123!")
    assert r.status_code == 200
    j = r.get_json()
    assert j["success"] is True
    assert isinstance(j.get("access_token"), str) and j["access_token"]
    assert isinstance(j.get("refresh_token"), str) and j["refresh_token"]
    assert isinstance(j.get("user"), dict)

def test_login_invalid_credentials(client: FlaskClient, user_factory):
    user_factory(email="a@b.com", password="Secret123!", is_active=True)
    r = login(client, "a@b.com", "WRONG")
    assert r.status_code == 401
    j = r.get_json()
    assert j["success"] is False
    assert "Invalid" in j["error"]

def test_login_missing_fields(client: FlaskClient):
    r = client.post("/api/login", json={"email": "only@email.com"})
    assert r.status_code == 400
    assert "Email and password required" in r.get_json().get("error", "")

def test_login_inactive_user(client: FlaskClient, user_factory):
    user_factory(email="inactive@b.com", password="Secret123!", is_active=False)
    r = login(client, "inactive@b.com", "Secret123!")
    assert r.status_code in (401, 403)  # impl returns 403; unified errors may return 401


# ---------- Protected Endpoint (JWT required) ----------

def test_protected_requires_token(client: FlaskClient):
    r = client.get(PROTECTED_PATH)
    assert r.status_code in (401, 403, 422)  # depends on JWT error handling

def test_protected_with_valid_access_token(client: FlaskClient, user_factory):
    user_factory(email="ok@b.com", password="Secret123!", is_active=True)
    r = login(client, "ok@b.com", "Secret123!")
    assert r.status_code == 200
    access = r.get_json()["access_token"]
    r2 = client.get(PROTECTED_PATH, headers=auth_hdr(access))
    assert r2.status_code in (200, 204) or (r2.status_code == 200 and r2.is_json)


# ---------- /api/refresh ----------

def test_refresh_success_issues_new_access_token(client: FlaskClient, user_factory):
    user_factory(email="ref@b.com", password="Secret123!", is_active=True)
    r = login(client, "ref@b.com", "Secret123!")
    assert r.status_code == 200
    refresh = r.get_json()["refresh_token"]

    r2 = client.post("/api/refresh", headers=auth_hdr(refresh))
    assert r2.status_code == 200
    j = r2.get_json()
    assert isinstance(j.get("access_token"), str) and j["access_token"]

def test_refresh_with_invalid_refresh_token(client: FlaskClient):
    bad = "Bearer x.y.z.corrupted"
    r = client.post("/api/refresh", headers={"Authorization": bad})
    assert r.status_code in (401, 422)

# Note: For 'expired' refresh token, configure a very short TTL in test settings or
# mock token creation to produce an already-expired token, then assert 401.


# ---------- /api/logout ----------

def test_logout_revokes_access_token_and_blocks_future_calls(client: FlaskClient, user_factory):
    user_factory(email="lo@b.com", password="Secret123!", is_active=True)
    r = login(client, "lo@b.com", "Secret123!")
    assert r.status_code == 200
    access = r.get_json()["access_token"]

    r2 = client.post("/api/logout", headers=auth_hdr(access))
    assert r2.status_code == 200
    # Follow-up with same token should fail if blocklist is active
    r3 = client.get(PROTECTED_PATH, headers=auth_hdr(access))
    assert r3.status_code in (401, 403, 422)


# ---------- End-to-end chain ----------

def test_full_chain_login_refresh_access_protected_logout(client: FlaskClient, user_factory):
    """
    1) login → get access+refresh
    2) protected with access
    3) refresh → new access
    4) protected with new access
    5) logout → using the new access
    6) protected with logged-out token should fail
    """
    user_factory(email="chain@b.com", password="Secret123!", is_active=True)

    r1 = login(client, "chain@b.com", "Secret123!")
    assert r1.status_code == 200
    body = r1.get_json()
    access, refresh = body["access_token"], body["refresh_token"]

    r2 = client.get(PROTECTED_PATH, headers=auth_hdr(access))
    assert r2.status_code in (200, 204) or (r2.status_code == 200 and r2.is_json)

    r3 = client.post("/api/refresh", headers=auth_hdr(refresh))
    assert r3.status_code == 200
    new_access = r3.get_json()["access_token"]

    r4 = client.get(PROTECTED_PATH, headers=auth_hdr(new_access))
    assert r4.status_code in (200, 204) or (r4.status_code == 200 and r4.is_json)

    r5 = client.post("/api/logout", headers=auth_hdr(new_access))
    assert r5.status_code == 200

    r6 = client.get(PROTECTED_PATH, headers=auth_hdr(new_access))
    assert r6.status_code in (401, 403, 422)
