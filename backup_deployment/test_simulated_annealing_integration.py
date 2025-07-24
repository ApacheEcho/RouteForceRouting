#!/usr/bin/env python3
"""
API integration test script for Simulated Annealing algorithm
Tests the algorithm through the API endpoints
"""
import requests
import json
import time
from typing import List, Dict, Any

# API Base URL
API_BASE = "http://localhost:5002/api/v1"


def create_test_stores(num_stores: int = 10) -> List[Dict[str, Any]]:
    """Create test stores with random coordinates"""
    import random

    random.seed(42)  # For reproducible results

    stores = []
    for i in range(num_stores):
        stores.append(
            {
                "name": f"Store_{i+1}",
                "address": f"{random.randint(100, 999)} Test St #{i+1}",
                "latitude": round(
                    37.7749 + random.uniform(-0.1, 0.1), 6
                ),  # San Francisco area
                "longitude": round(-122.4194 + random.uniform(-0.1, 0.1), 6),
                "id": i + 1,
            }
        )

    return stores


def test_api_health():
    """Test API health and check for simulated annealing support"""
    print("🏥 Testing API Health and Algorithm Support")
    print("=" * 60)

    try:
        response = requests.get(f"{API_BASE}/health")

        if response.status_code == 200:
            health_data = response.json()
            print("✅ API is healthy")

            # Check for simulated annealing support
            algorithms = health_data.get("algorithms", {}).get("available", [])
            if "simulated_annealing" in algorithms:
                print("✅ Simulated Annealing algorithm is supported")

                # Check for the new endpoint
                endpoints = health_data.get("endpoints", {})
                if "optimize_simulated_annealing" in endpoints:
                    print("✅ Simulated Annealing endpoint is available")
                    return True
                else:
                    print("❌ Simulated Annealing endpoint not found")
            else:
                print("❌ Simulated Annealing algorithm not supported")
        else:
            print(f"❌ API health check failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Error checking API health: {str(e)}")

    return False


def test_algorithms_endpoint():
    """Test the algorithms endpoint for simulated annealing"""
    print("\n🔍 Testing Algorithms Endpoint")
    print("=" * 60)

    try:
        response = requests.get(f"{API_BASE}/routes/algorithms")

        if response.status_code == 200:
            algorithms_data = response.json()
            algorithms = algorithms_data.get("algorithms", {})

            if "simulated_annealing" in algorithms:
                sa_config = algorithms["simulated_annealing"]
                print("✅ Simulated Annealing algorithm found")
                print(f"   Name: {sa_config.get('name', 'Unknown')}")
                print(
                    f"   Description: {sa_config.get('description', 'No description')}"
                )

                # Check parameters
                parameters = sa_config.get("parameters", {})
                if parameters:
                    print("   Parameters:")
                    for param_name, param_info in parameters.items():
                        print(
                            f"     {param_name}: {param_info.get('description', 'No description')}"
                        )
                        print(f"       Default: {param_info.get('default', 'N/A')}")

                return True
            else:
                print("❌ Simulated Annealing algorithm not found")
        else:
            print(f"❌ Algorithms endpoint failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Error checking algorithms endpoint: {str(e)}")

    return False


def test_create_route_with_simulated_annealing():
    """Test creating a route with simulated annealing through main API"""
    print("\n🛣️  Testing Route Creation with Simulated Annealing")
    print("=" * 60)

    # Create test stores
    stores = create_test_stores(8)
    print(f"Created {len(stores)} test stores")

    # Prepare request data
    request_data = {
        "stores": stores,
        "constraints": {},
        "options": {
            "algorithm": "simulated_annealing",
            "sa_initial_temperature": 1000.0,
            "sa_final_temperature": 0.1,
            "sa_cooling_rate": 0.99,
            "sa_max_iterations": 3000,
            "sa_max_no_improvement": 500,
            "sa_acceptance_threshold": 0.001,
        },
    }

    try:
        print("Sending request to create route...")
        start_time = time.time()
        response = requests.post(f"{API_BASE}/routes", json=request_data)
        api_time = time.time() - start_time

        if response.status_code == 201:
            route_data = response.json()
            print(f"✅ Route created successfully in {api_time:.2f}s")

            # Check response structure
            if "route" in route_data and "metadata" in route_data:
                route = route_data["route"]
                metadata = route_data["metadata"]

                print(f"   Route length: {len(route)} stops")
                print(f"   Algorithm used: {metadata.get('algorithm_used', 'Unknown')}")
                print(
                    f"   Processing time: {metadata.get('processing_time', 'N/A'):.2f}s"
                )
                print(
                    f"   Optimization score: {metadata.get('optimization_score', 'N/A'):.2f}"
                )

                # Check for algorithm-specific metrics
                if "algorithm_metrics" in metadata:
                    alg_metrics = metadata["algorithm_metrics"]
                    print("   Algorithm metrics:")
                    for key, value in alg_metrics.items():
                        if key != "algorithm":
                            print(f"     {key}: {value}")

                return True
            else:
                print("❌ Invalid response structure")
        else:
            print(f"❌ Route creation failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")

    except Exception as e:
        print(f"❌ Error creating route: {str(e)}")

    return False


