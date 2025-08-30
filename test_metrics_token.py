"""
Tests for optional METRICS_TOKEN protection on /metrics endpoints.
"""

import os
import pytest
from app import create_app


@pytest.fixture
def client_no_token(monkeypatch):
    """Flask test client with no METRICS_TOKEN configured"""
    monkeypatch.delenv("METRICS_TOKEN", raising=False)
    app = create_app("testing")
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def client_with_token(monkeypatch):
    """Flask test client with METRICS_TOKEN configured"""
    monkeypatch.setenv("METRICS_TOKEN", "secret-token")
    app = create_app("testing")
    app.config["TESTING"] = True
    return app.test_client()


def test_metrics_public_when_no_token(client_no_token):
    # /metrics should be accessible and return text/plain content
    r = client_no_token.get("/metrics")
    assert r.status_code == 200
    assert r.mimetype.startswith("text/plain") or r.mimetype == "text/plain"

    # /metrics/health should be accessible and JSON
    r = client_no_token.get("/metrics/health")
    assert r.status_code == 200
    assert r.is_json


def test_metrics_protected_with_token_header(client_with_token):
    # Without token -> 401
    r = client_with_token.get("/metrics")
    assert r.status_code == 401

    # With correct header -> 200
    r = client_with_token.get("/metrics", headers={"X-Metrics-Token": "secret-token"})
    assert r.status_code == 200

    # With query param -> 200
    r = client_with_token.get("/metrics?token=secret-token")
    assert r.status_code == 200

    # /metrics/health is exempt -> 200 regardless
    r = client_with_token.get("/metrics/health")
    assert r.status_code == 200
    assert r.is_json

