#!/usr/bin/env python3
"""
Direct test script for Simulated Annealing algorithm integration
Tests the algorithm directly without going through the API
"""
import time
import json
from typing import List, Dict, Any

from app.optimization.simulated_annealing import (
    SimulatedAnnealingOptimizer,
    SimulatedAnnealingConfig,
)


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


def test_simulated_annealing_basic():
    """Test basic Simulated Annealing functionality"""
    print("🔥 Testing Simulated Annealing - Basic Functionality")
    print("=" * 60)

    # Create test stores
    stores = create_test_stores(8)
    print(f"Created {len(stores)} test stores")

    # Create default configuration
    config = SimulatedAnnealingConfig()
    print(f"Configuration: {config}")

    # Initialize Simulated Annealing
    sa = SimulatedAnnealingOptimizer(config)

    # Run optimization
    start_time = time.time()
    try:
        optimized_route, metrics = sa.optimize(stores)
        processing_time = time.time() - start_time

        print(f"\n✅ Optimization completed in {processing_time:.2f}s")
        print(f"Original stores: {len(stores)}")
        print(f"Optimized route: {len(optimized_route)} stops")
        print(f"Algorithm: {metrics.get('algorithm', 'unknown')}")

        # Print metrics
        print("\n📊 Algorithm Metrics:")
        print(f"  Initial distance: {metrics.get('initial_distance', 0):.2f}")
        print(f"  Final distance: {metrics.get('final_distance', 0):.2f}")
        print(f"  Improvement: {metrics.get('improvement_percent', 0):.2f}%")
        print(f"  Iterations: {metrics.get('total_iterations', 0)}")
        print(f"  Accepted moves: {metrics.get('accepted_moves', 0)}")
        print(f"  Rejected moves: {metrics.get('rejected_moves', 0)}")
        print(f"  Acceptance rate: {metrics.get('acceptance_rate', 0):.2f}")

        # Print route summary
        print("\n🗺️  Route Summary:")
        for i, stop in enumerate(optimized_route):
            print(
                f"  {i+1}. {stop.get('name', 'Unknown')} - {stop.get('address', 'No address')}"
            )

        return True

    except Exception as e:
        print(f"❌ Error during optimization: {str(e)}")
        return False


def test_simulated_annealing_custom_config():
    """Test Simulated Annealing with custom configuration"""
    print("\n🔧 Testing Simulated Annealing - Custom Configuration")
    print("=" * 60)

    # Create test stores
    stores = create_test_stores(12)
    print(f"Created {len(stores)} test stores")

    # Create custom configuration
    config = SimulatedAnnealingConfig(
        initial_temperature=2000.0,
        final_temperature=0.01,
        cooling_rate=0.95,
        max_iterations=5000,
        iterations_per_temp=50,
        reheat_threshold=500,
        min_improvement_threshold=0.005,
    )

    print(f"Custom configuration:")
    print(f"  Initial temperature: {config.initial_temperature}")
    print(f"  Final temperature: {config.final_temperature}")
    print(f"  Cooling rate: {config.cooling_rate}")
    print(f"  Max iterations: {config.max_iterations}")
    print(f"  Iterations per temp: {config.iterations_per_temp}")
    print(f"  Reheat threshold: {config.reheat_threshold}")
    print(f"  Min improvement threshold: {config.min_improvement_threshold}")

    # Initialize Simulated Annealing
    sa = SimulatedAnnealingOptimizer(config)

    # Run optimization
    start_time = time.time()
    try:
        optimized_route, metrics = sa.optimize(stores)
        processing_time = time.time() - start_time

        print(f"\n✅ Optimization completed in {processing_time:.2f}s")
        print(f"Final route length: {len(optimized_route)} stops")

        # Print key metrics
        print("\n📊 Key Metrics:")
        print(f"  Iterations performed: {metrics.get('total_iterations', 0)}")
        print(f"  Initial distance: {metrics.get('initial_distance', 0):.2f}")
        print(f"  Final distance: {metrics.get('final_distance', 0):.2f}")
        print(f"  Improvement: {metrics.get('improvement_percent', 0):.2f}%")
        print(f"  Accepted moves: {metrics.get('accepted_moves', 0)}")
        print(f"  Rejected moves: {metrics.get('rejected_moves', 0)}")
        print(f"  Acceptance rate: {metrics.get('acceptance_rate', 0):.2f}")

        return True

    except Exception as e:
        print(f"❌ Error during optimization: {str(e)}")
        return False


