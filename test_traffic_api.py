#!/usr/bin/env python3
"""
Test script for traffic-aware routing API endpoints.
This script validates the new traffic API functionality.
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = "http://localhost:5003"


def test_traffic_optimization():
    """Test the traffic optimization endpoint."""
    print("\n🚗 Testing Traffic Optimization Endpoint...")

    url = f"{BASE_URL}/api/traffic/optimize"

    # Test data with sample stores
    test_data = {
        "stores": [
            {
                "id": "store_1",
                "address": "1600 Amphitheatre Parkway, Mountain View, CA",
            },
            {"id": "store_2", "address": "1 Hacker Way, Menlo Park, CA"},
            {"id": "store_3", "address": "410 Terry Ave N, Seattle, WA"},
        ],
        "starting_location": "San Francisco, CA",
        "vehicle_capacity": 1000,
        "time_windows": {"start_time": "09:00", "end_time": "17:00"},
        "traffic_model": "pessimistic",
    }

    try:
        response = requests.post(url, json=test_data, timeout=30)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Traffic optimization successful!")
            print(f"Route found with {len(result.get('route', []))} stops")
            print(f"Total distance: {result.get('total_distance', 'N/A')}")
            print(f"Total time: {result.get('total_time', 'N/A')}")
            if result.get("traffic_info"):
                print(
                    f"Traffic conditions: {result['traffic_info'].get('conditions', 'N/A')}"
                )
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Exception: {str(e)}")


def test_traffic_alternatives():
    """Test the traffic alternatives endpoint."""
    print("\n🛤️  Testing Traffic Alternatives Endpoint...")

    url = f"{BASE_URL}/api/traffic/alternatives"

    test_data = {
        "origin": "San Francisco, CA",
        "destination": "San Jose, CA",
        "departure_time": "now",
    }

    try:
        response = requests.post(url, json=test_data, timeout=30)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Traffic alternatives successful!")
            print(
                f"Found {len(result.get('alternatives', []))} alternative routes"
            )
            for i, alt in enumerate(
                result.get("alternatives", [])[:3]
            ):  # Show first 3
                print(
                    f"  Route {i+1}: {alt.get('summary', 'N/A')} - {alt.get('duration', 'N/A')}"
                )
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Exception: {str(e)}")


def test_traffic_prediction():
    """Test the traffic prediction endpoint."""
    print("\n🔮 Testing Traffic Prediction Endpoint...")

    url = f"{BASE_URL}/api/traffic/predict"

    # Predict traffic for 2 hours from now
    future_time = datetime.now() + timedelta(hours=2)

    test_data = {
        "origin": "Downtown San Francisco, CA",
        "destination": "Palo Alto, CA",
        "departure_time": future_time.isoformat(),
    }

    try:
        response = requests.post(url, json=test_data, timeout=30)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Traffic prediction successful!")
            print(
                f"Predicted duration: {result.get('predicted_duration', 'N/A')}"
            )
            print(
                f"Traffic conditions: {result.get('traffic_conditions', 'N/A')}"
            )
            print(f"Confidence: {result.get('confidence', 'N/A')}")
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Exception: {str(e)}")


def test_traffic_status():
    """Test the traffic service status endpoint."""
    print("\n📊 Testing Traffic Service Status...")

    url = f"{BASE_URL}/api/traffic/status"

    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Traffic service status retrieved!")
            print(f"Service status: {result.get('status', 'N/A')}")
            print(f"API quota used: {result.get('api_quota_used', 'N/A')}")
            print(f"Cache size: {result.get('cache_size', 'N/A')}")
            print(f"Last updated: {result.get('last_updated', 'N/A')}")
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Exception: {str(e)}")


def test_segment_traffic():
    """Test the segment traffic endpoint."""
    print("\n🛣️  Testing Segment Traffic Endpoint...")

    url = f"{BASE_URL}/api/traffic/segment"

    test_data = {
        "origin": "Golden Gate Bridge, San Francisco, CA",
        "destination": "Bay Bridge, San Francisco, CA",
    }

    try:
        response = requests.post(url, json=test_data, timeout=20)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Segment traffic info retrieved!")
            print(
                f"Duration in traffic: {result.get('duration_in_traffic', 'N/A')}"
            )
            print(f"Normal duration: {result.get('normal_duration', 'N/A')}")
            print(f"Traffic severity: {result.get('traffic_severity', 'N/A')}")
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
    """Run all traffic API tests."""
    print("🚀 Starting Traffic API Tests")
    print("=" * 50)

    # Check if server is running
    if not check_server_health():
        print("\n❌ Cannot proceed - server is not running.")
        print("Please start the server with: python main.py")
        return

    # Run all tests
    test_traffic_status()
    test_segment_traffic()
    test_traffic_alternatives()
    test_traffic_prediction()
    test_traffic_optimization()

    print("\n" + "=" * 50)
    print("🏁 Traffic API Tests Complete!")
    print(
        "\nNote: Some tests may fail if Google Maps API key is not configured."
    )
    print("Check app/config.py for GOOGLE_MAPS_API_KEY configuration.")


if __name__ == "__main__":
    main()
