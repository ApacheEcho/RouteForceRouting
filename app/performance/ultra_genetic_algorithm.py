"""
Enhanced Genetic Algorithm Performance Optimization - Beast Mode
Ultra-high performance genetic algorithm with advanced optimizations
"""

import random
import numpy as np
from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
from geopy.distance import geodesic
import logging
import time
from collections import deque
import math

# Optional high-performance imports
try:
    import cython

    CYTHON_AVAILABLE = True
except ImportError:
    CYTHON_AVAILABLE = False

try:
    from numba import jit, prange

    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

    # Create dummy jit decorator
    def jit(*args, **kwargs):
        def decorator(func):
            return func

        return decorator if args else jit

    prange = range

logger = logging.getLogger(__name__)


@jit(nopython=True)
def calculate_distance_matrix(coordinates: np.ndarray) -> np.ndarray:
    """Calculate distance matrix using Numba for speed"""
    n = coordinates.shape[0]
    distances = np.zeros((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            # Haversine distance calculation
            lat1, lon1 = coordinates[i]
            lat2, lon2 = coordinates[j]

            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)

            a = (
                math.sin(dlat / 2) ** 2
                + math.cos(lat1_rad)
                * math.cos(lat2_rad)
                * math.sin(dlon / 2) ** 2
            )
            c = 2 * math.asin(math.sqrt(a))
            distance = 6371 * c  # Earth radius in km

            distances[i][j] = distance
            distances[j][i] = distance

    return distances


@jit(nopython=True)
def calculate_route_distance(
    route: np.ndarray, distance_matrix: np.ndarray
) -> float:
    """Calculate total route distance using precomputed matrix"""
    total_distance = 0.0
    n = len(route)

    for i in range(n):
        current = route[i]
        next_store = route[(i + 1) % n]
        total_distance += distance_matrix[current][next_store]

    return total_distance


@jit(nopython=True)
def two_opt_improvement(
    route: np.ndarray, distance_matrix: np.ndarray
) -> Tuple[np.ndarray, bool]:
    """2-opt local search optimization"""
    n = len(route)
    improved = False
    best_route = route.copy()
    best_distance = calculate_route_distance(route, distance_matrix)

    for i in range(n - 1):
        for j in range(i + 2, n):
            if j == n - 1 and i == 0:
                continue

            # Create new route with reversed segment
            new_route = route.copy()
            new_route[i + 1 : j + 1] = new_route[i + 1 : j + 1][::-1]

            new_distance = calculate_route_distance(new_route, distance_matrix)

            if new_distance < best_distance:
                best_route = new_route.copy()
                best_distance = new_distance
                improved = True

    return best_route, improved


@dataclass
class OptimizedGeneticConfig:
    """Enhanced configuration for optimized genetic algorithm"""

    population_size: int = 200
    generations: int = 1000
    mutation_rate: float = 0.02
    crossover_rate: float = 0.9
    elite_size: int = 30
    tournament_size: int = 5

    # Advanced optimization parameters
    use_2opt: bool = True
    use_multiprocessing: bool = True
    max_workers: int = None  # None = use all cores
    adaptive_parameters: bool = True
    convergence_window: int = 50
    convergence_threshold: float = 0.001

    # Performance parameters
    batch_size: int = 10
    cache_distances: bool = True
    use_numba: bool = NUMBA_AVAILABLE  # Only use if available
    local_search_probability: float = 0.1


class OptimizedIndividual:
    """High-performance individual representation"""

    def __init__(self, route: np.ndarray, distance_matrix: np.ndarray):
        self.route = route
        self.distance_matrix = distance_matrix
        self.fitness = 0.0
        self.distance = 0.0
        self.age = 0  # For diversity management
        self.calculate_fitness()

    def calculate_fitness(self):
        """Calculate fitness using precomputed distance matrix"""
        self.distance = calculate_route_distance(
            self.route, self.distance_matrix
        )
        self.fitness = 1 / (self.distance + 1)

    def local_search(self) -> bool:
        """Apply 2-opt local search"""
        improved_route, improved = two_opt_improvement(
            self.route, self.distance_matrix
        )

        if improved:
            self.route = improved_route
            self.calculate_fitness()
            return True

        return False

    def __lt__(self, other):
        return self.fitness > other.fitness


class AdaptiveParameterManager:
    """Manages adaptive parameter adjustment during evolution"""

    def __init__(self, config: OptimizedGeneticConfig):
        self.config = config
        self.initial_mutation_rate = config.mutation_rate
        self.initial_crossover_rate = config.crossover_rate
        self.diversity_history = deque(maxlen=20)

    def update_parameters(
        self, generation: int, population: List[OptimizedIndividual]
    ) -> None:
        """Dynamically adjust parameters based on population state"""
        if not self.config.adaptive_parameters:
            return

        # Calculate population diversity
        diversity = self._calculate_diversity(population)
        self.diversity_history.append(diversity)

        # Adjust mutation rate based on diversity
        if diversity < 0.1:  # Low diversity
            self.config.mutation_rate = min(
                0.1, self.initial_mutation_rate * 2
            )
        elif diversity > 0.5:  # High diversity
            self.config.mutation_rate = max(
                0.001, self.initial_mutation_rate * 0.5
            )
        else:
            self.config.mutation_rate = self.initial_mutation_rate

        # Adjust crossover rate based on generation
        progress = generation / 1000  # Assume max 1000 generations
        self.config.crossover_rate = self.initial_crossover_rate * (
            1 - progress * 0.2
        )

    def _calculate_diversity(
        self, population: List[OptimizedIndividual]
    ) -> float:
        """Calculate population diversity"""
        if len(population) < 2:
            return 1.0

        total_distance_variance = 0.0
        mean_distance = sum(ind.distance for ind in population) / len(
            population
        )

        for individual in population:
            total_distance_variance += (
                individual.distance - mean_distance
            ) ** 2

        variance = total_distance_variance / len(population)
        return min(1.0, variance / mean_distance if mean_distance > 0 else 0)


class UltraGeneticAlgorithm:
    """Ultra-high performance genetic algorithm with all optimizations"""

    def __init__(self, config: OptimizedGeneticConfig = None):
        self.config = config or OptimizedGeneticConfig()
        self.population = []
        self.best_individual = None
        self.distance_matrix = None
        self.coordinates = None

        # Performance tracking
        self.generation_stats = []
        self.convergence_tracker = deque(maxlen=self.config.convergence_window)
        self.parameter_manager = AdaptiveParameterManager(self.config)

        # Multiprocessing setup
        if self.config.use_multiprocessing and self.config.max_workers is None:
            self.config.max_workers = min(multiprocessing.cpu_count(), 8)

    def optimize(
        self, stores: List[Dict[str, Any]], constraints: Dict[str, Any] = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Ultra-optimized route optimization"""
        start_time = time.time()

        logger.info(
            f"Starting ultra genetic algorithm for {len(stores)} stores"
        )

        if len(stores) < 2:
            return stores, {"algorithm": "ultra_genetic", "generations": 0}

        # Prepare coordinates and distance matrix
        self._prepare_data(stores)

        # Initialize population
        self._initialize_population()

        initial_best = min(self.population)
        best_distances = []

        # Evolution loop
        for generation in range(self.config.generations):
            generation_start = time.time()

            # Adaptive parameter management
            self.parameter_manager.update_parameters(
                generation, self.population
            )

            # Evolve population
            if self.config.use_multiprocessing and len(self.population) > 20:
                new_population = self._parallel_evolution()
            else:
                new_population = self._sequential_evolution()

            self.population = new_population

            # Track best solution
            current_best = min(self.population)
            best_distances.append(current_best.distance)

            if (
                not self.best_individual
                or current_best.fitness > self.best_individual.fitness
            ):
                self.best_individual = current_best

            # Convergence checking
            self.convergence_tracker.append(current_best.distance)

            if self._check_convergence() and generation > 100:
                logger.info(f"Convergence reached at generation {generation}")
                break

            # Optional local search on best individuals
            if (
                self.config.use_2opt
                and random.random() < self.config.local_search_probability
            ):
                self._apply_local_search()

            # Statistics
            generation_time = time.time() - generation_start
            self.generation_stats.append(
                {
                    "generation": generation,
                    "best_distance": current_best.distance,
                    "avg_distance": sum(
                        ind.distance for ind in self.population
                    )
                    / len(self.population),
                    "time": generation_time,
                    "mutation_rate": self.config.mutation_rate,
                }
            )

            if generation % 50 == 0:
                logger.info(
                    f"Gen {generation}: Best={current_best.distance:.2f}km, "
                    f"Time={generation_time:.3f}s"
                )

        # Convert result
        optimized_route = [stores[i] for i in self.best_individual.route]

        total_time = time.time() - start_time
        improvement = (
            (initial_best.distance - self.best_individual.distance)
            / initial_best.distance
        ) * 100

        metrics = {
            "algorithm": "ultra_genetic",
            "generations": len(self.generation_stats),
            "total_time": total_time,
            "initial_distance": initial_best.distance,
            "final_distance": self.best_individual.distance,
            "improvement_percent": improvement,
            "population_size": self.config.population_size,
            "used_multiprocessing": self.config.use_multiprocessing,
            "used_2opt": self.config.use_2opt,
            "convergence_generations": len(self.generation_stats),
        }

        logger.info(
            f"Ultra genetic completed: {improvement:.1f}% improvement in {total_time:.2f}s"
        )
        return optimized_route, metrics

    def _prepare_data(self, stores: List[Dict[str, Any]]) -> None:
        """Prepare coordinate data and distance matrix"""
        # Extract coordinates
        coordinates = []
        for store in stores:
            lat = store.get("latitude", store.get("lat", 0))
            lon = store.get("longitude", store.get("lon", 0))
            coordinates.append([lat, lon])

        self.coordinates = np.array(coordinates)

        # Calculate distance matrix if caching enabled
        if self.config.cache_distances:
            if self.config.use_numba:
                self.distance_matrix = calculate_distance_matrix(
                    self.coordinates
                )
            else:
                self.distance_matrix = (
                    self._calculate_distance_matrix_fallback()
                )

    def _calculate_distance_matrix_fallback(self) -> np.ndarray:
        """Fallback distance matrix calculation"""
        n = len(self.coordinates)
        distances = np.zeros((n, n))

        for i in range(n):
            for j in range(i + 1, n):
                coord1 = tuple(self.coordinates[i])
                coord2 = tuple(self.coordinates[j])
                distance = geodesic(coord1, coord2).kilometers
                distances[i][j] = distance
                distances[j][i] = distance

        return distances

    def _initialize_population(self) -> None:
        """Initialize optimized population"""
        self.population = []
        n_stores = len(self.coordinates)

        # Create diverse initial population
        for i in range(self.config.population_size):
            if i == 0:
                # Start with sorted route
                route = np.array(range(n_stores))
            elif i < 10:
                # Some nearest neighbor heuristic routes
                route = self._nearest_neighbor_route()
            else:
                # Random routes
                route = np.random.permutation(n_stores)

            individual = OptimizedIndividual(route, self.distance_matrix)
            self.population.append(individual)

        # Sort by fitness
        self.population.sort()

    def _nearest_neighbor_route(self) -> np.ndarray:
        """Generate route using nearest neighbor heuristic"""
        n = len(self.coordinates)
        route = [0]  # Start from first store
        unvisited = set(range(1, n))

        current = 0
        while unvisited:
            nearest = min(
                unvisited, key=lambda x: self.distance_matrix[current][x]
            )
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest

        return np.array(route)

    def _parallel_evolution(self) -> List[OptimizedIndividual]:
        """Parallel evolution using multiple processes"""
        new_population = []

        # Keep elite
        elite_size = min(self.config.elite_size, len(self.population))
        new_population.extend(self.population[:elite_size])

        # Parallel offspring generation
        offspring_needed = self.config.population_size - elite_size
        batch_size = max(1, offspring_needed // self.config.max_workers)

        with ThreadPoolExecutor(
            max_workers=self.config.max_workers
        ) as executor:
            futures = []

            for _ in range(self.config.max_workers):
                future = executor.submit(
                    self._generate_offspring_batch, batch_size
                )
                futures.append(future)

            for future in as_completed(futures):
                batch_offspring = future.result()
                new_population.extend(batch_offspring)

                if len(new_population) >= self.config.population_size:
                    break

        # Trim to exact size and sort
        new_population = new_population[: self.config.population_size]
        new_population.sort()

        return new_population

    def _sequential_evolution(self) -> List[OptimizedIndividual]:
        """Sequential evolution for smaller populations"""
        new_population = []

        # Elite individuals
        elite_size = min(self.config.elite_size, len(self.population))
        new_population.extend(self.population[:elite_size])

        # Generate offspring
        while len(new_population) < self.config.population_size:
            parent1 = self._tournament_selection()
            parent2 = self._tournament_selection()

            if random.random() < self.config.crossover_rate:
                child1, child2 = self._order_crossover(parent1, parent2)
            else:
                child1, child2 = parent1, parent2

            if random.random() < self.config.mutation_rate:
                child1 = self._mutate(child1)
            if random.random() < self.config.mutation_rate:
                child2 = self._mutate(child2)

            new_population.extend([child1, child2])

        new_population = new_population[: self.config.population_size]
        new_population.sort()

        return new_population

    def _generate_offspring_batch(
        self, batch_size: int
    ) -> List[OptimizedIndividual]:
        """Generate batch of offspring for parallel processing"""
        offspring = []

        for _ in range(batch_size):
            parent1 = self._tournament_selection()
            parent2 = self._tournament_selection()

            if random.random() < self.config.crossover_rate:
                child1, child2 = self._order_crossover(parent1, parent2)
            else:
                child1, child2 = parent1, parent2

            if random.random() < self.config.mutation_rate:
                child1 = self._mutate(child1)
            if random.random() < self.config.mutation_rate:
                child2 = self._mutate(child2)

            offspring.extend([child1, child2])

        return offspring

    def _tournament_selection(self) -> OptimizedIndividual:
        """Tournament selection"""
        tournament = random.sample(
            self.population, self.config.tournament_size
        )
        return min(tournament)

    def _order_crossover(
        self, parent1: OptimizedIndividual, parent2: OptimizedIndividual
    ) -> Tuple[OptimizedIndividual, OptimizedIndividual]:
        """Optimized order crossover"""
        size = len(parent1.route)
        start, end = sorted(random.sample(range(size), 2))

        child1_route = np.full(size, -1)
        child2_route = np.full(size, -1)

        child1_route[start:end] = parent1.route[start:end]
        child2_route[start:end] = parent2.route[start:end]

        self._fill_remaining_optimized(child1_route, parent2.route, end)
        self._fill_remaining_optimized(child2_route, parent1.route, end)

        child1 = OptimizedIndividual(child1_route, self.distance_matrix)
        child2 = OptimizedIndividual(child2_route, self.distance_matrix)

        return child1, child2

    def _fill_remaining_optimized(
        self, child_route: np.ndarray, parent_route: np.ndarray, start_pos: int
    ) -> None:
        """Optimized remaining position filling"""
        size = len(child_route)
        parent_idx = start_pos

        for pos in range(size):
            if child_route[pos] == -1:
                while parent_route[parent_idx % size] in child_route:
                    parent_idx += 1
                child_route[pos] = parent_route[parent_idx % size]
                parent_idx += 1

    def _mutate(self, individual: OptimizedIndividual) -> OptimizedIndividual:
        """Enhanced mutation with multiple strategies"""
        mutated_route = individual.route.copy()

        mutation_type = random.choice(["swap", "reverse", "insert"])

        if mutation_type == "swap" and len(mutated_route) > 1:
            idx1, idx2 = random.sample(range(len(mutated_route)), 2)
            mutated_route[idx1], mutated_route[idx2] = (
                mutated_route[idx2],
                mutated_route[idx1],
            )

        elif mutation_type == "reverse" and len(mutated_route) > 2:
            start, end = sorted(random.sample(range(len(mutated_route)), 2))
            mutated_route[start:end] = mutated_route[start:end][::-1]

        elif mutation_type == "insert" and len(mutated_route) > 2:
            idx1 = random.randint(0, len(mutated_route) - 1)
            idx2 = random.randint(0, len(mutated_route) - 1)

            gene = mutated_route[idx1]
            mutated_route = np.delete(mutated_route, idx1)
            mutated_route = np.insert(mutated_route, idx2, gene)

        return OptimizedIndividual(mutated_route, self.distance_matrix)

    def _apply_local_search(self) -> None:
        """Apply local search to best individuals"""
        elite_count = min(10, len(self.population))

        for i in range(elite_count):
            improved = self.population[i].local_search()
            if improved:
                logger.debug(f"Local search improved individual {i}")

        # Re-sort if improvements were made
        self.population.sort()

    def _check_convergence(self) -> bool:
        """Check for convergence"""
        if len(self.convergence_tracker) < self.config.convergence_window:
            return False

        distances = list(self.convergence_tracker)
        min_dist = min(distances)
        max_dist = max(distances)

        return (
            max_dist - min_dist
        ) / max_dist < self.config.convergence_threshold

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        if not self.generation_stats:
            return {}

        total_time = sum(stat["time"] for stat in self.generation_stats)
        avg_generation_time = total_time / len(self.generation_stats)

        return {
            "total_generations": len(self.generation_stats),
            "total_time": total_time,
            "avg_generation_time": avg_generation_time,
            "final_best_distance": (
                self.best_individual.distance if self.best_individual else 0
            ),
            "used_optimizations": {
                "numba": self.config.use_numba,
                "multiprocessing": self.config.use_multiprocessing,
                "2opt": self.config.use_2opt,
                "distance_caching": self.config.cache_distances,
                "adaptive_parameters": self.config.adaptive_parameters,
            },
            "performance_score": self._calculate_performance_score(),
        }

    def _calculate_performance_score(self) -> float:
        """Calculate overall performance score"""
        if not self.generation_stats:
            return 0.0

        # Base score from improvement
        initial_distance = self.generation_stats[0]["best_distance"]
        final_distance = self.generation_stats[-1]["best_distance"]
        improvement_score = (
            (initial_distance - final_distance) / initial_distance
        ) * 100

        # Time efficiency bonus
        avg_time = sum(stat["time"] for stat in self.generation_stats) / len(
            self.generation_stats
        )
        time_bonus = max(0, 10 - avg_time * 10)  # Bonus for fast generations

        # Convergence bonus
        convergence_bonus = 10 if self._check_convergence() else 0

        return improvement_score + time_bonus + convergence_bonus
