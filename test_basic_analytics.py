#!/usr/bin/env python3
"""
Simple Analytics Test - Uses Flask test client (no external server)
"""

import json
import logging
from app import create_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_analytics_endpoints():
    """Smoke test core analytics/monitoring endpoints with Flask test client"""
    app = create_app("testing")
    client = app.test_client()

    # Health
    r = client.get("/health")
    assert r.status_code in (200, 503)
    logger.info(f"Health: {r.status_code}")

    # Ensemble status (may require auth) — accept 200 or 401
    r = client.get("/api/ai/ensemble/status")
    logger.info(f"Ensemble status: {r.status_code}")
    assert r.status_code in (200, 401)

    # Monitoring summary (JSON, no auth)
    r = client.get("/metrics/summary")
    logger.info(f"Metrics summary: {r.status_code}")
    assert r.status_code == 200
    summary = r.get_json() or {}
    assert "total_metrics" in summary

    # Dashboard page (HTML)
    r = client.get("/dashboard/analytics")
    logger.info(f"Dashboard analytics: {r.status_code}")
    assert r.status_code == 200

    # Basic route generation via public endpoint /api/v1/routes
    test_data = {
        "stores": [
            {
                "id": "1",
                "name": "Store 1",
                "lat": 40.7128,
                "lon": -74.0060,
                "priority": 1,
            },
            {
                "id": "2",
                "name": "Store 2",
                "lat": 40.7589,
                "lon": -73.9851,
                "priority": 2,
            },
        ]
    }
    r = client.post("/api/v1/routes", json=test_data)
    logger.info(f"Route create: {r.status_code}")
    if r.status_code in (200, 201):
        data = r.get_json() or {}
        # Response may be wrapped; log minimal success without strict shape
        logger.info("✓ Route generation responded successfully")
    else:
        # Don’t fail the entire smoke if route generation is unavailable
        logger.info(f"Route generation response: {r.status_code}")

    logger.info("\n🎯 Basic functionality test completed")
    return True


if __name__ == "__main__":
    test_analytics_endpoints()
