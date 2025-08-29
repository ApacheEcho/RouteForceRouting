#!/usr/bin/env python3
"""
Local smoke test for Mobile API endpoints using Flask test client.
Avoids binding to a TCP port (disallowed in this environment).
"""

import json
from datetime import datetime

from app import create_app


def pretty(title: str):
    print("\n" + title)
    print("=" * len(title))


def main():
    app = create_app("development")
    client = app.test_client()

    # Health
    pretty("Mobile API Health")
    r = client.get("/api/mobile/health")
    print(r.status_code, r.json)

    # Auth token
    pretty("Mobile Auth Token")
    r = client.post(
        "/api/mobile/auth/token",
        json={"device_id": "dev-123", "app_version": "1.0.0", "device_type": "iOS"},
    )
    print(r.status_code, r.json)

    # Route optimize
    pretty("Mobile Route Optimize")
    route_req = {
        "stores": [
            {
                "id": "s1",
                "name": "Store A",
                "address": "1600 Amphitheatre Parkway, Mountain View, CA",
                "lat": 37.4221,
                "lng": -122.0841,
                "priority": 1,
            },
            {
                "id": "s2",
                "name": "Store B",
                "address": "1 Apple Park Way, Cupertino, CA",
                "lat": 37.3349,
                "lng": -122.0090,
                "priority": 2,
            },
        ],
        "preferences": {"algorithm": "genetic", "proximity": True},
        "compress_response": True,
        "include_directions": False,
        "max_waypoints": 23,
    }
    r = client.post(
        "/api/mobile/routes/optimize",
        json=route_req,
        headers={"X-API-Key": "test-api-key"},
    )
    print(r.status_code)
    if r.is_json:
        data = r.get_json()
        stops = len((data or {}).get("route", {}).get("stops", []))
        print(f"stops={stops} mobile_optimized={(data or {}).get('mobile_optimized')}")
    else:
        print(r.data[:200])

    # Traffic route (accepts address strings)
    pretty("Mobile Traffic Route")
    r = client.post(
        "/api/mobile/routes/traffic",
        json={
            "origin": "San Francisco, CA",
            "destination": "Palo Alto, CA",
            "alternatives": False,
            "include_steps": False,
        },
        headers={"X-API-Key": "test-api-key"},
    )
    print(r.status_code)
    if r.is_json:
        resp = r.get_json()
        print({k: type(v).__name__ for k, v in resp.items()})
    else:
        print(r.data[:200])

    # Driver location update
    pretty("Driver Location Update")
    r = client.post(
        "/api/mobile/driver/location",
        json={
            "driver_id": "driver_smoke",
            "lat": 37.7749,
            "lng": -122.4194,
            "timestamp": datetime.utcnow().isoformat(),
        },
        headers={"X-API-Key": "test-api-key"},
    )
    print(r.status_code, r.json)

    # Driver status update
    pretty("Driver Status Update")
    r = client.post(
        "/api/mobile/driver/status",
        json={"driver_id": "driver_smoke", "status": "available"},
        headers={"X-API-Key": "test-api-key"},
    )
    print(r.status_code, r.json)


if __name__ == "__main__":
    main()

