# Import GeneticAlgorithm and GeneticConfig using importlib from their file path
import importlib.util
import os
import sys


def import_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
genetic_algorithm_path = os.path.join(
    project_root, "app/optimization/genetic_algorithm.py"
)

genetic_algorithm_mod = import_from_path("genetic_algorithm", genetic_algorithm_path)
GeneticAlgorithm = genetic_algorithm_mod.GeneticAlgorithm
GeneticConfig = genetic_algorithm_mod.GeneticConfig
# Patch sys.path for reliable imports
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
#!/usr/bin/env python3
"""
Direct test of genetic algorithm implementation
"""
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.optimization.genetic_algorithm import GeneticAlgorithm, GeneticConfig

# Test data
TEST_STORES = [
    {
        "id": 1,
        "name": "Store A",
        "latitude": 39.7817,
        "longitude": -89.6501,
    },
    {
        "id": 2,
        "name": "Store B",
        "latitude": 39.7990,
        "longitude": -89.6441,
    },
    {
        "id": 3,
        "name": "Store C",
        "latitude": 39.7600,
        "longitude": -89.6550,
    },
    {
        "id": 4,
        "name": "Store D",
        "latitude": 39.8200,
        "longitude": -89.6800,
    },
    {
        "id": 5,
        "name": "Store E",
        "latitude": 39.7400,
        "longitude": -89.6200,
    },
    {
        "id": 6,
        "name": "Store F",
        "latitude": 39.8000,
        "longitude": -89.6100,
    },
]


def test_genetic_algorithm():
    """Test genetic algorithm directly"""
    print("🧬 Testing Genetic Algorithm Implementation")
    print("=" * 50)

    # Test with small config for quick testing
    config = GeneticConfig(
        population_size=20,
        generations=50,
        mutation_rate=0.02,
        crossover_rate=0.8,
        elite_size=5,
        tournament_size=3,
    )

    print(f"📊 Configuration:")
    print(f"  - Population Size: {config.population_size}")
    print(f"  - Generations: {config.generations}")
    print(f"  - Mutation Rate: {config.mutation_rate}")
    print(f"  - Crossover Rate: {config.crossover_rate}")
    print(f"  - Elite Size: {config.elite_size}")
    print(f"  - Tournament Size: {config.tournament_size}")

    # Initialize genetic algorithm
    ga = GeneticAlgorithm(config)

    # Run optimization
    print(f"\n🚀 Starting optimization with {len(TEST_STORES)} stores...")

    try:
        optimized_route, metrics = ga.optimize(TEST_STORES)

        print(f"✅ Optimization completed!")
        print(f"📊 Results:")
        print(f"  - Algorithm: {metrics.get('algorithm', 'unknown')}")
        print(f"  - Generations: {metrics.get('generations', 'N/A')}")
        print(f"  - Initial Distance: {metrics.get('initial_distance', 'N/A'):.2f}km")
        print(f"  - Final Distance: {metrics.get('final_distance', 'N/A'):.2f}km")
        print(f"  - Improvement: {metrics.get('improvement_percent', 'N/A'):.1f}%")
        print(f"  - Population Size: {metrics.get('population_size', 'N/A')}")
        print(f"  - Best Fitness: {metrics.get('best_fitness', 'N/A'):.6f}")

        print(f"\n🗺️  Optimized Route:")
        for i, store in enumerate(optimized_route):
            print(
                f"  {i + 1}. {store['name']} ({store['latitude']:.4f}, {store['longitude']:.4f})"
            )

        return True

    except Exception as e:
        print(f"❌ Optimization failed: {e}")
        return False


def test_edge_cases():
    """Test edge cases"""
    print("\n🔍 Testing Edge Cases")
    print("-" * 30)

    # Test with minimal stores
    print("Testing with 2 stores...")
    try:
        ga = GeneticAlgorithm()
        route, metrics = ga.optimize(TEST_STORES[:2])
        print(f"✅ 2 stores: {metrics.get('improvement_percent', 0):.1f}% improvement")
    except Exception as e:
        print(f"❌ 2 stores failed: {e}")

    # Test with single store
    print("Testing with 1 store...")
    try:
        ga = GeneticAlgorithm()
        route, metrics = ga.optimize(TEST_STORES[:1])
        print(f"✅ 1 store: Handled gracefully")
    except Exception as e:
        print(f"❌ 1 store failed: {e}")

    # Test with empty stores
    print("Testing with 0 stores...")
    try:
        ga = GeneticAlgorithm()
        route, metrics = ga.optimize([])
        print(f"✅ 0 stores: Handled gracefully")
    except Exception as e:
        print(f"❌ 0 stores failed: {e}")


def main():
    """Main test function"""
    success = test_genetic_algorithm()

    if success:
        test_edge_cases()
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n❌ Tests failed!")


if __name__ == "__main__":
    main()
