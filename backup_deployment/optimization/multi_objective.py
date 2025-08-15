"""
Multi-Objective Optimization for Route Planning
Implements NSGA-II (Non-dominated Sorting Genetic Algorithm II) for Pareto-optimal solutions
"""

import random
import math
import time
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class MultiObjectiveConfig:
    """Configuration for Multi-Objective Optimization"""

    population_size: int = 100
    generations: int = 200
    mutation_rate: float = 0.1
    crossover_rate: float = 0.9
    tournament_size: int = 2
    objectives: List[str] = (
        None  # ['distance', 'time', 'priority', 'fuel_cost']
    )

    def __post_init__(self):
        if self.objectives is None:
            self.objectives = ["distance", "time"]

        if self.population_size < 10:
            raise ValueError("Population size must be at least 10")
        if not 0 < self.mutation_rate < 1:
            raise ValueError("Mutation rate must be between 0 and 1")
        if not 0 < self.crossover_rate < 1:
            raise ValueError("Crossover rate must be between 0 and 1")


@dataclass
class MultiObjectiveMetrics:
    """Metrics for multi-objective optimization"""

    algorithm_used: str = "multi_objective"
    pareto_front_size: int = 0
    hypervolume: float = 0.0
    convergence_metric: float = 0.0
    diversity_metric: float = 0.0
    processing_time: float = 0.0
    total_generations: int = 0
    dominated_solutions: int = 0
    objectives_optimized: List[str] = None
    best_compromise_solution: Dict[str, Any] = None


