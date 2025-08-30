#!/usr/bin/env python3
"""
Test script for genetic algorithm integration
"""
import os
import pytest
import requests
import json
import time
from typing import Dict, List, Any

# Mark as integration; skip unless explicitly enabled
pytestmark = pytest.mark.integration
if not os.getenv("RUN_INTEGRATION"):
    pytest.skip("Integration test requires running server; set RUN_INTEGRATION=1 to enable.", allow_module_level=True)

# Test data
TEST_STORES = [
    {
        "id": 1,
        "name": "Store A",
        "address": "123 Main St",
        "city": "Springfield",
        "state": "IL",
        "zip": "62701",
        "latitude": 39.7817,
        "longitude": -89.6501,
        "chain": "SuperMart",
    },
    {
        "id": 2,
        "name": "Store B",
        "address": "456 Oak Ave",
        "city": "Springfield",
        "state": "IL",
        "zip": "62702",
        "latitude": 39.7990,
        "longitude": -89.6441,
        "chain": "SuperMart",
    },
    {
        "id": 3,
        "name": "Store C",
        "address": "789 Pine St",
        "city": "Springfield",
        "state": "IL",
        "zip": "62703",
        "latitude": 39.7600,
        "longitude": -89.6550,
        "chain": "SuperMart",
    },
    {
        "id": 4,
        "name": "Store D",
        "address": "321 Elm St",
        "city": "Springfield",
        "state": "IL",
        "zip": "62704",
        "latitude": 39.8200,
        "longitude": -89.6800,
        "chain": "SuperMart",
    },
    {
        "id": 5,
        "name": "Store E",
        "address": "654 Maple Ave",
        "city": "Springfield",
        "state": "IL",
        "zip": "62705",
        "latitude": 39.7400,
        "longitude": -89.6200,
        "chain": "SuperMart",
    },
    {
        "id": 6,
        "name": "Store F",
        "address": "987 Cedar St",
        "city": "Springfield",
        "state": "IL",
        "zip": "62706",
        "latitude": 39.8000,
        "longitude": -89.6100,
        "chain": "SuperMart",
    },
    {
        "id": 7,
        "name": "Store G",
        "address": "147 Birch St",
        "city": "Springfield",
        "state": "IL",
        "zip": "62707",
        "latitude": 39.7750,
        "longitude": -89.6750,
        "chain": "SuperMart",
    },
    {
        "id": 8,
        "name": "Store H",
        "address": "258 Walnut St",
        "city": "Springfield",
        "state": "IL",
        "zip": "62708",
        "latitude": 39.7900,
        "longitude": -89.6300,
        "chain": "SuperMart",
    },
]

BASE_URL = "http://localhost:5001"


def test_api_health():
    """Test API health endpoint"""
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Health: {data['status']}")
            print(
                f"📊 Available algorithms: {data.get('algorithms', {}).get('available', [])}"
            )
            return True
        else:
            print(f"❌ API Health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Health error: {e}")
        return False


def test_get_algorithms():
    """Test get algorithms endpoint"""
    print("\n🔍 Testing get algorithms endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/routes/algorithms")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Available algorithms: {list(data['algorithms'].keys())}")

            # Print genetic algorithm parameters
            if "genetic" in data["algorithms"]:
                genetic_params = data["algorithms"]["genetic"]["parameters"]
                print(f"🧬 Genetic Algorithm Parameters:")
                for param, config in genetic_params.items():
                    print(
                        f"  - {param}: {config['description']} (default: {config['default']})"
                    )

            return True
        else:
            print(f"❌ Get algorithms failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get algorithms error: {e}")
        return False


def test_default_algorithm():
    """Test route generation with default algorithm"""
    print("\n🔍 Testing default algorithm...")
    try:
        payload = {
            "stores": TEST_STORES,
            "constraints": {},
            "options": {"algorithm": "default"},
        }

        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/v1/routes", json=payload)
        duration = time.time() - start_time

        if response.status_code == 201:
            data = response.json()
            metadata = data.get("metadata", {})

            print(
                f"✅ Default Algorithm - Generated route with {metadata.get('route_stores', 0)} stores"
            )
            print(f"⏱️  Processing time: {duration:.2f}s")
            print(f"📊 Optimization score: {metadata.get('optimization_score', 0):.2f}")
            print(f"🔧 Algorithm used: {metadata.get('algorithm_used', 'unknown')}")

            return data
        else:
            print(f"❌ Default algorithm failed: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Default algorithm error: {e}")
        return None


