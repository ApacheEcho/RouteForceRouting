"""
Simulated Annealing Algorithm for Route Optimization
Implements classical simulated annealing with various cooling schedules and neighborhood operations
"""

import logging
import math
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class SimulatedAnnealingConfig:
    """Configuration for Simulated Annealing algorithm"""

    initial_temperature: float = 1000.0
    final_temperature: float = 0.1
    cooling_rate: float = 0.95
    max_iterations: int = 10000
    iterations_per_temp: int = 100
    cooling_schedule: str = "exponential"  # 'exponential', 'linear', 'logarithmic'
    neighborhood_operator: str = "swap"  # 'swap', 'insert', 'reverse', 'mixed'
    reheat_threshold: int = 1000  # Iterations without improvement before reheating
    reheat_factor: float = 1.5
    min_improvement_threshold: float = 0.001

    def __post_init__(self):
        """Validate configuration parameters"""
        if self.initial_temperature <= self.final_temperature:
            raise ValueError(
                "Initial temperature must be greater than final temperature"
            )
        if not 0 < self.cooling_rate < 1:
            raise ValueError("Cooling rate must be between 0 and 1")
        if self.max_iterations <= 0:
            raise ValueError("Max iterations must be positive")
        if self.iterations_per_temp <= 0:
            raise ValueError("Iterations per temperature must be positive")


@dataclass
class SimulatedAnnealingMetrics:
    """Metrics collected during simulated annealing optimization"""

    algorithm_used: str = "simulated_annealing"
    initial_distance: float = 0.0
    final_distance: float = 0.0
    improvement_percentage: float = 0.0
    total_iterations: int = 0
    temperature_reductions: int = 0
    accepted_moves: int = 0
    rejected_moves: int = 0
    reheats: int = 0
    processing_time: float = 0.0
    convergence_iteration: int = 0
    final_temperature: float = 0.0
    acceptance_rate: float = 0.0
    cooling_schedule: str = "exponential"
    neighborhood_operator: str = "swap"


