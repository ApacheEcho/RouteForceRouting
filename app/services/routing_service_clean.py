"""
Routing Service - Business logic for route generation with database integration
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from geopy.distance import geodesic

# Import genetic algorithm
from app.optimization.genetic_algorithm import GeneticAlgorithm, GeneticConfig
from routing.core import generate_route as core_generate_route

logger = logging.getLogger(__name__)


def cluster_by_proximity(
    stores: list[dict], radius_km: float = 2.0
) -> list[list[dict]]:
    """
    Cluster stores by proximity to optimize routing

    Args:
        stores: List of store dictionaries with lat/lon coordinates
        radius_km: Maximum distance in kilometers for clustering

    Returns:
        List of clusters, where each cluster is a list of nearby stores
    """
    clusters = []
    for store in stores:
        added = False
        for cluster in clusters:
            if cluster and is_within_radius(store, cluster[0], radius_km):
                cluster.append(store)
                added = True
                break
        if not added:
            clusters.append([store])
    return clusters


def is_within_radius(store1: dict, store2: dict, radius_km: float) -> bool:
    """
    Check if two stores are within the specified radius

    Args:
        store1: First store dictionary
        store2: Second store dictionary
        radius_km: Maximum distance in kilometers

    Returns:
        True if stores are within radius, False otherwise
    """
    coord1 = (store1.get("lat"), store1.get("lon"))
    coord2 = (store2.get("lat"), store2.get("lon"))
    if None in coord1 or None in coord2:
        return False
    return geodesic(coord1, coord2).km <= radius_km


@dataclass
class RoutingMetrics:
    """Metrics for route generation performance"""

    processing_time: float
    total_stores: int
    filtered_stores: int
    optimization_score: float
    route_id: int | None = None
    clusters_used: int = 0
    distance_saved: float = 0.0
    algorithm_used: str = "default"
    algorithm_metrics: dict[str, Any] = None


class RoutingService:
    """Service for handling route generation and optimization with database integration"""

    def __init__(self, user_id: int | None = None):
        self.user_id = user_id
        self.last_processing_time = 0.0
        self.metrics = None

        # Try to import database service, fall back to None if not available
        try:
            from app.services.database_service import DatabaseService

            self.database_service = DatabaseService()
        except ImportError:
            self.database_service = None
            logger.warning(
                "Database service not available, running without persistence"
            )

    def generate_route_from_stores(
        self,
        stores: list[dict[str, Any]],
        constraints: dict[str, Any] | None = None,
        save_to_db: bool = True,
        algorithm: str = "default",
        algorithm_params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Generate route directly from store data (for API usage)

        Args:
            stores: List of store dictionaries
            constraints: Optional routing constraints
            save_to_db: Whether to save route to database
            algorithm: Algorithm to use for optimization
            algorithm_params: Parameters for the selected algorithm

        Returns:
            List of optimized route stops
        """
        start_time = time.time()

        try:
            if not stores:
                logger.warning("No stores provided")
                return []

            # Build routing constraints
            route_constraints = constraints or {}

            # Add algorithm selection to filters
            algorithm_filters = {"algorithm": algorithm}

            # Add algorithm-specific parameters
            if algorithm_params:
                algorithm_filters.update(algorithm_params)

            # Generate route using selected algorithm
            route, algorithm_metrics = self._generate_route_with_algorithm(
                stores, route_constraints, algorithm_filters
            )

            if not route:
                logger.warning("Route generation failed")
                self.last_processing_time = time.time() - start_time
                return []

            processing_time = time.time() - start_time
            self.last_processing_time = processing_time

            # Calculate optimization metrics
            optimization_score = self._calculate_optimization_score(route)

            # Create metrics object
            self.metrics = RoutingMetrics(
                processing_time=processing_time,
                total_stores=len(stores),
                filtered_stores=len(stores),
                optimization_score=optimization_score,
                algorithm_used=algorithm_metrics.get("algorithm", "default"),
                algorithm_metrics=algorithm_metrics,
            )

            # Save route to database if requested and database is available
            if save_to_db and self.user_id and self.database_service:
                route_record = self._save_route_to_db(
                    route, algorithm_filters, self.metrics
                )
                if route_record:
                    self.metrics.route_id = route_record.id

            logger.info(
                f"Route generated successfully in {processing_time:.2f}s with score {optimization_score:.1f}"
            )
            return route

        except Exception as e:
            logger.error(f"Error generating route: {str(e)}")
            self.last_processing_time = time.time() - start_time
            raise

    def _generate_route_with_algorithm(
        self,
        stores: list[dict[str, Any]],
        constraints: dict[str, Any],
        filters: dict[str, Any],
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """
        Generate route using the specified algorithm

        Args:
            stores: List of store dictionaries
            constraints: Routing constraints
            filters: Filters including algorithm selection

        Returns:
            Tuple of (route, algorithm_metrics)
        """
        algorithm = filters.get("algorithm", "default").lower()

        if algorithm == "genetic":
            return self._generate_route_genetic(stores, constraints, filters)
        else:
            # Use default algorithm
            route = core_generate_route(stores, constraints)
            return route, {"algorithm": "default"}

    def _generate_route_genetic(
        self,
        stores: list[dict[str, Any]],
        constraints: dict[str, Any],
        filters: dict[str, Any],
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """
        Generate route using genetic algorithm

        Args:
            stores: List of store dictionaries
            constraints: Routing constraints
            filters: Filters including genetic algorithm parameters

        Returns:
            Tuple of (route, algorithm_metrics)
        """
        logger.info(
            f"Using genetic algorithm for route optimization with {len(stores)} stores"
        )

        # Configure genetic algorithm
        config = GeneticConfig(
            population_size=int(filters.get("ga_population_size", 100)),
            generations=int(filters.get("ga_generations", 500)),
            mutation_rate=float(filters.get("ga_mutation_rate", 0.02)),
            crossover_rate=float(filters.get("ga_crossover_rate", 0.8)),
            elite_size=int(filters.get("ga_elite_size", 20)),
            tournament_size=int(filters.get("ga_tournament_size", 3)),
        )

        # Initialize and run genetic algorithm
        ga = GeneticAlgorithm(config)
        optimized_route, metrics = ga.optimize(stores, constraints)

        return optimized_route, metrics

    def _calculate_optimization_score(self, route: list[dict[str, Any]]) -> float:
        """Calculate a score for route optimization quality"""
        if not route or len(route) < 2:
            return 0.0

        # Calculate total distance
        total_distance = self._calculate_total_distance(route)

        # Simple scoring based on distance efficiency
        # Lower distance = higher score
        if total_distance == 0:
            return 100.0

        # Normalize score (example: 100 - distance in km)
        score = max(0, 100 - total_distance)
        return round(score, 2)

    def _calculate_total_distance(self, route: list[dict[str, Any]]) -> float:
        """Calculate total distance of a route"""
        if not route or len(route) < 2:
            return 0.0

        total_distance = 0.0
        for i in range(len(route) - 1):
            coord1 = (route[i].get("lat", 0), route[i].get("lon", 0))
            coord2 = (route[i + 1].get("lat", 0), route[i + 1].get("lon", 0))

            if coord1 != (0, 0) and coord2 != (0, 0):
                total_distance += geodesic(coord1, coord2).km

        return total_distance

    def get_last_processing_time(self) -> float:
        """Get the last processing time"""
        return self.last_processing_time

    def get_metrics(self) -> RoutingMetrics | None:
        """Get the last routing metrics"""
        return self.metrics

    def generate_route(
        self,
        stores: list[dict],
        constraints: dict[str, Any],
        algorithm: str = "default",
    ) -> list[dict[str, Any]]:
        """
        Generate route from stores with constraints

        Args:
            stores: List of store dictionaries
            constraints: Dictionary of routing constraints
            algorithm: Algorithm to use for optimization

        Returns:
            List of optimized route stops
        """
        return self.generate_route_from_stores(stores, constraints, algorithm=algorithm)

    def cluster_stores_by_proximity(
        self, stores: list[dict], radius_km: float = 2.0
    ) -> list[list[dict]]:
        """
        Cluster stores by proximity for route optimization

        Args:
            stores: List of store dictionaries
            radius_km: Maximum distance in kilometers for clustering

        Returns:
            List of clusters, where each cluster is a list of nearby stores
        """
        return cluster_by_proximity(stores, radius_km)

    def _save_route_to_db(
        self,
        route: list[dict[str, Any]],
        filters: dict[str, Any],
        metrics: RoutingMetrics,
    ):
        """Save route to database (placeholder for database integration)"""
        # This method would save the route to the database
        # For now, just return None since database integration is handled elsewhere
        return None
