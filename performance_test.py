#!/usr/bin/env python3
"""
Performance testing script for RouteForceRouting optimization algorithms.
Tests scalability, memory usage, and execution time across different dataset sizes.
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List

import psutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routing_engine import (
    OptimizationMethod,
    RouteOptimizer,
    Store,
    Vehicle,
    VehicleStatus,
)


def generate_synthetic_stores(count: int, seed: int = 42) -> List[Store]:
    """Generate synthetic store dataset for performance testing."""
    import random

    random.seed(seed)

    stores = []

    # NYC area coordinates
    base_lat, base_lng = 40.7128, -74.0060
    lat_range, lng_range = 0.5, 0.5  # Roughly 50km radius

    store_chains = ["CVS", "WLG", "RIT", "DLR", "TGT"]
    priorities = ["high", "medium", "low"]
    delivery_windows = [
        "08:00-18:00",
        "09:00-17:00",
        "10:00-16:00",
        "11:00-15:00",
        "08:30-16:30",
        "09:30-17:30",
    ]

    for i in range(count):
        # Random location within NYC area
        lat = base_lat + (random.random() - 0.5) * lat_range
        lng = base_lng + (random.random() - 0.5) * lng_range

        # Vary store characteristics
        chain = store_chains[i % len(store_chains)]
        priority = priorities[i % len(priorities)]
        window = delivery_windows[i % len(delivery_windows)]

        store = Store(
            store_id=f"{chain}_{i + 1:04d}",
            name=f"{chain} Store #{i + 1}",
            address=f"{100 + i} Performance Test Ave, NYC",
            coordinates={"lat": lat, "lng": lng},
            delivery_window=window,
            priority=priority,
            estimated_service_time=10 + (i % 3) * 5,  # 10-20 minutes
            packages=1 + (i % 8),  # 1-8 packages
            weight_kg=5.0 + (i % 20) * 2.5,  # 5-55 kg
            special_requirements={"signature_required": i % 3 == 0},
        )
        stores.append(store)

    return stores


def generate_test_fleet(size: int = 5) -> List[Vehicle]:
    """Generate test vehicle fleet."""
    vehicles = []

    vehicle_types = [
        {"type": "VAN", "capacity": 800, "packages": 30, "hours": 8},
        {"type": "TRUCK", "capacity": 1200, "packages": 45, "hours": 10},
        {"type": "LARGE_TRUCK", "capacity": 1500, "packages": 60, "hours": 12},
    ]

    for i in range(size):
        vtype = vehicle_types[i % len(vehicle_types)]

        vehicle = Vehicle(
            vehicle_id=f"{vtype['type']}_{i + 1:02d}",
            capacity_kg=vtype["capacity"],
            max_packages=vtype["packages"],
            max_driving_hours=vtype["hours"],
            status=VehicleStatus.AVAILABLE,
            current_location={"lat": 40.7128 + i * 0.01, "lng": -74.0060 + i * 0.01},
            driver_id=f"DRIVER_{i + 1:02d}",
        )
        vehicles.append(vehicle)

    return vehicles


def measure_performance(func, *args, **kwargs) -> Dict[str, Any]:
    """Measure execution time and memory usage of a function."""
    process = psutil.Process(os.getpid())

    # Initial measurements
    start_time = time.time()
    start_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Execute function
    result = func(*args, **kwargs)

    # Final measurements
    end_time = time.time()
    end_memory = process.memory_info().rss / 1024 / 1024  # MB

    return {
        "result": result,
        "execution_time_seconds": end_time - start_time,
        "memory_usage_mb": end_memory - start_memory,
        "peak_memory_mb": end_memory,
    }


def run_scalability_test(
    dataset_sizes: List[int], methods: List[OptimizationMethod]
) -> Dict[str, Any]:
    """Run scalability tests across different dataset sizes and methods."""
    results = {"timestamp": datetime.now().isoformat(), "tests": []}

    fleet = generate_test_fleet(8)  # Large fleet for testing

    for size in dataset_sizes:
        print(f"\n{'=' * 50}")
        print(f"Testing with {size} stores...")
        print(f"{'=' * 50}")

        stores = generate_synthetic_stores(size)

        size_results = {
            "dataset_size": size,
            "store_count": len(stores),
            "vehicle_count": len(fleet),
            "methods": {},
        }

        for method in methods:
            print(f"  Testing {method.value}...")

            optimizer = RouteOptimizer()

            # Measure performance
            perf_data = measure_performance(
                optimizer.optimize_multi_vehicle_routes, stores, fleet, method
            )

            routes = perf_data["result"]

            # Calculate route statistics
            total_distance = sum(r.total_distance_km for r in routes)
            total_duration = sum(r.estimated_duration_hours for r in routes)
            total_stops = sum(len(r.stops) for r in routes)

            method_results = {
                "execution_time_seconds": perf_data["execution_time_seconds"],
                "memory_usage_mb": perf_data["memory_usage_mb"],
                "peak_memory_mb": perf_data["peak_memory_mb"],
                "routes_generated": len(routes),
                "total_distance_km": total_distance,
                "total_duration_hours": total_duration,
                "total_stops": total_stops,
                "avg_stops_per_route": total_stops / len(routes) if routes else 0,
                "stores_per_second": size / perf_data["execution_time_seconds"]
                if perf_data["execution_time_seconds"] > 0
                else 0,
            }

            size_results["methods"][method.value] = method_results

            print(f"    Time: {perf_data['execution_time_seconds']:.3f}s")
            print(f"    Memory: {perf_data['memory_usage_mb']:.1f}MB")
            print(f"    Routes: {len(routes)}")
            print(f"    Speed: {method_results['stores_per_second']:.1f} stores/sec")

        results["tests"].append(size_results)

    return results


def run_stress_test(max_stores: int = 1000, increment: int = 100) -> Dict[str, Any]:
    """Run stress test to find performance breaking points."""
    print(f"\n{'=' * 60}")
    print(f"STRESS TEST: Finding performance limits up to {max_stores} stores")
    print(f"{'=' * 60}")

    fleet = generate_test_fleet(10)
    optimizer = RouteOptimizer()
    stress_results = {"max_stores_tested": 0, "breaking_point": None, "results": []}

    current_size = increment
    while current_size <= max_stores:
        print(f"\nStress testing with {current_size} stores...")

        try:
            stores = generate_synthetic_stores(current_size)

            # Set timeout for stress test (30 seconds max)

            perf_data = measure_performance(
                optimizer.optimize_multi_vehicle_routes,
                stores,
                fleet,
                OptimizationMethod.NEAREST_NEIGHBOR,
            )

            execution_time = perf_data["execution_time_seconds"]

            # Check if performance is still acceptable
            stores_per_second = (
                current_size / execution_time if execution_time > 0 else 0
            )

            result = {
                "store_count": current_size,
                "execution_time_seconds": execution_time,
                "memory_usage_mb": perf_data["memory_usage_mb"],
                "stores_per_second": stores_per_second,
                "routes_generated": len(perf_data["result"]),
                "status": "success",
            }

            stress_results["results"].append(result)
            stress_results["max_stores_tested"] = current_size

            print(
                f"  ✅ SUCCESS: {execution_time:.2f}s, {stores_per_second:.1f} stores/sec"
            )

            # Check for performance degradation
            if execution_time > 60:  # More than 1 minute
                print("  ⚠️  WARNING: Performance degrading (>60s execution time)")
                stress_results["breaking_point"] = current_size
                break

            if perf_data["peak_memory_mb"] > 500:  # More than 500MB
                print(
                    f"  ⚠️  WARNING: High memory usage ({perf_data['peak_memory_mb']:.1f}MB)"
                )

        except Exception as e:
            print(f"  ❌ FAILED: {str(e)}")
            result = {"store_count": current_size, "status": "failed", "error": str(e)}
            stress_results["results"].append(result)
            stress_results["breaking_point"] = current_size
            break

        current_size += increment

    return stress_results


def generate_performance_report(results: Dict[str, Any]) -> str:
    """Generate formatted performance report."""
    report = []
    report.append("# RouteForceRouting Performance Test Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    if "tests" in results:
        report.append("## Scalability Test Results")
        report.append("")
        report.append(
            "| Dataset Size | Method | Time (s) | Memory (MB) | Routes | Stores/sec |"
        )
        report.append(
            "|--------------|--------|----------|-------------|--------|------------|"
        )

        for test in results["tests"]:
            size = test["dataset_size"]
            for method, data in test["methods"].items():
                report.append(
                    f"| {size:,} | {method} | {data['execution_time_seconds']:.3f} | "
                    f"{data['memory_usage_mb']:.1f} | {data['routes_generated']} | "
                    f"{data['stores_per_second']:.1f} |"
                )

        report.append("")

    if "results" in results and "max_stores_tested" in results:
        report.append("## Stress Test Results")
        report.append("")
        report.append(f"Maximum stores tested: {results['max_stores_tested']:,}")

        if results.get("breaking_point"):
            report.append(
                f"Performance breaking point: {results['breaking_point']:,} stores"
            )
        else:
            report.append("No breaking point found within test limits")

        report.append("")
        report.append("### Stress Test Details")
        report.append("| Stores | Time (s) | Memory (MB) | Routes | Status |")
        report.append("|--------|----------|-------------|--------|--------|")

        for result in results["results"]:
            if result["status"] == "success":
                report.append(
                    f"| {result['store_count']:,} | {result['execution_time_seconds']:.2f} | "
                    f"{result['memory_usage_mb']:.1f} | {result['routes_generated']} | ✅ |"
                )
            else:
                report.append(f"| {result['store_count']:,} | - | - | - | ❌ |")

    return "\n".join(report)


def main():
    """Main performance testing function."""
    print("RouteForceRouting Performance Testing Suite")
    print("=" * 50)

    # Configuration
    dataset_sizes = [10, 25, 50, 100, 200, 500]
    methods = [OptimizationMethod.NEAREST_NEIGHBOR, OptimizationMethod.TWO_OPT]

    # Run scalability tests
    print("Starting scalability tests...")
    scalability_results = run_scalability_test(dataset_sizes, methods)

    # Run stress tests
    print("\nStarting stress tests...")
    stress_results = run_stress_test(max_stores=1000, increment=100)

    # Combine results
    combined_results = {
        "scalability": scalability_results,
        "stress_test": stress_results,
        "summary": {
            "test_completed": datetime.now().isoformat(),
            "max_dataset_tested": max(dataset_sizes),
            "methods_tested": [m.value for m in methods],
            "stress_test_limit": stress_results.get("max_stores_tested", 0),
        },
    }

    # Generate and save report
    report = generate_performance_report(scalability_results)
    stress_report = generate_performance_report(stress_results)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save JSON results
    results_file = f"logs/2025-07-24/performance_results_{timestamp}.json"
    os.makedirs(os.path.dirname(results_file), exist_ok=True)

    with open(results_file, "w") as f:
        json.dump(combined_results, f, indent=2)

    # Save markdown report
    report_file = f"logs/2025-07-24/performance_report_{timestamp}.md"
    with open(report_file, "w") as f:
        f.write(report)
        f.write("\n\n")
        f.write(stress_report)

    print(f"\n{'=' * 60}")
    print("PERFORMANCE TESTING COMPLETE")
    print(f"{'=' * 60}")
    print(f"Results saved to: {results_file}")
    print(f"Report saved to: {report_file}")
    print(f"Max stores tested: {stress_results.get('max_stores_tested', 'N/A')}")

    if stress_results.get("breaking_point"):
        print(
            f"⚠️  Performance breaking point: {stress_results['breaking_point']} stores"
        )
    else:
        print("✅ No performance breaking point found")


if __name__ == "__main__":
    main()
