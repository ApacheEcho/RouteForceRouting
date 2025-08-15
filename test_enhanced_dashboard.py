#!/usr/bin/env python3
"""
Test Enhanced Dashboard Implementation
Validates the enhanced dashboard with algorithm comparison and analytics
"""
import requests
import json
import time
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_enhanced_dashboard():
    """Test enhanced dashboard endpoints and functionality"""
    base_url = "http://localhost:5000"

    print("🧪 RouteForce Enhanced Dashboard Test")
    print("=" * 50)

    # Test 1: Enhanced dashboard page
    print("\n1. Testing Enhanced Dashboard Page...")
    try:
        response = requests.get(f"{base_url}/dashboard")
        if response.status_code == 200:
            print("✅ Enhanced dashboard page loads successfully")
            print(f"   Status: {response.status_code}")
            print(
                f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}"
            )
        else:
            print(f"❌ Enhanced dashboard page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing enhanced dashboard: {e}")

    # Test 2: Algorithm comparison endpoint
    print("\n2. Testing Algorithm Comparison API...")
    try:
        sample_stores = [
            {
                "name": "Store A",
                "lat": 37.7749,
                "lng": -122.4194,
                "priority": 1,
            },
            {
                "name": "Store B",
                "lat": 37.7849,
                "lng": -122.4094,
                "priority": 2,
            },
            {
                "name": "Store C",
                "lat": 37.7649,
                "lng": -122.4294,
                "priority": 1,
            },
            {
                "name": "Store D",
                "lat": 37.7949,
                "lng": -122.3994,
                "priority": 3,
            },
            {
                "name": "Store E",
                "lat": 37.7549,
                "lng": -122.4394,
                "priority": 2,
            },
        ]

        response = requests.post(
            f"{base_url}/dashboard/api/algorithms/compare",
            json={"stores": sample_stores},
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ Algorithm comparison API works")
            print(f"   Algorithms tested: {len(data['results'])}")

            # Display results
            for result in data["results"]:
                status = "✅" if result["success"] else "❌"
                improvement = result.get("improvement_percent", 0)
                processing_time = result.get("processing_time", 0)
                print(
                    f"   {status} {result['algorithm']}: {improvement:.1f}% improvement, {processing_time:.3f}s"
                )
        else:
            print(f"❌ Algorithm comparison failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing algorithm comparison: {e}")

    # Test 3: Performance history endpoint
    print("\n3. Testing Performance History API...")
    try:
        response = requests.get(
            f"{base_url}/dashboard/api/performance/history"
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Performance history API works")
            print(f"   History entries: {len(data['history'])}")

            # Display sample history
            if data["history"]:
                recent = data["history"][0]
                print(f"   Recent data: {recent['date']}")
                for algo, metrics in recent.items():
                    if algo != "date" and isinstance(metrics, dict):
                        print(
                            f"     {algo}: {metrics['avg_improvement']}% improvement"
                        )
        else:
            print(f"❌ Performance history failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing performance history: {e}")

    # Test 4: Algorithm details endpoint
    print("\n4. Testing Algorithm Details API...")
    algorithms = [
        "genetic",
        "simulated_annealing",
        "multi_objective",
        "default",
    ]

    for algorithm in algorithms:
        try:
            response = requests.get(
                f"{base_url}/dashboard/api/algorithm/details/{algorithm}"
            )
            if response.status_code == 200:
                data = response.json()
                algo_info = data["algorithm"]
                print(f"✅ {algorithm} details: {algo_info['name']}")
                print(f"   Best for: {algo_info['best_for']}")
                print(
                    f"   Avg improvement: {algo_info['performance']['avg_improvement']}"
                )
            else:
                print(f"❌ {algorithm} details failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing {algorithm} details: {e}")

    # Test 5: System status endpoint
    print("\n5. Testing System Status API...")
    try:
        response = requests.get(f"{base_url}/dashboard/api/system/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ System status API works")

            stats = data["statistics"]
            performance = data["performance"]

            print(f"   Routes optimized: {stats['total_routes_optimized']}")
            print(f"   Distance saved: {stats['total_distance_saved']} km")
            print(f"   Average improvement: {stats['avg_improvement']}%")
            print(f"   CPU usage: {performance['cpu_usage']}%")
            print(f"   Memory usage: {performance['memory_usage']} MB")
            print(f"   Request rate: {performance['request_rate']} req/min")
            print(f"   Recent activities: {len(data['recent_activity'])}")
        else:
            print(f"❌ System status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing system status: {e}")

    # Test 6: Basic connectivity tests
    print("\n6. Testing Basic Connectivity...")
    endpoints = [
        "/api/v1/health",
        "/api/v1/routes",
        "/api/v1/stores",
        "/api/v1/clusters",
    ]

    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code in [
                200,
                400,
            ]:  # 400 is expected for some endpoints without data
                print(f"✅ {endpoint} is accessible")
            else:
                print(f"❌ {endpoint} returned {response.status_code}")
        except Exception as e:
            print(f"❌ Error accessing {endpoint}: {e}")

    print("\n" + "=" * 50)
    print("🎯 Enhanced Dashboard Test Complete!")
    print("\nNext steps:")
    print(
        "1. Visit http://localhost:5000/dashboard for the enhanced dashboard"
    )
    print("2. Try the algorithm comparison feature")
    print("3. Explore the analytics and system status tabs")
    print("4. Check the real-time performance monitoring")


if __name__ == "__main__":
    test_enhanced_dashboard()
