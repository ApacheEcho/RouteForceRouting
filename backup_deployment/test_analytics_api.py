#!/usr/bin/env python3
"""
Test script for Analytics API endpoints.
This script validates the analytics functionality for business intelligence and monitoring.
"""

import requests
import json
import time
import uuid
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = "http://localhost:5002"

# Test API key
API_KEY = "test-api-key"


def test_analytics_health():
    """Test the analytics API health check endpoint."""
    print("\n📊 Testing Analytics API Health Check...")

    url = f"{BASE_URL}/api/analytics/health"

    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Analytics API health check successful!")
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


def test_track_mobile_session():
    """Test mobile session tracking."""
    print("\n📱 Testing Mobile Session Tracking...")

    url = f"{BASE_URL}/api/analytics/track/session"
    headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}

    test_data = {
        "device_id": str(uuid.uuid4()),
        "app_version": "1.0.0",
        "device_type": "iOS",
        "features_used": ["route_optimization", "traffic_routing"],
        "api_calls": 5,
    }

    try:
        response = requests.post(
            url, json=test_data, headers=headers, timeout=10
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Mobile session tracking successful!")
            print(f"Message: {result.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_track_driver_performance():
    """Test driver performance tracking."""
    print("\n🚗 Testing Driver Performance Tracking...")

    url = f"{BASE_URL}/api/analytics/track/driver"
    headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}

    test_data = {
        "driver_id": "driver_123",
        "location_accuracy": 5.0,
        "speed": 45.5,
        "route_deviation": 0.1,
        "stops_completed": 8,
        "time_at_stop": 300,
        "fuel_efficiency": 25.5,
        "customer_rating": 4.5,
    }

    try:
        response = requests.post(
            url, json=test_data, headers=headers, timeout=10
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Driver performance tracking successful!")
            print(f"Message: {result.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_track_route_optimization():
    """Test route optimization tracking."""
    print("\n🗺️ Testing Route Optimization Tracking...")

    url = f"{BASE_URL}/api/analytics/track/route"
    headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}

    test_data = {
        "route_id": str(uuid.uuid4()),
        "algorithm": "genetic",
        "stores": [
            {
                "id": "store_1",
                "name": "Store A",
                "lat": 37.7749,
                "lng": -122.4194,
            },
            {
                "id": "store_2",
                "name": "Store B",
                "lat": 37.7849,
                "lng": -122.4094,
            },
            {
                "id": "store_3",
                "name": "Store C",
                "lat": 37.7649,
                "lng": -122.4294,
            },
        ],
        "optimization_time": 2.5,
        "total_distance": 15.2,
        "total_time": 45,
        "improvement_percentage": 18.5,
        "success": True,
        "traffic_aware": False,
    }

    try:
        response = requests.post(
            url, json=test_data, headers=headers, timeout=10
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Route optimization tracking successful!")
            print(f"Message: {result.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_track_system_event():
    """Test system event tracking."""
    print("\n⚡ Testing System Event Tracking...")

    url = f"{BASE_URL}/api/analytics/track/event"
    headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}

    test_data = {
        "event_type": "api_performance_alert",
        "event_data": {
            "endpoint": "/api/mobile/routes/optimize",
            "response_time": 3.2,
            "severity": "warning",
            "threshold": 2.0,
        },
    }

    try:
        response = requests.post(
            url, json=test_data, headers=headers, timeout=10
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ System event tracking successful!")
            print(f"Message: {result.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_get_mobile_analytics():
    """Test getting mobile analytics."""
    print("\n📊 Testing Mobile Analytics Retrieval...")

    url = f"{BASE_URL}/api/analytics/mobile"
    headers = {"X-API-Key": API_KEY}
    params = {"timeframe": "24h"}

    try:
        response = requests.get(
            url, headers=headers, params=params, timeout=10
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Mobile analytics retrieval successful!")
            data = result.get("data", {})
            print(f"Total sessions: {data.get('total_sessions', 0)}")
            print(f"Unique devices: {data.get('unique_devices', 0)}")
            print(f"API calls: {data.get('total_api_calls', 0)}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_get_driver_analytics():
    """Test getting driver analytics."""
    print("\n🚗 Testing Driver Analytics Retrieval...")

    url = f"{BASE_URL}/api/analytics/drivers"
    headers = {"X-API-Key": API_KEY}
    params = {"timeframe": "24h"}

    try:
        response = requests.get(
            url, headers=headers, params=params, timeout=10
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Driver analytics retrieval successful!")
            data = result.get("data", {})
            print(f"Total drivers: {data.get('total_drivers', 0)}")
            print(f"Location updates: {data.get('total_location_updates', 0)}")
            print(f"Avg rating: {data.get('avg_customer_rating', 0)}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_get_route_analytics():
    """Test getting route analytics."""
    print("\n🗺️ Testing Route Analytics Retrieval...")

    url = f"{BASE_URL}/api/analytics/routes"
    headers = {"X-API-Key": API_KEY}
    params = {"timeframe": "24h"}

    try:
        response = requests.get(
            url, headers=headers, params=params, timeout=10
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Route analytics retrieval successful!")
            data = result.get("data", {})
            print(f"Total routes: {data.get('total_routes', 0)}")
            print(f"Success rate: {data.get('success_rate', 0)}%")
            print(
                f"Avg optimization time: {data.get('avg_optimization_time', 0)}s"
            )
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_get_api_analytics():
    """Test getting API analytics."""
    print("\n🔗 Testing API Analytics Retrieval...")

    url = f"{BASE_URL}/api/analytics/api-usage"
    headers = {"X-API-Key": API_KEY}
    params = {"timeframe": "24h"}

    try:
        response = requests.get(
            url, headers=headers, params=params, timeout=10
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ API analytics retrieval successful!")
            data = result.get("data", {})
            print(f"Total requests: {data.get('total_requests', 0)}")
            print(f"Mobile requests: {data.get('mobile_requests', 0)}")
            print(f"Error rate: {data.get('error_rate', 0)}%")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_get_system_health():
    """Test getting system health."""
    print("\n⚡ Testing System Health Retrieval...")

    url = f"{BASE_URL}/api/analytics/system-health"
    headers = {"X-API-Key": API_KEY}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ System health retrieval successful!")
            data = result.get("data", {})
            print(f"Health score: {data.get('health_score', 0)}")
            print(f"Status: {data.get('status', 'unknown')}")
            print(f"Uptime: {data.get('uptime', 'unknown')}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_get_analytics_report():
    """Test getting comprehensive analytics report."""
    print("\n📈 Testing Analytics Report Generation...")

    url = f"{BASE_URL}/api/analytics/report"
    headers = {"X-API-Key": API_KEY}
    params = {"timeframe": "24h"}

    try:
        response = requests.get(
            url, headers=headers, params=params, timeout=15
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Analytics report generation successful!")
            data = result.get("data", {})
            print(f"Report ID: {data.get('report_id', 'N/A')}")
            print(f"Timeframe: {data.get('timeframe', 'N/A')}")

            # Check all sections
            sections = [
                "mobile_analytics",
                "driver_analytics",
                "route_analytics",
                "api_analytics",
                "system_health",
            ]
            for section in sections:
                if section in data:
                    print(f"✓ {section.replace('_', ' ').title()} included")

            return True
        else:
            print(f"❌ Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def check_server_health():
    """Check if the server is running."""
    print("\n🔍 Checking Server Health...")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Server is running and healthy")
            return True
        else:
            print(f"⚠️ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running or not accessible")
        print("   Please start the server with: python run_app.py")
        return False
    except Exception as e:
        print(f"❌ Server health check failed: {str(e)}")
        return False


def main():
    """Run all analytics API tests."""
    print("=" * 70)
    print("🧪 ANALYTICS API COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    # Check server health first
    if not check_server_health():
        print("\n❌ Server not available. Please start the server first.")
        return

    # Track overall test results
    test_results = []

    # Test tracking endpoints first (to generate data)
    test_results.append(("Track Mobile Session", test_track_mobile_session()))
    test_results.append(
        ("Track Driver Performance", test_track_driver_performance())
    )
    test_results.append(
        ("Track Route Optimization", test_track_route_optimization())
    )
    test_results.append(("Track System Event", test_track_system_event()))

    # Give a moment for data to be processed
    time.sleep(1)

    # Test analytics retrieval endpoints
    test_results.append(("Analytics Health Check", test_analytics_health()))
    test_results.append(("Get Mobile Analytics", test_get_mobile_analytics()))
    test_results.append(("Get Driver Analytics", test_get_driver_analytics()))
    test_results.append(("Get Route Analytics", test_get_route_analytics()))
    test_results.append(("Get API Analytics", test_get_api_analytics()))
    test_results.append(("Get System Health", test_get_system_health()))
    test_results.append(("Get Analytics Report", test_get_analytics_report()))

    # Print summary
    print("\n" + "=" * 70)
    print("📊 ANALYTICS API TEST SUMMARY")
    print("=" * 70)

    passed = 0
    failed = 0

    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\nTotal Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(test_results)*100):.1f}%")

    if failed == 0:
        print(
            "\n🎉 All analytics API tests passed! Analytics system is fully functional."
        )
    else:
        print(
            f"\n⚠️ {failed} test(s) failed. Please check the error messages above."
        )

    print("\n📋 Next Steps:")
    print("- Integrate analytics into dashboard frontend")
    print("- Set up real-time analytics monitoring")
    print("- Configure production analytics database")
    print("- Add custom analytics dashboards")


if __name__ == "__main__":
    main()
