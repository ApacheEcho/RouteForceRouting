#!/usr/bin/env python3
"""
Test Multi-Objective Optimization - Direct Implementation
Tests the multi-objective optimizer directly without API
"""

import json
import time

from app.optimization.multi_objective import (
    MultiObjectiveConfig,
    MultiObjectiveOptimizer,
)


def test_multi_objective_direct():
    """Test multi-objective optimization directly"""
    print("=== Testing Multi-Objective Optimization - Direct Implementation ===")

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

    # Test different objective combinations
    test_cases = [
        {
            "name": "Distance + Time",
            "objectives": ["distance", "time"],
            "config": MultiObjectiveConfig(
                population_size=50, generations=100, objectives=["distance", "time"]
            ),
        },
        {
            "name": "Distance + Priority",
            "objectives": ["distance", "priority"],
            "config": MultiObjectiveConfig(
                population_size=50, generations=100, objectives=["distance", "priority"]
            ),
        },
        {
            "name": "Distance + Time + Priority",
            "objectives": ["distance", "time", "priority"],
            "config": MultiObjectiveConfig(
                population_size=60,
                generations=120,
                objectives=["distance", "time", "priority"],
            ),
        },
        {
            "name": "All Objectives",
            "objectives": ["distance", "time", "priority", "fuel_cost"],
            "config": MultiObjectiveConfig(
                population_size=80,
                generations=150,
                objectives=["distance", "time", "priority", "fuel_cost"],
            ),
        },
    ]

    results = []

    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test Case {i + 1}: {test_case['name']} ---")
        print(f"Objectives: {test_case['objectives']}")

        try:
            # Initialize optimizer
            optimizer = MultiObjectiveOptimizer(test_case["config"])

            # Run optimization
            start_time = time.time()
            best_route, metrics = optimizer.optimize(stores)
            end_time = time.time()

            print(f"Processing time: {end_time - start_time:.4f} seconds")
            print(f"Algorithm: {metrics.get('algorithm', 'unknown')}")
            print(f"Pareto front size: {metrics.get('pareto_front_size', 0)}")
            print(f"Total generations: {metrics.get('total_generations', 0)}")
            print(f"Hypervolume: {metrics.get('hypervolume', 0.0):.4f}")

            # Display best compromise solution
            if "best_compromise_solution" in metrics:
                print("\nBest compromise solution objectives:")
                for obj, value in metrics["best_compromise_solution"][
                    "objectives"
                ].items():
                    print(f"  {obj}: {value:.4f}")

            # Display route
            print(f"\nBest route ({len(best_route)} stores):")
            for j, store in enumerate(best_route):
                print(
                    f"  {j + 1}. {store['name']} (Priority: {store.get('priority', 'N/A')})"
                )

            results.append(
                {
                    "test_case": test_case["name"],
                    "success": True,
                    "processing_time": end_time - start_time,
                    "metrics": metrics,
                    "route_length": len(best_route),
                }
            )

        except Exception as e:
            print(f"Error in test case {i + 1}: {str(e)}")
            results.append(
                {"test_case": test_case["name"], "success": False, "error": str(e)}
            )

    # Summary
    print("\n=== Test Summary ===")
    successful_tests = sum(1 for r in results if r["success"])
    print(f"Successful tests: {successful_tests}/{len(results)}")

    # Assert that all test cases succeeded
    assert successful_tests == len(results), (
        f"Some test cases failed: {[r for r in results if not r['success']]}"
    )

    if successful_tests > 0:
        avg_time = (
            sum(r["processing_time"] for r in results if r["success"])
            / successful_tests
        )
        print(f"Average processing time: {avg_time:.4f} seconds")

        # Find best performance
        best_result = max(
            [r for r in results if r["success"]],
            key=lambda x: x["metrics"].get("pareto_front_size", 0),
        )
        print(
            f"Best Pareto front size: {best_result['metrics'].get('pareto_front_size', 0)} "
            f"({best_result['test_case']})"
        )

    print("\n=== Multi-Objective Optimization Direct Test Complete ===")

    # Save results
    with open("test_multi_objective_direct_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    # No return statement; test function should return None


if __name__ == "__main__":
    test_multi_objective_direct()