class MultiObjectiveOptimizer:
    """
    Multi-Objective optimizer using NSGA-II algorithm

    Optimizes multiple objectives simultaneously to find Pareto-optimal solutions
    for route planning problems.
    """

    def __init__(self, config: MultiObjectiveConfig):
        """
        Initialize the Multi-Objective optimizer

        Args:
            config: Configuration object containing optimization parameters
        """
        self.config = config
        self.metrics = MultiObjectiveMetrics()
        self.distance_matrix = None
        self.stores = None

        # Objective functions
        self.objective_functions = {
            "distance": self._calculate_total_distance,
            "time": self._calculate_total_time,
            "priority": self._calculate_priority_score,
            "fuel_cost": self._calculate_fuel_cost,
            "delivery_windows": self._calculate_time_window_violations,
            "vehicle_capacity": self._calculate_capacity_violations,
        }

        logger.info(
            f"Initialized Multi-Objective optimizer with objectives: {config.objectives}"
        )

    def optimize(
        self,
        stores: List[Dict[str, Any]],
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Optimize route using multi-objective approach

        Args:
            stores: List of store dictionaries
            constraints: Optional constraints dictionary

        Returns:
            Tuple of (best_compromise_route, metrics_dict)
        """
        start_time = time.time()

        try:
            if len(stores) < 2:
                raise ValueError("At least 2 stores required for optimization")

            self.stores = stores
            self.distance_matrix = self._create_distance_matrix(stores)

            # Initialize population
            population = self._initialize_population()

            # Evolutionary loop
            for generation in range(self.config.generations):
                # Evaluate objectives for all individuals
                objective_values = self._evaluate_population(population)

                # Non-dominated sorting and crowding distance
                fronts = self._non_dominated_sort(objective_values)
                crowding_distances = self._calculate_crowding_distance(
                    fronts, objective_values
                )

                # Selection, crossover, and mutation
                new_population = self._evolutionary_operators(
                    population, fronts, crowding_distances
                )
                population = new_population

                # Log progress
                if generation % 20 == 0:
                    logger.debug(
                        f"Generation {generation}: Pareto front size = {len(fronts[0])}"
                    )

            # Final evaluation and Pareto front extraction
            final_objectives = self._evaluate_population(population)
            final_fronts = self._non_dominated_sort(final_objectives)
            pareto_front = final_fronts[0]

            # Select best compromise solution
            best_compromise_idx = self._select_best_compromise(
                pareto_front, final_objectives
            )
            best_route_indices = population[best_compromise_idx]
            best_route = [stores[i] for i in best_route_indices]

            # Calculate metrics
            processing_time = time.time() - start_time
            metrics_dict = self._calculate_metrics(
                pareto_front,
                final_objectives,
                processing_time,
                best_compromise_idx,
            )

            logger.info(
                f"Multi-objective optimization completed in {processing_time:.4f}s"
            )
            logger.info(f"Pareto front size: {len(pareto_front)}")

            return best_route, metrics_dict

        except Exception as e:
            logger.error(f"Error in multi-objective optimization: {str(e)}")
            processing_time = time.time() - start_time
            return stores, {
                "algorithm": "multi_objective",
                "error": str(e),
                "processing_time": processing_time,
            }

    def _initialize_population(self) -> List[List[int]]:
        """Initialize random population of route permutations"""
        population = []
        n_stores = len(self.stores)

        for _ in range(self.config.population_size):
            route = list(range(n_stores))
            random.shuffle(route)
            population.append(route)

        return population

    def _evaluate_population(
        self, population: List[List[int]]
    ) -> List[List[float]]:
        """Evaluate all objectives for each individual in population"""
        objective_values = []

        for individual in population:
            values = []
            for objective in self.config.objectives:
                if objective in self.objective_functions:
                    value = self.objective_functions[objective](individual)
                    values.append(value)
                else:
                    logger.warning(f"Unknown objective: {objective}")
                    values.append(0.0)
            objective_values.append(values)

        return objective_values

    def _non_dominated_sort(
        self, objective_values: List[List[float]]
    ) -> List[List[int]]:
        """Perform non-dominated sorting (NSGA-II)"""
        n = len(objective_values)
        dominated_count = [0] * n
        dominates = [[] for _ in range(n)]
        fronts = [[] for _ in range(n)]

        # Find domination relationships
        for i in range(n):
            for j in range(n):
                if i != j:
                    if self._dominates(
                        objective_values[i], objective_values[j]
                    ):
                        dominates[i].append(j)
                    elif self._dominates(
                        objective_values[j], objective_values[i]
                    ):
                        dominated_count[i] += 1

        # First front (non-dominated solutions)
        current_front = 0
        for i in range(n):
            if dominated_count[i] == 0:
                fronts[current_front].append(i)

        # Subsequent fronts
        while fronts[current_front]:
            next_front = []
            for i in fronts[current_front]:
                for j in dominates[i]:
                    dominated_count[j] -= 1
                    if dominated_count[j] == 0:
                        next_front.append(j)
            current_front += 1
            fronts[current_front] = next_front

        # Return only non-empty fronts
        return [front for front in fronts if front]

    def _dominates(self, obj1: List[float], obj2: List[float]) -> bool:
        """Check if obj1 dominates obj2 (minimization assumed)"""
        better_in_at_least_one = False
        for i in range(len(obj1)):
            if obj1[i] > obj2[i]:  # obj1 is worse in this objective
                return False
            if obj1[i] < obj2[i]:  # obj1 is better in this objective
                better_in_at_least_one = True
        return better_in_at_least_one

    def _calculate_crowding_distance(
        self, fronts: List[List[int]], objective_values: List[List[float]]
    ) -> List[float]:
        """Calculate crowding distance for diversity preservation"""
        n = len(objective_values)
        distances = [0.0] * n

        for front in fronts:
            if len(front) <= 2:
                for idx in front:
                    distances[idx] = float("inf")
                continue

            # For each objective
            for obj_idx in range(len(self.config.objectives)):
                # Sort by objective value
                front_sorted = sorted(
                    front, key=lambda x: objective_values[x][obj_idx]
                )

                # Set boundary points to infinity
                distances[front_sorted[0]] = float("inf")
                distances[front_sorted[-1]] = float("inf")

                # Calculate range
                obj_range = (
                    objective_values[front_sorted[-1]][obj_idx]
                    - objective_values[front_sorted[0]][obj_idx]
                )
                if obj_range == 0:
                    continue

                # Calculate crowding distance
                for i in range(1, len(front_sorted) - 1):
                    distances[front_sorted[i]] += (
                        objective_values[front_sorted[i + 1]][obj_idx]
                        - objective_values[front_sorted[i - 1]][obj_idx]
                    ) / obj_range

        return distances

    def _evolutionary_operators(
        self,
        population: List[List[int]],
        fronts: List[List[int]],
        crowding_distances: List[float],
    ) -> List[List[int]]:
        """Apply selection, crossover, and mutation"""
        new_population = []

        # Elitism: keep the best solutions
        elite_size = self.config.population_size // 4
        elite_indices = self._select_elite(
            fronts, crowding_distances, elite_size
        )
        for idx in elite_indices:
            new_population.append(population[idx][:])

        # Generate offspring through crossover and mutation
        while len(new_population) < self.config.population_size:
            # Tournament selection
            parent1_idx = self._tournament_selection(
                population, fronts, crowding_distances
            )
            parent2_idx = self._tournament_selection(
                population, fronts, crowding_distances
            )

            # Crossover
            if random.random() < self.config.crossover_rate:
                child1, child2 = self._crossover(
                    population[parent1_idx], population[parent2_idx]
                )
            else:
                child1, child2 = (
                    population[parent1_idx][:],
                    population[parent2_idx][:],
                )

            # Mutation
            if random.random() < self.config.mutation_rate:
                child1 = self._mutate(child1)
            if random.random() < self.config.mutation_rate:
                child2 = self._mutate(child2)

            new_population.extend([child1, child2])

        return new_population[: self.config.population_size]

    def _select_elite(
        self,
        fronts: List[List[int]],
        crowding_distances: List[float],
        elite_size: int,
    ) -> List[int]:
        """Select elite solutions based on front rank and crowding distance"""
        elite = []

        for front in fronts:
            if len(elite) >= elite_size:
                break

            # Sort by crowding distance (descending)
            front_sorted = sorted(
                front, key=lambda x: crowding_distances[x], reverse=True
            )

            remaining = elite_size - len(elite)
            elite.extend(front_sorted[:remaining])

        return elite

    def _tournament_selection(
        self,
        population: List[List[int]],
        fronts: List[List[int]],
        crowding_distances: List[float],
    ) -> int:
        """Tournament selection based on dominance and crowding distance"""
        candidates = random.sample(
            range(len(population)),
            min(self.config.tournament_size, len(population)),
        )

        best_candidate = candidates[0]
        best_front = self._get_front_rank(best_candidate, fronts)

        for candidate in candidates[1:]:
            candidate_front = self._get_front_rank(candidate, fronts)

            if candidate_front < best_front or (
                candidate_front == best_front
                and crowding_distances[candidate]
                > crowding_distances[best_candidate]
            ):
                best_candidate = candidate
                best_front = candidate_front

        return best_candidate

    def _get_front_rank(
        self, individual_idx: int, fronts: List[List[int]]
    ) -> int:
        """Get the front rank of an individual"""
        for rank, front in enumerate(fronts):
            if individual_idx in front:
                return rank
        return len(fronts)

    def _crossover(
        self, parent1: List[int], parent2: List[int]
    ) -> Tuple[List[int], List[int]]:
        """Order crossover (OX) for permutation representation"""
        n = len(parent1)

        # Choose crossover points
        start, end = sorted(random.sample(range(n), 2))

        # Create offspring
        child1 = [-1] * n
        child2 = [-1] * n

        # Copy segments
        child1[start:end] = parent1[start:end]
        child2[start:end] = parent2[start:end]

        # Fill remaining positions
        self._fill_remaining(child1, parent2, start, end)
        self._fill_remaining(child2, parent1, start, end)

        return child1, child2

    def _fill_remaining(
        self, child: List[int], parent: List[int], start: int, end: int
    ):
        """Fill remaining positions in order crossover"""
        child_set = set(child[start:end])
        parent_filtered = [x for x in parent if x not in child_set]

        idx = 0
        for i in range(len(child)):
            if child[i] == -1:
                child[i] = parent_filtered[idx]
                idx += 1

    def _mutate(self, individual: List[int]) -> List[int]:
        """Swap mutation for permutation representation"""
        mutated = individual[:]
        if len(mutated) >= 2:
            i, j = random.sample(range(len(mutated)), 2)
            mutated[i], mutated[j] = mutated[j], mutated[i]
        return mutated

    def _select_best_compromise(
        self, pareto_front: List[int], objective_values: List[List[float]]
    ) -> int:
        """Select best compromise solution from Pareto front"""
        if not pareto_front:
            return 0

        # Simple approach: select solution closest to ideal point
        ideal_point = []
        for obj_idx in range(len(self.config.objectives)):
            min_val = min(
                objective_values[idx][obj_idx] for idx in pareto_front
            )
            ideal_point.append(min_val)

        best_distance = float("inf")
        best_idx = pareto_front[0]

        for idx in pareto_front:
            distance = sum(
                (objective_values[idx][i] - ideal_point[i]) ** 2
                for i in range(len(ideal_point))
            )
            if distance < best_distance:
                best_distance = distance
                best_idx = idx

        return best_idx

    def _calculate_metrics(
        self,
        pareto_front: List[int],
        objective_values: List[List[float]],
        processing_time: float,
        best_compromise_idx: int,
    ) -> Dict[str, Any]:
        """Calculate optimization metrics"""
        metrics = {
            "algorithm": "multi_objective",
            "pareto_front_size": len(pareto_front),
            "processing_time": processing_time,
            "total_generations": self.config.generations,
            "objectives_optimized": self.config.objectives,
            "best_compromise_solution": {
                "objectives": {
                    obj: objective_values[best_compromise_idx][i]
                    for i, obj in enumerate(self.config.objectives)
                }
            },
        }

        # Calculate hypervolume if possible
        if len(pareto_front) > 0:
            try:
                metrics["hypervolume"] = self._calculate_hypervolume(
                    pareto_front, objective_values
                )
            except:
                metrics["hypervolume"] = 0.0

        return metrics

    def _calculate_hypervolume(
        self, pareto_front: List[int], objective_values: List[List[float]]
    ) -> float:
        """Calculate hypervolume metric (simplified version)"""
        if len(pareto_front) == 0:
            return 0.0

        # Reference point (nadir point)
        ref_point = []
        for obj_idx in range(len(self.config.objectives)):
            max_val = max(
                objective_values[idx][obj_idx] for idx in pareto_front
            )
            ref_point.append(max_val * 1.1)  # 10% worse than worst

        # Simplified hypervolume calculation
        total_volume = 0.0
        for idx in pareto_front:
            volume = 1.0
            for i, obj_val in enumerate(objective_values[idx]):
                volume *= ref_point[i] - obj_val
            total_volume += volume

        return total_volume

    def _create_distance_matrix(
        self, stores: List[Dict[str, Any]]
    ) -> List[List[float]]:
        """Create distance matrix between stores"""
        n = len(stores)
        matrix = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(i + 1, n):
                distance = self._calculate_distance(stores[i], stores[j])
                matrix[i][j] = distance
                matrix[j][i] = distance

        return matrix

    def _calculate_distance(
        self, store1: Dict[str, Any], store2: Dict[str, Any]
    ) -> float:
        """Calculate Haversine distance between two stores"""
        lat1 = store1.get("lat", store1.get("latitude", 0))
        lon1 = store1.get("lon", store1.get("longitude", 0))
        lat2 = store2.get("lat", store2.get("latitude", 0))
        lon2 = store2.get("lon", store2.get("longitude", 0))

        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        return c * 6371  # Earth's radius in km

    # Objective functions
    def _calculate_total_distance(self, route: List[int]) -> float:
        """Calculate total distance of route"""
        if len(route) < 2:
            return 0.0

        total = 0.0
        for i in range(len(route) - 1):
            total += self.distance_matrix[route[i]][route[i + 1]]

        # Return to start
        total += self.distance_matrix[route[-1]][route[0]]
        return total

    def _calculate_total_time(self, route: List[int]) -> float:
        """Calculate total time (distance + service time)"""
        distance = self._calculate_total_distance(route)
        service_time = len(route) * 0.5  # 30 minutes per stop
        travel_time = distance / 50  # 50 km/h average speed
        return travel_time + service_time

    def _calculate_priority_score(self, route: List[int]) -> float:
        """Calculate priority score (lower is better)"""
        total_priority = 0.0
        for i, store_idx in enumerate(route):
            store = self.stores[store_idx]
            priority = store.get("priority", 1)  # Default priority = 1
            # Earlier positions get higher weight
            position_weight = len(route) - i
            total_priority += priority * position_weight
        return -total_priority  # Negative for minimization

    def _calculate_fuel_cost(self, route: List[int]) -> float:
        """Calculate fuel cost based on distance"""
        distance = self._calculate_total_distance(route)
        fuel_rate = 0.12  # $0.12 per km
        return distance * fuel_rate

    def _calculate_time_window_violations(self, route: List[int]) -> float:
        """Calculate time window violations"""
        violations = 0.0
        current_time = 9.0  # Start at 9 AM

        for store_idx in route:
            store = self.stores[store_idx]

            # Add travel time
            if store_idx > 0:
                prev_store_idx = route[route.index(store_idx) - 1]
                travel_time = (
                    self.distance_matrix[prev_store_idx][store_idx] / 50
                )  # 50 km/h
                current_time += travel_time

            # Check time window
            earliest = store.get("earliest_time", 8.0)
            latest = store.get("latest_time", 18.0)

            if current_time < earliest:
                violations += earliest - current_time
                current_time = earliest
            elif current_time > latest:
                violations += current_time - latest

            # Add service time
            service_time = store.get("service_time", 0.5)
            current_time += service_time

        return violations

    def _calculate_capacity_violations(self, route: List[int]) -> float:
        """Calculate vehicle capacity violations"""
        total_load = 0.0
        capacity = 1000.0  # Default capacity

        for store_idx in route:
            store = self.stores[store_idx]
            demand = store.get("demand", 10.0)  # Default demand
            total_load += demand

        if total_load > capacity:
            return total_load - capacity
        return 0.0

    def get_pareto_front(self) -> List[Dict[str, Any]]:
        """Get the Pareto front solutions"""
        # This would return all non-dominated solutions
        pass

    def get_metrics(self) -> MultiObjectiveMetrics:
        """Get optimization metrics"""
        return self.metrics