def test_dedicated_simulated_annealing_endpoint():
    """Test the dedicated simulated annealing optimization endpoint"""
    print("\n🔥 Testing Dedicated Simulated Annealing Endpoint")
    print("=" * 60)

    # Create test stores
    stores = create_test_stores(10)
    print(f"Created {len(stores)} test stores")

    # Prepare request data
    request_data = {
        "stores": stores,
        "constraints": {},
        "sa_config": {
            "initial_temperature": 1500.0,
            "final_temperature": 0.01,
            "cooling_rate": 0.98,
            "max_iterations": 5000,
            "max_no_improvement": 800,
            "acceptance_threshold": 0.002,
        },
    }

    try:
        print("Sending request to dedicated SA endpoint...")
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/routes/optimize/simulated_annealing", json=request_data
        )
        api_time = time.time() - start_time

        if response.status_code == 201:
            route_data = response.json()
            print(f"✅ SA optimization completed in {api_time:.2f}s")

            # Check response structure
            if "route" in route_data and "metadata" in route_data:
                route = route_data["route"]
                metadata = route_data["metadata"]

                print(f"   Route length: {len(route)} stops")
                print(f"   Algorithm used: {metadata.get('algorithm_used', 'Unknown')}")
                print(
                    f"   Processing time: {metadata.get('processing_time', 'N/A'):.2f}s"
                )
                print(
                    f"   Optimization score: {metadata.get('optimization_score', 'N/A'):.2f}"
                )

                # Check for simulated annealing specific metrics
                if "simulated_annealing_metrics" in route_data:
                    sa_metrics = route_data["simulated_annealing_metrics"]
                    print("   Simulated Annealing metrics:")
                    for key, value in sa_metrics.items():
                        if key != "algorithm":
                            print(f"     {key}: {value}")

                return True
            else:
                print("❌ Invalid response structure")
        else:
            print(f"❌ SA optimization failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")

    except Exception as e:
        print(f"❌ Error with SA endpoint: {str(e)}")

    return False


