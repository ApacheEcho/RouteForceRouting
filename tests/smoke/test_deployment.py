import os
import pytest

from flask import Flask


def test_health_includes_request_id(monkeypatch):
    # Import create_app from app package
    from app.__init__ import create_app

    app = create_app("testing")
    client = app.test_client()

    resp = client.get("/health")
    assert resp.status_code in (200, 503)
    # header should be present even on error
    assert "X-Request-ID" in resp.headers

    data = resp.get_json()
    assert isinstance(data, dict)
    assert "status" in data
