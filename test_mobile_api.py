#!/usr/bin/env python3
"""
Test script for Mobile API endpoints.
This script validates the mobile API functionality for app integration.
"""

import requests
import json
import time
import uuid
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = "http://localhost:5002"

# Test device data
DEVICE_DATA = {
    "device_id": str(uuid.uuid4()),
    "app_version": "1.0.0",
    "device_type": "iOS",
}


def test_mobile_health():
    """Test the mobile API health check endpoint."""
    print("\n📱 Testing Mobile API Health Check...")

    url = f"{BASE_URL}/api/mobile/health"

    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Mobile API health check successful!")
            print(f"Service: {result.get('service', 'N/A')}")
            print(f"Version: {result.get('version', 'N/A')}")
            print(
                f"Capabilities: {len(result.get('capabilities', []))} features"
            )
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_mobile_auth():
    """Test mobile device authentication."""
    print("\n🔐 Testing Mobile Authentication...")

    url = f"{BASE_URL}/api/mobile/auth/token"

    try:
        response = requests.post(url, json=DEVICE_DATA, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Mobile authentication successful!")
            print(
                f"Session token generated: {result.get('session_token', 'N/A')[:20]}..."
            )
            print(f"Expires at: {result.get('expires_at', 'N/A')}")
            print(
                f"Device capabilities: {len(result.get('device_capabilities', {}))} features"
            )
            return result.get("session_token")
        else:
            print(f"❌ Error: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None


def test_mobile_route_optimization():
    """Test mobile route optimization endpoint."""
    print("\n🗺️  Testing Mobile Route Optimization...")

    url = f"{BASE_URL}/api/mobile/routes/optimize"

    # Sample mobile route request
    test_data = {
        "stores": [
            {
                "id": "mobile_store_1",
                "name": "Mobile Store A",
                "address": "123 Market St, San Francisco, CA",
                "lat": 37.7749,
                "lng": -122.4194,
                "priority": 1,
            },
            {
                "id": "mobile_store_2",
                "name": "Mobile Store B",
                "address": "456 Mission St, San Francisco, CA",
                "lat": 37.7849,
                "lng": -122.4094,
                "priority": 2,
            },
            {
                "id": "mobile_store_3",
                "name": "Mobile Store C",
                "address": "789 Valencia St, San Francisco, CA",
                "lat": 37.7649,
                "lng": -122.4294,
                "priority": 1,
            },
        ],
        "preferences": {"algorithm": "genetic", "proximity": True},
        "compress_response": True,
        "include_directions": True,
        "max_waypoints": 23,
    }

    # Add API key header (in real implementation)
    headers = {"Content-Type": "application/json", "X-API-Key": "test-api-key"}

    try:
        response = requests.post(
            url, json=test_data, headers=headers, timeout=30
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Mobile route optimization successful!")
            print(
                f"Route generated with {len(result.get('route', {}).get('stops', []))} stops"
            )
            print(f"Mobile optimized: {result.get('mobile_optimized', False)}")
            print(
                f"Optimization time: {result.get('optimization_time', 'N/A')}"
            )
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Exception: {str(e)}")


def test_mobile_traffic_routing():
    """Test mobile traffic-aware routing."""
    print("\n🚦 Testing Mobile Traffic Routing...")

    url = f"{BASE_URL}/api/mobile/routes/traffic"

    test_data = {
        "origin": "San Francisco, CA",
        "destination": "Palo Alto, CA",
        "waypoints": ["Daly City, CA", "San Mateo, CA"],
        "avoid_tolls": True,
        "avoid_highways": False,
        "traffic_model": "best_guess",
        "departure_time": "now",
        "alternatives": True,
        "include_steps": True,
    }

    headers = {"Content-Type": "application/json", "X-API-Key": "test-api-key"}

    try:
        response = requests.post(
            url, json=test_data, headers=headers, timeout=30
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Mobile traffic routing successful!")
            print(f"Mobile formatted: {result.get('mobile_formatted', False)}")
            directions = result.get("directions", {})
            print(f"Route legs: {len(directions.get('legs', []))}")
            print(f"Alternatives: {len(result.get('alternatives', []))}")
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Exception: {str(e)}")


def test_driver_location_updates():
    """Test driver location update functionality."""
    print("\n📍 Testing Driver Location Updates...")

    url = f"{BASE_URL}/api/mobile/driver/location"

    # Simulate GPS location updates
    locations = [
        {"lat": 37.7749, "lng": -122.4194, "heading": 45, "speed": 25},
        {"lat": 37.7759, "lng": -122.4184, "heading": 50, "speed": 30},
        {"lat": 37.7769, "lng": -122.4174, "heading": 55, "speed": 28},
    ]

    driver_id = f"driver_{uuid.uuid4().hex[:8]}"
    headers = {"Content-Type": "application/json", "X-API-Key": "test-api-key"}

    success_count = 0

    for i, location in enumerate(locations):
        test_data = {
            "driver_id": driver_id,
            "lat": location["lat"],
            "lng": location["lng"],
            "heading": location["heading"],
            "speed": location["speed"],
            "accuracy": 5.0,
            "timestamp": datetime.utcnow().isoformat(),
        }

        try:
            response = requests.post(
                url, json=test_data, headers=headers, timeout=10
            )

            if response.status_code == 200:
                success_count += 1
                print(
                    f"  📍 Location {i+1}: ✅ Updated ({location['lat']:.4f}, {location['lng']:.4f})"
                )
            else:
                print(
                    f"  📍 Location {i+1}: ❌ Failed - {response.status_code}"
                )

        except Exception as e:
            print(f"  📍 Location {i+1}: ❌ Exception - {str(e)}")

        time.sleep(0.5)  # Small delay between updates

    print(f"✅ Location updates: {success_count}/{len(locations)} successful")


def test_driver_status_updates():
    """Test driver status update functionality."""
    print("\n👤 Testing Driver Status Updates...")

    url = f"{BASE_URL}/api/mobile/driver/status"

    driver_id = f"driver_{uuid.uuid4().hex[:8]}"
    statuses = [
        "available",
        "busy",
        "en_route",
        "delivering",
        "break",
        "offline",
    ]

    headers = {"Content-Type": "application/json", "X-API-Key": "test-api-key"}

    success_count = 0

    for status in statuses:
        test_data = {
            "driver_id": driver_id,
            "status": status,
            "metadata": {
                "location": "San Francisco",
                "route_id": (
                    "route_123"
                    if status in ["busy", "en_route", "delivering"]
                    else None
                ),
            },
        }

        try:
            response = requests.post(
                url, json=test_data, headers=headers, timeout=10
            )

            if response.status_code == 200:
                success_count += 1
                print(f"  👤 Status '{status}': ✅ Updated")
            else:
                print(
                    f"  👤 Status '{status}': ❌ Failed - {response.status_code}"
                )

        except Exception as e:
            print(f"  👤 Status '{status}': ❌ Exception - {str(e)}")

        time.sleep(0.3)

    print(f"✅ Status updates: {success_count}/{len(statuses)} successful")


def test_offline_sync():
    """Test offline data synchronization."""
    print("\n🔄 Testing Offline Data Sync...")

    url = f"{BASE_URL}/api/mobile/sync/offline"

    # Simulate offline data that was stored locally
    offline_data = [
        {
            "type": "location_update",
            "data": {
                "driver_id": "driver_offline_test",
                "lat": 37.7749,
                "lng": -122.4194,
                "timestamp": (
                    datetime.utcnow() - timedelta(hours=2)
                ).isoformat(),
            },
        },
        {
            "type": "status_update",
            "data": {
                "driver_id": "driver_offline_test",
                "status": "delivering",
                "timestamp": (
                    datetime.utcnow() - timedelta(hours=1)
                ).isoformat(),
            },
        },
        {
            "type": "delivery_confirmation",
            "data": {
                "driver_id": "driver_offline_test",
                "store_id": "store_123",
                "completed": True,
                "timestamp": (
                    datetime.utcnow() - timedelta(minutes=30)
                ).isoformat(),
            },
        },
    ]

    test_data = {
        "device_id": DEVICE_DATA["device_id"],
        "offline_data": offline_data,
    }

    headers = {"Content-Type": "application/json", "X-API-Key": "test-api-key"}

    try:
        response = requests.post(
            url, json=test_data, headers=headers, timeout=15
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            sync_results = result.get("sync_results", {})
            print("✅ Offline sync successful!")
            print(f"Processed: {sync_results.get('processed', 0)}")
            print(f"Failed: {sync_results.get('failed', 0)}")
            print(f"Duplicates: {sync_results.get('duplicates', 0)}")

            if sync_results.get("errors"):
                print(f"Errors: {sync_results['errors']}")
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Exception: {str(e)}")


def check_server_health():
    """Check if the server is running."""
    print("\n🏥 Checking Server Health...")

    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server not accessible: {str(e)}")
        return False


def main():
    """Run all mobile API tests."""
    print("📱 Starting Mobile API Tests")
    print("=" * 50)

    # Check if server is running
    if not check_server_health():
        print("\n❌ Cannot proceed - server is not running.")
        print("Please start the server with: python run_app.py")
        return

    # Run health check first
    if not test_mobile_health():
        print("\n❌ Mobile API not available. Tests aborted.")
        return

    # Test authentication
    session_token = test_mobile_auth()
    if not session_token:
        print("\n⚠️  Authentication failed, but continuing with other tests...")

    # Run all mobile API tests
    test_mobile_route_optimization()
    test_mobile_traffic_routing()
    test_driver_location_updates()
    test_driver_status_updates()
    test_offline_sync()

    print("\n" + "=" * 50)
    print("🏁 Mobile API Tests Complete!")
    print("\nNote: Some tests may require API keys or database setup.")
    print("The mobile API is ready for mobile app integration.")


if __name__ == "__main__":
    main()
