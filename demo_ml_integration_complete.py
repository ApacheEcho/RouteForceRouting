#!/usr/bin/env python3
"""
Demo ML Integration - Complete System Test
Tests the complete ML integration with actual API calls
"""

import sys
import os
import json
import time
import requests
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_ml_api_direct():
    """Test ML API endpoints directly"""
    print("=" * 60)
    print("TESTING ML API ENDPOINTS DIRECT")
    print("=" * 60)

    # Test data
    test_data = {
        "stores": [
            {
                "id": "store_1",
                "name": "Downtown Store",
                "lat": 40.7128,
                "lon": -74.0060,
                "priority": 1,
                "demand": 150,
            },
            {
                "id": "store_2",
                "name": "Uptown Store",
                "lat": 40.7580,
                "lon": -73.9855,
                "priority": 2,
                "demand": 200,
            },
            {
                "id": "store_3",
                "name": "Brooklyn Store",
                "lat": 40.6782,
                "lon": -73.9442,
                "priority": 1,
                "demand": 100,
            },
            {
                "id": "store_4",
                "name": "Queens Store",
                "lat": 40.7282,
                "lon": -73.7949,
                "priority": 3,
                "demand": 120,
            },
            {
                "id": "store_5",
                "name": "Bronx Store",
                "lat": 40.8448,
                "lon": -73.8648,
                "priority": 2,
                "demand": 180,
            },
        ],
        "context": {
            "weather_factor": 1.0,
            "traffic_factor": 1.2,
            "timestamp": datetime.now().isoformat(),
        },
    }

    base_url = "http://localhost:5001/api/v1"

    try:
        # Test API health
        print("\n1. Testing API health...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✓ API is healthy")
            print(
                f"   Available endpoints: {len(health_data.get('endpoints', {}))}"
            )
        else:
            print(f"   ✗ API health check failed: {response.status_code}")
            return False

        # Test basic route generation
        print("\n2. Testing basic route generation...")
        response = requests.post(f"{base_url}/routes/generate", json=test_data)
        if response.status_code == 200:
            route_data = response.json()
            print(f"   ✓ Basic route generated successfully")
            print(f"   Route stops: {len(route_data.get('route', []))}")
        else:
            print(
                f"   ✗ Basic route generation failed: {response.status_code}"
            )
            return False

        # Test genetic algorithm optimization
        print("\n3. Testing genetic algorithm optimization...")
        response = requests.post(
            f"{base_url}/routes/optimize/genetic", json=test_data
        )
        if response.status_code == 200:
            genetic_data = response.json()
            print(f"   ✓ Genetic algorithm optimization successful")
            print(
                f"   Improvement: {genetic_data.get('metrics', {}).get('improvement_percent', 0):.2f}%"
            )
        else:
            print(
                f"   ✗ Genetic algorithm optimization failed: {response.status_code}"
            )

        # Test simulated annealing optimization
        print("\n4. Testing simulated annealing optimization...")
        response = requests.post(
            f"{base_url}/routes/optimize/simulated_annealing", json=test_data
        )
        if response.status_code == 200:
            sa_data = response.json()
            print(f"   ✓ Simulated annealing optimization successful")
            print(
                f"   Improvement: {sa_data.get('metrics', {}).get('improvement_percent', 0):.2f}%"
            )
        else:
            print(
                f"   ✗ Simulated annealing optimization failed: {response.status_code}"
            )

        # Test algorithm listing
        print("\n5. Testing algorithm listing...")
        response = requests.get(f"{base_url}/routes/algorithms")
        if response.status_code == 200:
            algorithms_data = response.json()
            print(f"   ✓ Algorithm listing successful")
            algorithms = algorithms_data.get("algorithms", {})
            print(f"   Available algorithms: {list(algorithms.keys())}")
        else:
            print(f"   ✗ Algorithm listing failed: {response.status_code}")

        print("\n✓ All API tests completed successfully!")
        return True

    except Exception as e:
        print(f"   ✗ Error in API tests: {str(e)}")
        return False


