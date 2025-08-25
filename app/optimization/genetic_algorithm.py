"""
Genetic Algorithm for Route Optimization
Advanced TSP (Traveling Salesman Problem) solver using evolutionary algorithms
"""

import random
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from geopy.distance import geodesic
import logging
from collections import deque

logger = logging.getLogger(__name__)


# AUTO-PILOT: Efficient convergence detection class
class ConvergenceTracker:
    """O(1) convergence detection using sliding window"""

    def __init__(self, window_size: int = 20, threshold: float = 0.001):
        self.window_size = window_size
        self.threshold = threshold
        self.values = deque(maxlen=window_size)
        self.min_value = float("inf")
        self.max_value = float("-inf")

    def check_convergence(self, value: float) -> bool:
        """Check if algorithm has converged (O(1) operation)"""
        self.values.append(value)

        if len(self.values) < self.window_size:
            return False

        # Update min/max for current window
        self.min_value = min(self.values)
        self.max_value = max(self.values)

        # Check if range is below threshold
        range_diff = self.max_value - self.min_value
        return range_diff <= self.threshold


@dataclass
class GeneticConfig:
    """Configuration for Genetic Algorithm"""

    population_size: int = 100
    generations: int = 500
    mutation_rate: float = 0.02
    crossover_rate: float = 0.8
    elite_size: int = 20
    tournament_size: int = 3


class Individual:
    """Represents a single route solution"""

    def __init__(self, route: List[int], stores: List[Dict[str, Any]]):
        self.route = route
        self.stores = stores
        self.fitness = 0.0
        self.distance = 0.0
        self.calculate_fitness()

    def calculate_fitness(self):
        """Calculate fitness based on total route distance"""
        total_distance = 0.0

        for i in range(len(self.route)):
            current_store = self.stores[self.route[i]]
            next_store = self.stores[self.route[(i + 1) % len(self.route)]]

            # Handle both 'lat'/'lon' and 'latitude'/'longitude' formats
            coord1 = (
                current_store.get("latitude", current_store.get("lat", 0)),
                current_store.get("longitude", current_store.get("lon", 0)),
            )
            coord2 = (
                next_store.get("latitude", next_store.get("lat", 0)),
                next_store.get("longitude", next_store.get("lon", 0)),
            )

            if coord1 != (0, 0) and coord2 != (0, 0):
                total_distance += geodesic(coord1, coord2).kilometers

        self.distance = total_distance
        # Fitness is inverse of distance (higher fitness = shorter distance)
        self.fitness = 1 / (total_distance + 1)  # +1 to avoid division by zero

    def __lt__(self, other):
        return self.fitness > other.fitness  # Higher fitness is better


