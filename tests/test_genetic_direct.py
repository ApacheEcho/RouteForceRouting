"""
Direct test of genetic algorithm edge case
Tests the genetic algorithm directly without HTTP layer
"""

import pytest
from app.optimization.genetic_algorithm import GeneticAlgorithm, GeneticConfig


def test_genetic_algorithm_population_one_direct():
    """Edge case: Genetic algorithm with population size 1 should not fail or hang."""
    # Test data
    stores = [
        {"id": "1", "lat": 37.7749, "lon": -122.4194, "name": "Stop 1"},
        {"id": "2", "lat": 37.7849, "lon": -122.4094, "name": "Stop 2"},
    ]
    
    # Create genetic config with population size 1
    config = GeneticConfig(
        population_size=1,
        generations=50,
        mutation_rate=0.02,
        crossover_rate=0.8,
        elite_size=1,
        tournament_size=1,
    )
    
    # Create genetic algorithm instance
    ga = GeneticAlgorithm(config)
    
    # This should not hang or fail
    optimized_route, metrics = ga.optimize(stores)
    
    # Verify results
    assert optimized_route is not None
    assert len(optimized_route) == 2
    assert metrics is not None
    assert metrics["algorithm"] == "genetic"
    assert metrics["population_size"] == 1
    assert metrics["generations"] >= 1  # Should have run at least one generation
    
    print(f"✅ Genetic algorithm with population_size=1 completed successfully!")
    print(f"📊 Metrics: {metrics}")


def test_genetic_algorithm_zero_population():
    """Edge case: Genetic algorithm with population size 0 should handle gracefully."""
    stores = [
        {"id": "1", "lat": 37.7749, "lon": -122.4194, "name": "Stop 1"},
        {"id": "2", "lat": 37.7849, "lon": -122.4094, "name": "Stop 2"},
    ]
    
    config = GeneticConfig(population_size=0)
    ga = GeneticAlgorithm(config)
    
    # This should handle the edge case gracefully
    optimized_route, metrics = ga.optimize(stores)
    
    assert optimized_route is not None
    assert metrics is not None
    assert metrics["algorithm"] == "genetic"


def test_genetic_algorithm_empty_stores():
    """Edge case: Genetic algorithm with empty stores list."""
    stores = []
    
    config = GeneticConfig(population_size=1)
    ga = GeneticAlgorithm(config)
    
    optimized_route, metrics = ga.optimize(stores)
    
    assert optimized_route == []
    assert metrics["generations"] == 0


def test_genetic_algorithm_single_store():
    """Edge case: Genetic algorithm with single store."""
    stores = [{"id": "1", "lat": 37.7749, "lon": -122.4194, "name": "Stop 1"}]
    
    config = GeneticConfig(population_size=1)
    ga = GeneticAlgorithm(config)
    
    optimized_route, metrics = ga.optimize(stores)
    
    assert optimized_route == stores
    assert metrics["generations"] == 0