class SimulatedAnnealingOptimizer:
    """
    Simulated Annealing optimizer for the Traveling Salesman Problem (TSP)

    Implements the classic simulated annealing algorithm with multiple cooling schedules
    and neighborhood operations for route optimization.
    """

    def __init__(self, config: SimulatedAnnealingConfig):
        """
        Initialize the Simulated Annealing optimizer

        Args:
            config: Configuration object containing SA parameters
        """
        self.config = config
        self.distance_matrix = None
        self.metrics = SimulatedAnnealingMetrics()

        # Choose cooling schedule function
        self.cooling_schedules = {
            "exponential": self._exponential_cooling,
            "linear": self._linear_cooling,
            "logarithmic": self._logarithmic_cooling,
        }

        # Choose neighborhood operation function
        self.neighborhood_operators = {
            "swap": self._swap_two_nodes,
            "insert": self._insert_node,
            "reverse": self._reverse_segment,
            "mixed": self._mixed_neighborhood,
        }

        self.cooling_function = self.cooling_schedules.get(
            config.cooling_schedule, self._exponential_cooling
        )

        self.neighborhood_function = self.neighborhood_operators.get(
            config.neighborhood_operator, self._swap_two_nodes
        )

        logger.info(
            f"Initialized SA optimizer with {config.cooling_schedule} cooling and {config.neighborhood_operator} neighborhood"
        )

    def optimize(
        self, stores: list[dict[str, Any]], constraints: dict[str, Any] | None = None
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """
        Optimize route using simulated annealing

        Args:
            stores: List of store dictionaries with lat/lon coordinates
            constraints: Optional constraints (not used in current implementation)

        Returns:
            Tuple of (optimized_route, metrics_dict)
        """
        start_time = time.time()

        try:
            if len(stores) < 2:
                raise ValueError("At least 2 stores required for optimization")

            # Initialize metrics
            self.metrics.cooling_schedule = self.config.cooling_schedule
            self.metrics.neighborhood_operator = self.config.neighborhood_operator

            # Create distance matrix
            self.distance_matrix = self._create_distance_matrix(stores)

            # Create initial solution (random permutation)
            current_route = list(range(len(stores)))
            random.shuffle(current_route)

            # Calculate initial distance
            current_distance = self._calculate_route_distance(current_route)
            self.metrics.initial_distance = current_distance

            # Initialize best solution
            best_route = current_route.copy()
            best_distance = current_distance

            # Initialize temperature
            temperature = self.config.initial_temperature

            # Initialize tracking variables
            iterations = 0
            temperature_reductions = 0
            accepted_moves = 0
            rejected_moves = 0
            reheats = 0
            iterations_without_improvement = 0

            logger.info(f"Starting SA optimization with {len(stores)} stores")
            logger.info(f"Initial distance: {current_distance:.4f}")

            # Main simulated annealing loop
            while (
                temperature > self.config.final_temperature
                and iterations < self.config.max_iterations
            ):

                # Perform iterations at current temperature
                for _ in range(self.config.iterations_per_temp):
                    if iterations >= self.config.max_iterations:
                        break

                    # Generate neighbor solution
                    neighbor_route = self.neighborhood_function(current_route.copy())
                    neighbor_distance = self._calculate_route_distance(neighbor_route)

                    # Calculate change in objective function
                    delta = neighbor_distance - current_distance

                    # Accept or reject the neighbor
                    if delta < 0 or random.random() < math.exp(-delta / temperature):
                        # Accept the neighbor
                        current_route = neighbor_route
                        current_distance = neighbor_distance
                        accepted_moves += 1

                        # Update best solution if better
                        if current_distance < best_distance:
                            best_route = current_route.copy()
                            best_distance = current_distance
                            iterations_without_improvement = 0
                            self.metrics.convergence_iteration = iterations
                        else:
                            iterations_without_improvement += 1
                    else:
                        # Reject the neighbor
                        rejected_moves += 1
                        iterations_without_improvement += 1

                    iterations += 1

                # Check for reheating
                if iterations_without_improvement >= self.config.reheat_threshold:
                    temperature *= self.config.reheat_factor
                    reheats += 1
                    iterations_without_improvement = 0
                    logger.debug(f"Reheated to temperature {temperature:.4f}")

                # Cool down the temperature
                temperature = self.cooling_function(temperature, temperature_reductions)
                temperature_reductions += 1

                # Log progress periodically
                if temperature_reductions % 10 == 0:
                    logger.debug(
                        f"Temperature: {temperature:.4f}, Best distance: {best_distance:.4f}"
                    )

            # Create the optimized route with store data
            optimized_route = [stores[i] for i in best_route]

            # Calculate metrics
            processing_time = time.time() - start_time
            improvement_percent = (
                (self.metrics.initial_distance - best_distance)
                / self.metrics.initial_distance
            ) * 100

            # Update metrics
            self.metrics.final_distance = best_distance
            self.metrics.improvement_percentage = improvement_percent
            self.metrics.total_iterations = iterations
            self.metrics.temperature_reductions = temperature_reductions
            self.metrics.accepted_moves = accepted_moves
            self.metrics.rejected_moves = rejected_moves
            self.metrics.reheats = reheats
            self.metrics.processing_time = processing_time
            self.metrics.final_temperature = temperature

            # Calculate acceptance rate
            total_moves = accepted_moves + rejected_moves
            self.metrics.acceptance_rate = (
                accepted_moves / total_moves if total_moves > 0 else 0
            )

            # Create metrics dictionary for API compatibility
            metrics_dict = {
                "algorithm": "simulated_annealing",
                "initial_distance": self.metrics.initial_distance,
                "final_distance": self.metrics.final_distance,
                "improvement_percent": improvement_percent,
                "total_iterations": iterations,
                "temperature_reductions": temperature_reductions,
                "accepted_moves": accepted_moves,
                "rejected_moves": rejected_moves,
                "acceptance_rate": self.metrics.acceptance_rate,
                "reheats": reheats,
                "processing_time": processing_time,
                "convergence_iteration": self.metrics.convergence_iteration,
                "final_temperature": temperature,
                "cooling_schedule": self.config.cooling_schedule,
                "neighborhood_operator": self.config.neighborhood_operator,
            }

            logger.info(f"SA optimization completed in {processing_time:.4f}s")
            logger.info(f"Final distance: {best_distance:.4f}")
            logger.info(f"Improvement: {improvement_percent:.2f}%")
            logger.info(
                f"Accepted moves: {accepted_moves}/{total_moves} ({self.metrics.acceptance_rate:.1%})"
            )

            return optimized_route, metrics_dict

        except Exception as e:
            logger.error(f"Error in Simulated Annealing optimization: {str(e)}")
            processing_time = time.time() - start_time
            return stores, {
                "algorithm": "simulated_annealing",
                "error": str(e),
                "processing_time": processing_time,
            }

    def _create_distance_matrix(
        self, stores: list[dict[str, Any]]
    ) -> list[list[float]]:
        """Create distance matrix between all stores"""
        n = len(stores)
        matrix = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(i + 1, n):
                distance = self._calculate_distance(stores[i], stores[j])
                matrix[i][j] = distance
                matrix[j][i] = distance

        return matrix

    def _calculate_distance(
        self, store1: dict[str, Any], store2: dict[str, Any]
    ) -> float:
        """Calculate Haversine distance between two stores"""
        # Handle both 'lat'/'lon' and 'latitude'/'longitude' formats
        lat1 = store1.get("lat", store1.get("latitude"))
        lon1 = store1.get("lon", store1.get("longitude"))
        lat2 = store2.get("lat", store2.get("latitude"))
        lon2 = store2.get("lon", store2.get("longitude"))

        if any(coord is None for coord in [lat1, lon1, lat2, lon2]):
            raise ValueError("Missing latitude/longitude coordinates")

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

        # Radius of Earth in kilometers
        r = 6371

        return c * r

    def _calculate_route_distance(self, route: list[int]) -> float:
        """Calculate total distance of a route"""
        if not route or len(route) < 2:
            return 0.0

        total_distance = 0.0
        for i in range(len(route) - 1):
            total_distance += self.distance_matrix[route[i]][route[i + 1]]

        # Add distance from last to first (complete the tour)
        total_distance += self.distance_matrix[route[-1]][route[0]]

        return total_distance

    # Cooling schedule functions
    def _exponential_cooling(self, temperature: float, iteration: int) -> float:
        """Exponential cooling schedule"""
        return temperature * self.config.cooling_rate

    def _linear_cooling(self, temperature: float, iteration: int) -> float:
        """Linear cooling schedule"""
        return self.config.initial_temperature - (
            iteration
            * (self.config.initial_temperature - self.config.final_temperature)
            / self.config.max_iterations
        )

    def _logarithmic_cooling(self, temperature: float, iteration: int) -> float:
        """Logarithmic cooling schedule"""
        return self.config.initial_temperature / (1 + math.log(1 + iteration))

    # Neighborhood operation functions
    def _swap_two_nodes(self, route: list[int]) -> list[int]:
        """Swap two random nodes in the route"""
        if len(route) < 2:
            return route

        i, j = random.sample(range(len(route)), 2)
        route[i], route[j] = route[j], route[i]
        return route

    def _insert_node(self, route: list[int]) -> list[int]:
        """Remove a node and insert it at a different position"""
        if len(route) < 3:
            return route

        # Remove node from random position
        i = random.randint(0, len(route) - 1)
        node = route.pop(i)

        # Insert at different random position
        j = random.randint(0, len(route))
        route.insert(j, node)

        return route

    def _reverse_segment(self, route: list[int]) -> list[int]:
        """Reverse a random segment of the route"""
        if len(route) < 3:
            return route

        # Choose two random points
        i, j = sorted(random.sample(range(len(route)), 2))

        # Reverse the segment between i and j
        route[i : j + 1] = route[i : j + 1][::-1]

        return route

    def _mixed_neighborhood(self, route: list[int]) -> list[int]:
        """Randomly choose between different neighborhood operations"""
        operations = [self._swap_two_nodes, self._insert_node, self._reverse_segment]
        operation = random.choice(operations)
        return operation(route)

    def get_metrics(self) -> SimulatedAnnealingMetrics:
        """Get optimization metrics"""
        return self.metrics