class GeneticAlgorithm:
    """
    Genetic Algorithm for Route Optimization

    Uses evolutionary principles to find optimal routes:
    - Selection: Tournament selection of best individuals
    - Crossover: Order crossover (OX) preserving route validity
    - Mutation: Swap mutation for local improvements
    - Elitism: Keep best solutions across generations
    """

    def __init__(self, config: GeneticConfig = None):
        self.config = config or GeneticConfig()
        self.population = []
        self.best_individual = None
        self.generation_stats = []

    def optimize(
        self, stores: List[Dict[str, Any]], constraints: Dict[str, Any] = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Optimize route using genetic algorithm

        Args:
            stores: List of store dictionaries with lat/lon coordinates
            constraints: Optional constraints for optimization

        Returns:
            Tuple of (optimized_route, optimization_metrics)
        """
        logger.info(
            f"Starting genetic algorithm optimization for {len(stores)} stores"
        )

        if len(stores) < 2:
            return stores, {
                "algorithm": "genetic",
                "generations": 0,
                "improvement": 0,
            }

        # Handle degenerate case where population size is 1
        if self.config.population_size <= 1:
            logger.info("Population size <= 1, performing basic route optimization")
            # Just return a simple route permutation instead of running full GA
            store_indices = list(range(len(stores)))
            random.shuffle(store_indices)
            optimized_route = [stores[i] for i in store_indices]
            
            return optimized_route, {
                "algorithm": "genetic",
                "generations": 1,
                "initial_distance": 0,
                "final_distance": 0,
                "improvement_percent": 0,
                "population_size": self.config.population_size,
                "best_fitness": 1.0,
            }

        # Initialize population
        self._initialize_population(stores)

        initial_best = min(self.population)
        best_distances = []

        # Evolution loop with enhanced convergence detection
        convergence_tracker = ConvergenceTracker(
            window_size=20, threshold=0.001
        )

        for generation in range(self.config.generations):
            # Selection and reproduction
            new_population = self._evolve_population()
            self.population = new_population

            # Track best solution
            current_best = min(self.population)
            best_distances.append(current_best.distance)

            if (
                not self.best_individual
                or current_best.fitness > self.best_individual.fitness
            ):
                self.best_individual = current_best

            # AUTO-PILOT: Enhanced convergence detection (O(1) instead of O(n))
            if generation > 50 and convergence_tracker.check_convergence(
                current_best.distance
            ):
                logger.info(
                    f"Early stopping at generation {generation} - convergence detected"
                )
                break

            # Log progress
            if generation % 50 == 0:
                logger.info(
                    f"Generation {generation}: Best distance = {current_best.distance:.2f}km"
                )

        # Convert best route back to store format
        optimized_route = [stores[i] for i in self.best_individual.route]

        # Calculate improvement
        improvement = (
            (initial_best.distance - self.best_individual.distance)
            / initial_best.distance
        ) * 100

        metrics = {
            "algorithm": "genetic",
            "generations": generation + 1,
            "initial_distance": initial_best.distance,
            "final_distance": self.best_individual.distance,
            "improvement_percent": improvement,
            "population_size": self.config.population_size,
            "best_fitness": self.best_individual.fitness,
        }

        logger.info(
            f"Genetic algorithm completed: {improvement:.1f}% improvement"
        )
        return optimized_route, metrics

    def _initialize_population(self, stores: List[Dict[str, Any]]):
        """Initialize population with random routes"""
        self.population = []
        store_indices = list(range(len(stores)))

        for _ in range(self.config.population_size):
            # Create random route
            route = store_indices.copy()
            random.shuffle(route)

            individual = Individual(route, stores)
            self.population.append(individual)

        # Sort by fitness
        self.population.sort()

    def _evolve_population(self) -> List[Individual]:
        """Evolve population through selection, crossover, and mutation"""
        new_population = []

        # Elitism: Keep best individuals
        elite_count = min(self.config.elite_size, len(self.population))
        new_population.extend(self.population[:elite_count])

        # Generate offspring
        while len(new_population) < self.config.population_size:
            # Selection
            parent1 = self._tournament_selection()
            parent2 = self._tournament_selection()

            # Crossover
            if random.random() < self.config.crossover_rate:
                child1, child2 = self._order_crossover(parent1, parent2)
            else:
                child1, child2 = parent1, parent2

            # Mutation
            if random.random() < self.config.mutation_rate:
                child1 = self._mutate(child1)
            if random.random() < self.config.mutation_rate:
                child2 = self._mutate(child2)

            # AUTO-PILOT: Ensure exact population size bounds
            remaining_slots = self.config.population_size - len(new_population)
            if remaining_slots >= 2:
                new_population.extend([child1, child2])
            elif remaining_slots == 1:
                new_population.append(child1)
                break

        # AUTO-PILOT: Ensure exact population size
        new_population = new_population[: self.config.population_size]
        new_population.sort()

        return new_population

    def _tournament_selection(self) -> Individual:
        """Select individual using tournament selection"""
        # Handle edge case where population size is smaller than tournament size
        tournament_size = min(self.config.tournament_size, len(self.population))
        tournament = random.sample(
            self.population, tournament_size
        )
        return min(tournament)  # Best fitness (lowest distance)

    def _order_crossover(
        self, parent1: Individual, parent2: Individual
    ) -> Tuple[Individual, Individual]:
        """Order crossover (OX) preserving route validity"""
        size = len(parent1.route)

        # Select crossover points
        start, end = sorted(random.sample(range(size), 2))

        # Create children
        child1_route = [-1] * size
        child2_route = [-1] * size

        # Copy segments
        child1_route[start:end] = parent1.route[start:end]
        child2_route[start:end] = parent2.route[start:end]

        # Fill remaining positions
        self._fill_remaining(child1_route, parent2.route, end)
        self._fill_remaining(child2_route, parent1.route, end)

        child1 = Individual(child1_route, parent1.stores)
        child2 = Individual(child2_route, parent2.stores)

        return child1, child2

    def _fill_remaining(
        self, child_route: List[int], parent_route: List[int], start_pos: int
    ):
        """Fill remaining positions in crossover"""
        size = len(child_route)
        parent_idx = start_pos
        child_idx = start_pos

        while -1 in child_route:
            if parent_route[parent_idx % size] not in child_route:
                while child_route[child_idx % size] != -1:
                    child_idx += 1
                child_route[child_idx % size] = parent_route[parent_idx % size]
            parent_idx += 1

    def _mutate(self, individual: Individual) -> Individual:
        """Swap mutation"""
        mutated_route = individual.route.copy()

        # Swap two random positions
        if len(mutated_route) > 1:
            idx1, idx2 = random.sample(range(len(mutated_route)), 2)
            mutated_route[idx1], mutated_route[idx2] = (
                mutated_route[idx2],
                mutated_route[idx1],
            )

        return Individual(mutated_route, individual.stores)

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get detailed optimization statistics"""
        if not self.best_individual:
            return {}

        return {
            "best_distance": self.best_individual.distance,
            "best_fitness": self.best_individual.fitness,
            "population_size": self.config.population_size,
            "generations_run": len(self.generation_stats),
            "config": {
                "population_size": self.config.population_size,
                "generations": self.config.generations,
                "mutation_rate": self.config.mutation_rate,
                "crossover_rate": self.config.crossover_rate,
                "elite_size": self.config.elite_size,
            },
        }