def test_genetic_algorithm():
    """Test route generation with genetic algorithm"""
    print("\n🔍 Testing genetic algorithm...")
    try:
        payload = {
            "stores": TEST_STORES,
            "constraints": {},
            "options": {
                "algorithm": "genetic",
                "ga_population_size": 50,
                "ga_generations": 100,
                "ga_mutation_rate": 0.02,
                "ga_crossover_rate": 0.8,
                "ga_elite_size": 10,
                "ga_tournament_size": 3,
            },
        }

        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/v1/routes", json=payload)
        duration = time.time() - start_time

        if response.status_code == 201:
            data = response.json()
            metadata = data.get("metadata", {})

            print(
                f"✅ Genetic Algorithm - Generated route with {metadata.get('route_stores', 0)} stores"
            )
            print(f"⏱️  Processing time: {duration:.2f}s")
            print(f"📊 Optimization score: {metadata.get('optimization_score', 0):.2f}")
            print(f"🔧 Algorithm used: {metadata.get('algorithm_used', 'unknown')}")

            # Print genetic algorithm specific metrics
            if "algorithm_metrics" in metadata:
                ga_metrics = metadata["algorithm_metrics"]
                print(f"🧬 Genetic Algorithm Metrics:")
                print(f"  - Generations: {ga_metrics.get('generations', 'N/A')}")
                print(
                    f"  - Final distance: {ga_metrics.get('final_distance', 'N/A'):.2f}km"
                )
                print(
                    f"  - Improvement: {ga_metrics.get('improvement_percent', 'N/A'):.1f}%"
                )
                print(
                    f"  - Population size: {ga_metrics.get('population_size', 'N/A')}"
                )

            return data
        else:
            print(f"❌ Genetic algorithm failed: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Genetic algorithm error: {e}")
        return None


def test_genetic_optimize_endpoint():
    """Test dedicated genetic algorithm optimization endpoint"""
    print("\n🔍 Testing dedicated genetic optimization endpoint...")
    try:
        payload = {
            "stores": TEST_STORES,
            "constraints": {},
            "genetic_config": {
                "population_size": 80,
                "generations": 200,
                "mutation_rate": 0.03,
                "crossover_rate": 0.85,
                "elite_size": 15,
                "tournament_size": 4,
            },
        }

        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/routes/optimize/genetic", json=payload
        )
        duration = time.time() - start_time

        if response.status_code == 201:
            data = response.json()
            metadata = data.get("metadata", {})

            print(
                f"✅ Genetic Optimize - Generated route with {metadata.get('route_stores', 0)} stores"
            )
            print(f"⏱️  Processing time: {duration:.2f}s")
            print(f"📊 Optimization score: {metadata.get('optimization_score', 0):.2f}")

            # Print genetic algorithm specific metrics
            if "genetic_metrics" in data:
                ga_metrics = data["genetic_metrics"]
                print(f"🧬 Genetic Algorithm Metrics:")
                print(f"  - Generations: {ga_metrics.get('generations', 'N/A')}")
                print(
                    f"  - Final distance: {ga_metrics.get('final_distance', 'N/A'):.2f}km"
                )
                print(
                    f"  - Improvement: {ga_metrics.get('improvement_percent', 'N/A'):.1f}%"
                )
                print(
                    f"  - Population size: {ga_metrics.get('population_size', 'N/A')}"
                )

            return data
        else:
            print(f"❌ Genetic optimize failed: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Genetic optimize error: {e}")
        return None


def compare_algorithms(default_result, genetic_result):
    """Compare results from different algorithms"""
    print("\n🔍 Comparing algorithm results...")

    if not default_result or not genetic_result:
        print("❌ Cannot compare - one or both algorithms failed")
        return

    default_meta = default_result.get("metadata", {})
    genetic_meta = genetic_result.get("metadata", {})

    default_score = default_meta.get("optimization_score", 0)
    genetic_score = genetic_meta.get("optimization_score", 0)

    default_time = default_meta.get("processing_time", 0)
    genetic_time = genetic_meta.get("processing_time", 0)

    print(f"📊 Algorithm Comparison:")
    print(f"  Default Algorithm:")
    print(f"    - Score: {default_score:.2f}")
    print(f"    - Time: {default_time:.2f}s")
    print(f"  Genetic Algorithm:")
    print(f"    - Score: {genetic_score:.2f}")
    print(f"    - Time: {genetic_time:.2f}s")

    if genetic_score > default_score:
        improvement = ((genetic_score - default_score) / default_score) * 100
        print(f"✅ Genetic algorithm improved by {improvement:.1f}%")
    elif genetic_score < default_score:
        decline = ((default_score - genetic_score) / default_score) * 100
        print(f"⚠️  Genetic algorithm scored {decline:.1f}% lower")
    else:
        print(f"🔄 Both algorithms achieved similar scores")


def main():
    """Main test function"""
    print("🚀 Testing Genetic Algorithm Integration")
    print("=" * 50)

    # Test API health
    if not test_api_health():
        print("❌ API is not healthy, stopping tests")
        return

    # Test get algorithms
    if not test_get_algorithms():
        print("❌ Cannot get algorithms info, stopping tests")
        return

    # Test default algorithm
    default_result = test_default_algorithm()

    # Test genetic algorithm
    genetic_result = test_genetic_algorithm()

    # Test dedicated genetic optimization endpoint
    genetic_optimize_result = test_genetic_optimize_endpoint()

    # Compare results
    if default_result and genetic_result:
        compare_algorithms(default_result, genetic_result)

    print("\n🎉 Testing completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