def test_simulated_annealing_performance():
    """Test Simulated Annealing performance with larger datasets"""
    print("\n⚡ Testing Simulated Annealing - Performance")
    print("=" * 60)

    test_sizes = [5, 10, 15, 20]
    results = []

    for size in test_sizes:
        print(f"\nTesting with {size} stores...")
        stores = create_test_stores(size)

        # Use fast configuration for performance testing
        config = SimulatedAnnealingConfig(
            initial_temperature=500.0,
            final_temperature=0.5,
            cooling_rate=0.98,
            max_iterations=2000,
            iterations_per_temp=50,
            reheat_threshold=300,
        )

        sa = SimulatedAnnealingOptimizer(config)

        start_time = time.time()
        try:
            optimized_route, metrics = sa.optimize(stores)
            processing_time = time.time() - start_time

            result = {
                "stores": size,
                "processing_time": processing_time,
                "route_length": len(optimized_route),
                "iterations": metrics.get("total_iterations", 0),
                "best_fitness": metrics.get("final_distance", 0),
            }
            results.append(result)

            print(
                f"  ✅ {size} stores: {processing_time:.2f}s, {result['iterations']} iterations"
            )

        except Exception as e:
            print(f"  ❌ {size} stores: Error - {str(e)}")

    # Print performance summary
    print("\n📈 Performance Summary:")
    print("Stores | Time (s) | Iterations | Best Fitness")
    print("-" * 45)
    for result in results:
        print(
            f"{result['stores']:6} | {result['processing_time']:8.2f} | {result['iterations']:10} | {result['best_fitness']:12.2f}"
        )

    return len(results) == len(test_sizes)


def test_simulated_annealing_comparison():
    """Compare different Simulated Annealing configurations"""
    print("\n🔬 Testing Simulated Annealing - Configuration Comparison")
    print("=" * 60)

    # Create test stores
    stores = create_test_stores(10)
    print(f"Testing with {len(stores)} stores")

    # Test different configurations
    configurations = [
        {
            "name": "Fast (Low Quality)",
            "config": SimulatedAnnealingConfig(
                initial_temperature=100.0,
                final_temperature=1.0,
                cooling_rate=0.90,
                max_iterations=500,
                iterations_per_temp=25,
                reheat_threshold=100,
            ),
        },
        {
            "name": "Balanced",
            "config": SimulatedAnnealingConfig(
                initial_temperature=1000.0,
                final_temperature=0.1,
                cooling_rate=0.99,
                max_iterations=5000,
                iterations_per_temp=100,
                reheat_threshold=500,
            ),
        },
        {
            "name": "Slow (High Quality)",
            "config": SimulatedAnnealingConfig(
                initial_temperature=2000.0,
                final_temperature=0.01,
                cooling_rate=0.995,
                max_iterations=20000,
                iterations_per_temp=200,
                reheat_threshold=2000,
            ),
        },
    ]

    results = []

    for test_config in configurations:
        print(f"\nTesting {test_config['name']}...")

        sa = SimulatedAnnealingOptimizer(test_config["config"])

        start_time = time.time()
        try:
            optimized_route, metrics = sa.optimize(stores)
            processing_time = time.time() - start_time

            result = {
                "name": test_config["name"],
                "processing_time": processing_time,
                "route_length": len(optimized_route),
                "iterations": metrics.get("total_iterations", 0),
                "best_fitness": metrics.get("final_distance", 0),
                "final_temperature": metrics.get("final_temperature", 0),
            }
            results.append(result)

            print(f"  ✅ Completed in {processing_time:.2f}s")
            print(f"     Iterations: {result['iterations']}")
            print(f"     Best fitness: {result['best_fitness']:.2f}")

        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

    # Print comparison summary
    print("\n📊 Configuration Comparison:")
    print("Configuration      | Time (s) | Iterations | Best Fitness | Final Temp")
    print("-" * 70)
    for result in results:
        print(
            f"{result['name']:18} | {result['processing_time']:8.2f} | {result['iterations']:10} | {result['best_fitness']:12.2f} | {result['final_temperature']:10.4f}"
        )

    return len(results) == len(configurations)


def main():
    """Run all Simulated Annealing tests"""
    print("🚀 RouteForce Simulated Annealing Algorithm - Direct Testing")
    print("=" * 70)

    # Track test results
    test_results = []

    # Run tests
    test_results.append(("Basic Functionality", test_simulated_annealing_basic()))
    test_results.append(
        ("Custom Configuration", test_simulated_annealing_custom_config())
    )
    test_results.append(("Performance Testing", test_simulated_annealing_performance()))
    test_results.append(
        ("Configuration Comparison", test_simulated_annealing_comparison())
    )

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
        print("🎉 All Simulated Annealing tests passed successfully!")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
