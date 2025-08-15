#!/usr/bin/env python3
"""
Test Multi-Objective Optimization - API Integration
Tests the multi-objective optimizer through the API
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
import time


def test_multi_objective_api():
    """Test multi-objective optimization through API"""
    print("=== Testing Multi-Objective Optimization - API Integration ===")

    base_url = "http://localhost:5001/api/v1"

    # Test stores with various attributes
    stores = [
        {
            "id": 1,
            "name": "Store A",
            "lat": 40.7128,
            "lon": -74.0060,
            "priority": 1,
            "demand": 50,
        },
        {
            "id": 2,
            "name": "Store B",
            "lat": 40.7589,
            "lon": -73.9851,
            "priority": 2,
            "demand": 30,
        },
        {
            "id": 3,
            "name": "Store C",
            "lat": 40.7282,
            "lon": -73.7949,
            "priority": 3,
            "demand": 40,
        },
        {
            "id": 4,
            "name": "Store D",
            "lat": 40.6782,
            "lon": -73.9442,
            "priority": 1,
            "demand": 60,
        },
        {
            "id": 5,
            "name": "Store E",
            "lat": 40.7505,
            "lon": -73.9934,
            "priority": 2,
            "demand": 25,
        },
        {
            "id": 6,
            "name": "Store F",
            "lat": 40.7831,
            "lon": -73.9712,
            "priority": 3,
            "demand": 35,
        },
        {
            "id": 7,
            "name": "Store G",
            "lat": 40.7061,
            "lon": -74.0087,
            "priority": 1,
            "demand": 45,
        },
        {
            "id": 8,
            "name": "Store H",
            "lat": 40.7614,
            "lon": -73.9776,
            "priority": 2,
            "demand": 55,
        },
    ]

    print(f"Number of stores: {len(stores)}")

    # Test different API configurations
    test_cases = [
        {
            "name": "Distance + Time (Small)",
            "payload": {
                "stores": stores,
                "constraints": {},
                "options": {
                    "algorithm": "multi_objective",
                    "mo_objectives": "distance,time",
                    "mo_population_size": 30,
                    "mo_generations": 50,
                },
            },
        },
        {
            "name": "Distance + Priority (Medium)",
            "payload": {
                "stores": stores,
                "constraints": {},
                "options": {
                    "algorithm": "multi_objective",
                    "mo_objectives": "distance,priority",
                    "mo_population_size": 50,
                    "mo_generations": 100,
                },
            },
        },
        {
            "name": "Triple Objective (Large)",
            "payload": {
                "stores": stores,
                "constraints": {},
                "options": {
                    "algorithm": "multi_objective",
                    "mo_objectives": "distance,time,priority",
                    "mo_population_size": 80,
                    "mo_generations": 150,
                },
            },
        },
    ]

    results = []

    # First, check if server is running
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code != 200:
            print(f"Server health check failed: {health_response.status_code}")
            return None
        print("Server is running ✓")
    except Exception as e:
        print(f"Cannot connect to server: {str(e)}")
        print("Please start the server with: python app.py")
        return None

    # Check if multi-objective algorithm is available
    try:
        algorithms_response = requests.get(
            f"{base_url}/routes/algorithms", timeout=10
        )
        if algorithms_response.status_code == 200:
            algorithms = algorithms_response.json()
            if "multi_objective" in algorithms["algorithms"]:
                print("Multi-objective algorithm is available ✓")
            else:
                print("Multi-objective algorithm is NOT available ✗")
                return None
        else:
            print(
                f"Failed to get algorithms: {algorithms_response.status_code}"
            )
    except Exception as e:
        print(f"Error checking algorithms: {str(e)}")

    # Run test cases
    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test Case {i+1}: {test_case['name']} ---")

        try:
            # Send request
            start_time = time.time()
            response = requests.post(
                f"{base_url}/routes", json=test_case["payload"], timeout=60
            )
            end_time = time.time()

            if response.status_code in [200, 201]:
                data = response.json()

                print(f"✓ Request successful ({response.status_code})")
                print(
                    f"API response time: {end_time - start_time:.4f} seconds"
                )
                print(f"Route generated with {len(data['route'])} stores")

                # Display metadata
                metadata = data.get("metadata", {})
                print(
                    f"Processing time: {metadata.get('processing_time', 'N/A'):.4f}s"
                )
                print(
                    f"Algorithm used: {metadata.get('algorithm_used', 'N/A')}"
                )
                print(
                    f"Optimization score: {metadata.get('optimization_score', 'N/A')}"
                )

                # Display algorithm metrics
                if "algorithm_metrics" in metadata:
                    metrics = metadata["algorithm_metrics"]
                    print(
                        f"Pareto front size: {metrics.get('pareto_front_size', 'N/A')}"
                    )
                    print(
                        f"Total generations: {metrics.get('total_generations', 'N/A')}"
                    )
                    print(f"Hypervolume: {metrics.get('hypervolume', 'N/A')}")

                    if "best_compromise_solution" in metrics:
                        print("Best compromise objectives:")
                        for obj, value in metrics["best_compromise_solution"][
                            "objectives"
                        ].items():
                            print(f"  {obj}: {value:.4f}")

                # Display route
                print(f"\nOptimized route:")
                for j, store in enumerate(
                    data["route"][:5]
                ):  # Show first 5 stores
                    print(
                        f"  {j+1}. {store['name']} (Priority: {store.get('priority', 'N/A')})"
                    )
                if len(data["route"]) > 5:
                    print(f"  ... and {len(data['route']) - 5} more stores")

                results.append(
                    {
                        "test_case": test_case["name"],
                        "success": True,
                        "status_code": response.status_code,
                        "api_time": end_time - start_time,
                        "processing_time": metadata.get("processing_time", 0),
                        "route_length": len(data["route"]),
                        "metrics": metadata.get("algorithm_metrics", {}),
                    }
                )

            else:
                print(f"✗ Request failed ({response.status_code})")
                try:
                    error_data = response.json()
                    print(f"Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"Error: {response.text}")

                results.append(
                    {
                        "test_case": test_case["name"],
                        "success": False,
                        "status_code": response.status_code,
                        "error": response.text,
                    }
                )

        except Exception as e:
            print(f"✗ Exception during test case {i+1}: {str(e)}")
            results.append(
                {
                    "test_case": test_case["name"],
                    "success": False,
                    "error": str(e),
                }
            )

    # Summary
    print("\n=== Test Summary ===")
    successful_tests = sum(1 for r in results if r["success"])
    print(f"Successful tests: {successful_tests}/{len(results)}")

    if successful_tests > 0:
        avg_api_time = (
            sum(r["api_time"] for r in results if r["success"])
            / successful_tests
        )
        avg_processing_time = (
            sum(r["processing_time"] for r in results if r["success"])
            / successful_tests
        )
        print(f"Average API response time: {avg_api_time:.4f} seconds")
        print(f"Average processing time: {avg_processing_time:.4f} seconds")

        # Find best performance
        best_result = max(
            [r for r in results if r["success"]],
            key=lambda x: x["metrics"].get("pareto_front_size", 0),
        )
        print(
            f"Best Pareto front size: {best_result['metrics'].get('pareto_front_size', 0)} "
            f"({best_result['test_case']})"
        )

    print("\n=== Multi-Objective Optimization API Test Complete ===")

    # Save results
    with open("test_multi_objective_api_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    return results


if __name__ == "__main__":
    test_multi_objective_api()
