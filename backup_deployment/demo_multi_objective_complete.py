#!/usr/bin/env python3
"""
Demo: Multi-Objective Optimization Complete Integration
Demonstrates the complete multi-objective optimization integration with RouteForce
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.optimization.multi_objective import (
    MultiObjectiveOptimizer,
    MultiObjectiveConfig,
)
import json
import time


def demo_multi_objective_complete():
    """Complete demo of multi-objective optimization"""
    print("=== RouteForce Multi-Objective Optimization Demo ===")
    print("Demonstrating NSGA-II based multi-objective route optimization")
    print()

    # Sample stores representing a real delivery scenario
    stores = [
        {
            "id": 1,
            "name": "Downtown Store",
            "lat": 40.7128,
            "lon": -74.0060,
            "priority": 1,
            "demand": 50,
            "service_time": 0.5,
        },
        {
            "id": 2,
            "name": "Central Park Store",
            "lat": 40.7589,
            "lon": -73.9851,
            "priority": 2,
            "demand": 30,
            "service_time": 0.3,
        },
        {
            "id": 3,
            "name": "Queens Store",
            "lat": 40.7282,
            "lon": -73.7949,
            "priority": 3,
            "demand": 40,
            "service_time": 0.4,
        },
        {
            "id": 4,
            "name": "Brooklyn Store",
            "lat": 40.6782,
            "lon": -73.9442,
            "priority": 1,
            "demand": 60,
            "service_time": 0.6,
        },
        {
            "id": 5,
            "name": "Midtown Store",
            "lat": 40.7505,
            "lon": -73.9934,
            "priority": 2,
            "demand": 25,
            "service_time": 0.25,
        },
        {
            "id": 6,
            "name": "Upper West Store",
            "lat": 40.7831,
            "lon": -73.9712,
            "priority": 3,
            "demand": 35,
            "service_time": 0.35,
        },
        {
            "id": 7,
            "name": "Financial District",
            "lat": 40.7061,
            "lon": -74.0087,
            "priority": 1,
            "demand": 45,
            "service_time": 0.45,
        },
        {
            "id": 8,
            "name": "East Side Store",
            "lat": 40.7614,
            "lon": -73.9776,
            "priority": 2,
            "demand": 55,
            "service_time": 0.55,
        },
        {
            "id": 9,
            "name": "Harlem Store",
            "lat": 40.8176,
            "lon": -73.9782,
            "priority": 3,
            "demand": 20,
            "service_time": 0.2,
        },
        {
            "id": 10,
            "name": "Battery Park Store",
            "lat": 40.7033,
            "lon": -74.0170,
            "priority": 1,
            "demand": 65,
            "service_time": 0.65,
        },
    ]

    print(
        f"Scenario: Optimizing delivery route for {len(stores)} stores in NYC"
    )
    print("Each store has different priorities, demands, and service times")
    print()

    # Test different optimization scenarios
    scenarios = [
        {
            "name": "Scenario 1: Distance vs Time",
            "description": "Minimize total distance while considering travel time",
            "config": MultiObjectiveConfig(
                population_size=80,
                generations=100,
                objectives=["distance", "time"],
            ),
        },
        {
            "name": "Scenario 2: Distance vs Priority",
            "description": "Balance distance efficiency with priority-based routing",
            "config": MultiObjectiveConfig(
                population_size=80,
                generations=100,
                objectives=["distance", "priority"],
            ),
        },
        {
            "name": "Scenario 3: Triple Objective",
            "description": "Optimize distance, time, and priority simultaneously",
            "config": MultiObjectiveConfig(
                population_size=100,
                generations=120,
                objectives=["distance", "time", "priority"],
            ),
        },
        {
            "name": "Scenario 4: Complete Multi-Objective",
            "description": "Optimize all available objectives (distance, time, priority, fuel_cost)",
            "config": MultiObjectiveConfig(
                population_size=120,
                generations=150,
                objectives=["distance", "time", "priority", "fuel_cost"],
            ),
        },
    ]

    results = []

    for i, scenario in enumerate(scenarios):
        print(f"--- {scenario['name']} ---")
        print(f"Description: {scenario['description']}")
        print(f"Objectives: {scenario['config'].objectives}")
        print()

        try:
            # Initialize optimizer
            optimizer = MultiObjectiveOptimizer(scenario["config"])

            # Run optimization
            start_time = time.time()
            best_route, metrics = optimizer.optimize(stores)
            end_time = time.time()

            # Display results
            print(
                f"✓ Optimization completed in {end_time - start_time:.2f} seconds"
            )
            print(
                f"✓ Pareto front size: {metrics.get('pareto_front_size', 0)} solutions"
            )
            print(
                f"✓ Total generations: {metrics.get('total_generations', 0)}"
            )
            print(f"✓ Hypervolume: {metrics.get('hypervolume', 0.0):.2f}")

            # Show best compromise solution
            if "best_compromise_solution" in metrics:
                print("\n📊 Best Compromise Solution:")
                objectives = metrics["best_compromise_solution"]["objectives"]
                for obj, value in objectives.items():
                    if obj == "distance":
                        print(f"  • Total Distance: {value:.2f} km")
                    elif obj == "time":
                        print(f"  • Total Time: {value:.2f} hours")
                    elif obj == "priority":
                        print(f"  • Priority Score: {abs(value):.0f}")
                    elif obj == "fuel_cost":
                        print(f"  • Fuel Cost: ${value:.2f}")

            # Show route
            print(f"\n🚛 Optimized Route ({len(best_route)} stops):")
            for j, store in enumerate(best_route[:5]):  # Show first 5 stops
                print(
                    f"  {j+1}. {store['name']} (Priority: {store.get('priority', 'N/A')}, Demand: {store.get('demand', 'N/A')})"
                )
            if len(best_route) > 5:
                print(f"  ... and {len(best_route) - 5} more stops")

            results.append(
                {
                    "scenario": scenario["name"],
                    "success": True,
                    "processing_time": end_time - start_time,
                    "pareto_front_size": metrics.get("pareto_front_size", 0),
                    "hypervolume": metrics.get("hypervolume", 0.0),
                    "objectives": scenario["config"].objectives,
                    "best_solution": metrics.get(
                        "best_compromise_solution", {}
                    ),
                }
            )

        except Exception as e:
            print(f"✗ Error in {scenario['name']}: {str(e)}")
            results.append(
                {
                    "scenario": scenario["name"],
                    "success": False,
                    "error": str(e),
                }
            )

        print("\n" + "=" * 60 + "\n")

    # Summary and analysis
    print("📈 OPTIMIZATION SUMMARY")
    print("=" * 50)

    successful_scenarios = [r for r in results if r["success"]]
    if successful_scenarios:
        print(
            f"✅ Successful optimizations: {len(successful_scenarios)}/{len(results)}"
        )

        avg_time = sum(
            r["processing_time"] for r in successful_scenarios
        ) / len(successful_scenarios)
        print(f"⏱️  Average processing time: {avg_time:.2f} seconds")

        best_scenario = max(
            successful_scenarios, key=lambda x: x["pareto_front_size"]
        )
        print(
            f"🏆 Best Pareto front: {best_scenario['pareto_front_size']} solutions ({best_scenario['scenario']})"
        )

        total_objectives = sum(
            len(r["objectives"]) for r in successful_scenarios
        )
        print(f"🎯 Total objectives optimized: {total_objectives}")

        print("\n💡 Key Insights:")
        print(
            "• Multi-objective optimization provides multiple trade-off solutions"
        )
        print("• Larger Pareto fronts offer more choice in route selection")
        print(
            "• Different objective combinations suit different business needs"
        )
        print("• NSGA-II efficiently handles complex routing constraints")

    else:
        print("❌ No successful optimizations")

    print("\n" + "=" * 60)
    print("🚀 Multi-Objective Optimization Demo Complete!")
    print(
        "The system can now handle complex routing scenarios with multiple competing objectives."
    )

    # Save results
    with open("demo_multi_objective_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    return results


if __name__ == "__main__":
    demo_multi_objective_complete()