def test_simulated_annealing_performance():
    """Test simulated annealing performance with different configurations"""
    print("\n⚡ Testing Simulated Annealing Performance")
    print("=" * 60)

    # Create test stores
    stores = create_test_stores(12)
    print(f"Testing with {len(stores)} stores")

    # Test different configurations
    configurations = [
        {
            "name": "Fast",
            "config": {
                "initial_temperature": 500.0,
                "final_temperature": 1.0,
                "cooling_rate": 0.95,
                "max_iterations": 1000,
                "max_no_improvement": 200,
                "acceptance_threshold": 0.01,
            },
        },
        {
            "name": "Balanced",
            "config": {
                "initial_temperature": 1000.0,
                "final_temperature": 0.1,
                "cooling_rate": 0.99,
                "max_iterations": 5000,
                "max_no_improvement": 500,
                "acceptance_threshold": 0.001,
            },
        },
        {
            "name": "Thorough",
            "config": {
                "initial_temperature": 2000.0,
                "final_temperature": 0.01,
                "cooling_rate": 0.995,
                "max_iterations": 10000,
                "max_no_improvement": 1000,
                "acceptance_threshold": 0.0001,
            },
        },
    ]

    results = []

    for test_config in configurations:
        print(f"\nTesting {test_config['name']} configuration...")

        request_data = {
            "stores": stores,
            "constraints": {},
            "sa_config": test_config["config"],
        }

        try:
            start_time = time.time()
            response = requests.post(
                f"{API_BASE}/routes/optimize/simulated_annealing", json=request_data
            )
            api_time = time.time() - start_time

            if response.status_code == 201:
                route_data = response.json()
                metadata = route_data["metadata"]

                result = {
                    "name": test_config["name"],
                    "api_time": api_time,
                    "processing_time": metadata.get("processing_time", 0),
                    "optimization_score": metadata.get("optimization_score", 0),
                    "route_length": len(route_data["route"]),
                }
                results.append(result)

                print(
                    f"  ✅ {test_config['name']}: {api_time:.2f}s API, {result['processing_time']:.2f}s processing"
                )
                print(f"     Score: {result['optimization_score']:.2f}")

            else:
                print(
                    f"  ❌ {test_config['name']}: Failed with status {response.status_code}"
                )

        except Exception as e:
            print(f"  ❌ {test_config['name']}: Error - {str(e)}")

    # Print performance summary
    if results:
        print("\n📊 Performance Summary:")
        print("Config    | API Time | Processing | Score  | Route Length")
        print("-" * 55)
        for result in results:
            print(
                f"{result['name']:9} | {result['api_time']:8.2f} | {result['processing_time']:10.2f} | {result['optimization_score']:6.2f} | {result['route_length']:12}"
            )

    return len(results) > 0


def test_error_handling():
    """Test error handling for invalid requests"""
    print("\n🚨 Testing Error Handling")
    print("=" * 60)

    test_cases = [
        {
            "name": "No stores",
            "data": {"stores": [], "constraints": {}, "sa_config": {}},
            "expected_error": "No stores provided",
        },
        {
            "name": "Invalid JSON",
            "data": None,
            "expected_error": "No JSON data provided",
        },
        {
            "name": "Single store",
            "data": {
                "stores": [
                    {"name": "Store1", "latitude": 37.7749, "longitude": -122.4194}
                ],
                "constraints": {},
                "sa_config": {},
            },
            "expected_error": "At least 2 stores required",
        },
    ]

    passed_tests = 0

    for test_case in test_cases:
        print(f"\nTesting {test_case['name']}...")

        try:
            response = requests.post(
                f"{API_BASE}/routes/optimize/simulated_annealing",
                json=test_case["data"],
            )

            if response.status_code == 400:
                error_data = response.json()
                if "error" in error_data:
                    print(f"  ✅ Correctly returned error: {error_data['error']}")
                    passed_tests += 1
                else:
                    print(f"  ❌ Missing error message in response")
            else:
                print(f"  ❌ Expected 400 error, got {response.status_code}")

        except Exception as e:
            print(f"  ❌ Error during test: {str(e)}")

    print(f"\nError handling: {passed_tests}/{len(test_cases)} tests passed")
    return passed_tests == len(test_cases)


def main():
    """Run all Simulated Annealing API tests"""
    print("🚀 RouteForce Simulated Annealing - API Integration Testing")
    print("=" * 70)

    # Check if API is running
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not running or not healthy")
            print("Please start the Flask application first: python app.py")
            return False
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API")
        print("Please start the Flask application first: python app.py")
        return False

    # Track test results
    test_results = []

    # Run tests
    test_results.append(("API Health Check", test_api_health()))
    test_results.append(("Algorithms Endpoint", test_algorithms_endpoint()))
    test_results.append(
        ("Route Creation with SA", test_create_route_with_simulated_annealing())
    )
    test_results.append(
        ("Dedicated SA Endpoint", test_dedicated_simulated_annealing_endpoint())
    )
    test_results.append(("Performance Testing", test_simulated_annealing_performance()))
    test_results.append(("Error Handling", test_error_handling()))

    # Print summary
    print("\n" + "=" * 70)
    print("🎯 Test Results Summary")
    print("=" * 70)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:30} | {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All Simulated Annealing API tests passed successfully!")
        return True
    else:
        print("⚠️  Some tests failed. Please check the API implementation.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