def demonstrate_optimization_algorithms():
    """Demonstrate different optimization algorithms"""
    print("\n" + "=" * 60)
    print("DEMONSTRATING OPTIMIZATION ALGORITHMS")
    print("=" * 60)

    # Test data
    test_data = {
        "stores": [
            {
                "id": "store_1",
                "name": "Manhattan Store",
                "lat": 40.7128,
                "lon": -74.0060,
                "priority": 1,
                "demand": 150,
            },
            {
                "id": "store_2",
                "name": "Brooklyn Store",
                "lat": 40.6782,
                "lon": -73.9442,
                "priority": 2,
                "demand": 200,
            },
            {
                "id": "store_3",
                "name": "Queens Store",
                "lat": 40.7282,
                "lon": -73.7949,
                "priority": 1,
                "demand": 100,
            },
            {
                "id": "store_4",
                "name": "Bronx Store",
                "lat": 40.8448,
                "lon": -73.8648,
                "priority": 3,
                "demand": 120,
            },
            {
                "id": "store_5",
                "name": "Staten Island Store",
                "lat": 40.5795,
                "lon": -74.1502,
                "priority": 2,
                "demand": 180,
            },
            {
                "id": "store_6",
                "name": "Harlem Store",
                "lat": 40.8176,
                "lon": -73.9782,
                "priority": 1,
                "demand": 90,
            },
            {
                "id": "store_7",
                "name": "LIC Store",
                "lat": 40.7505,
                "lon": -73.9370,
                "priority": 2,
                "demand": 140,
            },
            {
                "id": "store_8",
                "name": "Williamsburg Store",
                "lat": 40.7081,
                "lon": -73.9571,
                "priority": 1,
                "demand": 160,
            },
        ]
    }

    base_url = "http://localhost:5001/api/v1"
    algorithms = [
        {"name": "Default", "endpoint": "routes/generate"},
        {"name": "Genetic Algorithm", "endpoint": "routes/optimize/genetic"},
        {
            "name": "Simulated Annealing",
            "endpoint": "routes/optimize/simulated_annealing",
        },
    ]

    results = []

    for algorithm in algorithms:
        print(f"\n--- Testing {algorithm['name']} ---")

        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/{algorithm['endpoint']}", json=test_data
            )
            processing_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()

                # Extract metrics
                metrics = data.get("metrics", {})
                improvement = metrics.get("improvement_percent", 0)
                route_length = len(data.get("route", []))

                results.append(
                    {
                        "algorithm": algorithm["name"],
                        "improvement": improvement,
                        "processing_time": processing_time,
                        "route_length": route_length,
                        "success": True,
                    }
                )

                print(f"   ✓ Success!")
                print(f"   Processing time: {processing_time:.3f}s")
                print(f"   Route improvement: {improvement:.2f}%")
                print(f"   Route length: {route_length} stops")

            else:
                results.append(
                    {
                        "algorithm": algorithm["name"],
                        "success": False,
                        "error": response.status_code,
                    }
                )
                print(f"   ✗ Failed with status {response.status_code}")

        except Exception as e:
            results.append(
                {
                    "algorithm": algorithm["name"],
                    "success": False,
                    "error": str(e),
                }
            )
            print(f"   ✗ Error: {str(e)}")

    # Print summary
    print("\n" + "=" * 60)
    print("ALGORITHM PERFORMANCE SUMMARY")
    print("=" * 60)

    for result in results:
        if result["success"]:
            print(
                f"{result['algorithm']:<20} | {result['improvement']:>6.1f}% | {result['processing_time']:>8.3f}s | {result['route_length']:>3d} stops"
            )
        else:
            print(f"{result['algorithm']:<20} | ERROR: {result['error']}")

    return results


def main():
    """Run complete ML integration demo"""
    print("MACHINE LEARNING INTEGRATION DEMO")
    print("=" * 60)

    # Check if server is running
    try:
        response = requests.get(
            "http://localhost:5001/api/v1/health", timeout=5
        )
        if response.status_code != 200:
            print("❌ Server is not running or not responding correctly")
            print("Please start the server with: python app.py")
            return False
    except Exception as e:
        print("❌ Cannot connect to server")
        print("Please start the server with: python app.py")
        return False

    print("✓ Server is running and responding")

    start_time = time.time()

    # Run tests
    success = True

    if not test_ml_api_direct():
        success = False

    results = demonstrate_optimization_algorithms()

    # Check if at least one algorithm worked
    if not any(r["success"] for r in results):
        success = False

    # Print final summary
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print("FINAL DEMO SUMMARY")
    print("=" * 60)
    print(f"Total time: {total_time:.2f} seconds")

    if success:
        print("\n🎉 ML Integration Demo completed successfully!")
        print("✓ API endpoints are working")
        print("✓ Optimization algorithms are functional")
        print("✓ Route generation is working")

        # Show best performing algorithm
        successful_results = [r for r in results if r["success"]]
        if successful_results:
            best_algorithm = max(
                successful_results, key=lambda x: x["improvement"]
            )
            print(
                f"✓ Best performing algorithm: {best_algorithm['algorithm']} ({best_algorithm['improvement']:.1f}% improvement)"
            )
    else:
        print("\n⚠️  Some issues detected in ML integration")
        print("Check the output above for details")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
