"""
Unified Routing Service - Consolidation of all routing service implementations
Clean, modern, testable design with dependency injection
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.services.distance_service import (
    RouteDistanceCalculator,
    create_distance_calculator,
)

# Import modern service modules
from app.services.geocoding_service import (
    ModernGeocodingService,
    create_geocoding_service,
)
from app.services.metrics_service import track_route_generation
from app.services.route_core import (
    ModernRouteGenerator,
    RouteConstraints,
    create_route_generator,
)
from app.services.route_scoring_service import RouteScorer

# Import optimization algorithms (with fallback)
try:
    from app.optimization.genetic_algorithm import (
        GeneticAlgorithm,
        GeneticConfig,
    )
except ImportError:
    GeneticAlgorithm = None
    GeneticConfig = None

try:
    from app.optimization.simulated_annealing import (
        SimulatedAnnealingConfig,
        SimulatedAnnealingOptimizer,
    )
except ImportError:
    SimulatedAnnealingOptimizer = None
    SimulatedAnnealingConfig = None

logger = logging.getLogger(__name__)


@dataclass
class UnifiedRoutingMetrics:
    """Extended routing metrics for the unified service"""

    processing_time: float
    total_stores: int
    filtered_stores: int
    optimization_score: float
    total_distance: float
    algorithm_used: str
    route_id: Optional[int] = None
    clusters_used: int = 0
    distance_saved: float = 0.0
    algorithm_metrics: Optional[Dict[str, Any]] = None


class UnifiedRoutingService:
    """
    Unified Routing Service - Consolidates all routing functionality
    Modern, clean, testable design replacing multiple legacy implementations
    """

    def __init__(
        self,
        user_id: Optional[int] = None,
        geocoding_service: Optional[ModernGeocodingService] = None,
        distance_calculator: Optional[RouteDistanceCalculator] = None,
        route_generator: Optional[ModernRouteGenerator] = None,
        route_scorer: Optional[RouteScorer] = None,
    ):
        """
        Initialize with dependency injection for testability

        Args:
            user_id: Optional user ID for database operations
            geocoding_service: Geocoding service instance
            distance_calculator: Distance calculation service
            route_generator: Route generation service
            route_scorer: Route scoring service instance
        """
        self.user_id = user_id
        self.last_processing_time = 0.0
        self.metrics: Optional[UnifiedRoutingMetrics] = None

        # Initialize services with defaults if not provided
        self.geocoding_service = (
            geocoding_service or create_geocoding_service()
        )
        self.distance_calculator = (
            distance_calculator or create_distance_calculator()
        )
        self.route_generator = route_generator or create_route_generator(
            "nearest_neighbor"
        )
        self.route_scorer = route_scorer or RouteScorer()

        # Try to initialize database service
        self.database_service = self._initialize_database_service()

        # Initialize advanced optimization algorithms
        self._initialize_optimization_algorithms()

    def _initialize_database_service(self):
        """Initialize database service with fallback"""
        try:
            from app.services.database_service import DatabaseService

            return DatabaseService()
        except ImportError:
            logger.warning(
                "Database service not available, running without persistence"
            )
            return None

    def _initialize_optimization_algorithms(self):
        """Initialize advanced optimization algorithms"""
        # Genetic Algorithm
        if GeneticAlgorithm and GeneticConfig:
            self.genetic_config = GeneticConfig()
            logger.info("Genetic algorithm available")
        else:
            self.genetic_config = None
            logger.warning("Genetic algorithm not available")

        # Simulated Annealing
        if SimulatedAnnealingOptimizer and SimulatedAnnealingConfig:
            self.sa_config = SimulatedAnnealingConfig()
            logger.info("Simulated annealing available")
        else:
            self.sa_config = None
            logger.warning("Simulated annealing not available")

    def ensure_coordinates(
        self, stores: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Ensure all stores have coordinates, geocoding addresses if needed

        Args:
            stores: List of store dictionaries

        Returns:
            List of stores with coordinates populated
        """
        geocoded_stores = []

        for store in stores:
            store_copy = store.copy()

            # Check if coordinates already exist (support both lon and lng)
            if "lat" in store_copy and ("lon" in store_copy or "lng" in store_copy):
                # Normalize to 'lon' key internally for consistency
                if "lng" in store_copy and "lon" not in store_copy:
                    try:
                        store_copy["lon"] = float(store_copy["lng"])  # type: ignore[index]
                    except (TypeError, ValueError):
                        pass
                geocoded_stores.append(store_copy)
                continue

            # Try to geocode from address
            address = store_copy.get("address", "")
            if address:
                coords = self.geocoding_service.get_coordinates(address)
                if coords:
                    store_copy["lat"], store_copy["lon"] = coords
                    geocoded_stores.append(store_copy)
                else:
                    logger.warning(
                        f"Failed to geocode store: {store_copy.get('name', 'Unknown')}"
                    )
            else:
                logger.warning(
                    f"No address available for store: {store_copy.get('name', 'Unknown')}"
                )

        return geocoded_stores

    @track_route_generation
    def generate_route_from_stores(
        self,
        stores: List[Dict[str, Any]],
        constraints: Optional[Dict[str, Any]] = None,
        save_to_db: bool = True,
        algorithm: str = "nearest_neighbor",
        algorithm_params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate optimized route from stores list

        Args:
            stores: List of store dictionaries
            constraints: Route constraints dictionary
            save_to_db: Whether to save route to database
            algorithm: Algorithm to use ("nearest_neighbor", "priority", "genetic", "simulated_annealing")
            algorithm_params: Algorithm-specific parameters

        Returns:
            List of stores representing optimized route
        """
        start_time = time.time()

        try:
            if not stores:
                self.last_processing_time = 0.0
                return []

            # Ensure all stores have coordinates
            geocoded_stores = self.ensure_coordinates(stores)
            if not geocoded_stores:
                logger.warning("No stores with valid coordinates")
                self.last_processing_time = time.time() - start_time
                return []

            # Convert constraints to RouteConstraints format
            route_constraints = self._convert_constraints(constraints)

            # Generate route based on algorithm
            if algorithm == "genetic" and self.genetic_config:
                route = self._generate_route_genetic(
                    geocoded_stores, route_constraints, algorithm_params
                )
            elif algorithm == "simulated_annealing" and self.sa_config:
                route = self._generate_route_simulated_annealing(
                    geocoded_stores, route_constraints, algorithm_params
                )
            else:
                # Use modern route generator for standard algorithms
                generator = create_route_generator(algorithm)
                route, core_metrics = generator.generate_route(
                    geocoded_stores, route_constraints
                )

            processing_time = time.time() - start_time
            self.last_processing_time = processing_time

            # Calculate metrics
            total_distance = self.distance_calculator.calculate_route_distance(
                route
            )
            optimization_score = (
                len(route) / max(total_distance, 0.1)
                if total_distance > 0
                else 0
            )

            self.metrics = UnifiedRoutingMetrics(
                processing_time=processing_time,
                total_stores=len(stores),
                filtered_stores=len(route),
                optimization_score=optimization_score,
                total_distance=total_distance,
                algorithm_used=algorithm,
            )

            # Save to database if requested
            if save_to_db and self.database_service and self.user_id:
                try:
                    route_record = self._save_route_to_db(
                        route, constraints or {}, self.metrics
                    )
                    if route_record:
                        self.metrics.route_id = getattr(
                            route_record, "id", None
                        )
                except Exception as e:
                    logger.error(f"Failed to save route to database: {e}")

            logger.info(
                f"Route generated successfully in {processing_time:.2f}s using {algorithm}"
            )
            return route

        except Exception as e:
            logger.error(f"Error generating route: {str(e)}")
            self.last_processing_time = time.time() - start_time
            raise

    def _convert_constraints(
        self, constraints: Optional[Dict[str, Any]]
    ) -> RouteConstraints:
        """Convert legacy constraints format to RouteConstraints"""
        if not constraints:
            return RouteConstraints()

        return RouteConstraints(
            max_stores=constraints.get("max_stores"),
            max_distance_km=constraints.get("max_distance_km"),
            time_windows=constraints.get("time_windows"),
            priority_weights=constraints.get("priority_weights"),
            visit_date=constraints.get("visit_date"),
        )

    def _generate_route_genetic(
        self,
        stores: List[Dict[str, Any]],
        constraints: RouteConstraints,
        algorithm_params: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Generate route using genetic algorithm"""
        if not GeneticAlgorithm:
            logger.warning(
                "Genetic algorithm not available, falling back to nearest neighbor"
            )
            generator = create_route_generator("nearest_neighbor")
            route, _ = generator.generate_route(stores, constraints)
            return route

        # Configure genetic algorithm
        config = GeneticConfig()
        if algorithm_params:
            config.population_size = algorithm_params.get(
                "population_size", config.population_size
            )
            config.generations = algorithm_params.get(
                "generations", config.generations
            )
            config.mutation_rate = algorithm_params.get(
                "mutation_rate", config.mutation_rate
            )
            config.crossover_rate = algorithm_params.get(
                "crossover_rate", config.crossover_rate
            )

        # If population size is 1, GA degenerates; use nearest neighbor fast path
        if getattr(config, "population_size", 1) <= 1:
            generator = create_route_generator("nearest_neighbor")
            route, _ = generator.generate_route(stores, constraints)
            # Store algorithm-specific metrics as a trivial result
            if self.metrics:
                self.metrics.algorithm_metrics = {
                    "population_size": config.population_size,
                    "generations": getattr(config, "generations", 0),
                    "note": "Population size <= 1; used nearest_neighbor fallback",
                }
            return route

        # Run genetic algorithm
        ga = GeneticAlgorithm(config)
        route, metrics = ga.optimize(stores, constraints.__dict__)

        # Store algorithm-specific metrics
        if self.metrics:
            self.metrics.algorithm_metrics = metrics

        return route

    def _generate_route_simulated_annealing(
        self,
        stores: List[Dict[str, Any]],
        constraints: RouteConstraints,
        algorithm_params: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Generate route using simulated annealing"""
        if not SimulatedAnnealingOptimizer:
            logger.warning(
                "Simulated annealing not available, falling back to nearest neighbor"
            )
            generator = create_route_generator("nearest_neighbor")
            route, _ = generator.generate_route(stores, constraints)
            return route

        # Configure simulated annealing
        config = SimulatedAnnealingConfig()
        if algorithm_params:
            config.initial_temperature = algorithm_params.get(
                "initial_temperature", config.initial_temperature
            )
            config.cooling_rate = algorithm_params.get(
                "cooling_rate", config.cooling_rate
            )
            config.min_temperature = algorithm_params.get(
                "min_temperature", config.min_temperature
            )

        # Run simulated annealing
        sa = SimulatedAnnealingOptimizer(config)
        route, metrics = sa.optimize(stores, constraints.__dict__)

        # Store algorithm-specific metrics
        if self.metrics:
            self.metrics.algorithm_metrics = metrics

        return route

    def _save_route_to_db(
        self,
        route: List[Dict[str, Any]],
        constraints: Dict[str, Any],
        metrics: UnifiedRoutingMetrics,
    ):
        """Save route to database"""
        try:
            if not self.database_service:
                return None

            route_data = {
                "user_id": self.user_id,
                "stores": route,
                "constraints": constraints,
                "metrics": {
                    "processing_time": metrics.processing_time,
                    "total_stores": metrics.total_stores,
                    "optimization_score": metrics.optimization_score,
                    "algorithm_used": metrics.algorithm_used,
                    "total_distance": metrics.total_distance,
                },
            }

            return self.database_service.save_route(route_data)
        except Exception as e:
            logger.error(f"Database save failed: {e}")
            return None

    def score_route(
        self,
        route: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        Score a route using the integrated route scoring service

        Args:
            route: List of stores in route order
            context: Optional context (playbook, traffic data, etc.)

        Returns:
            RouteScore object with total score and component breakdown
        """
        try:
            return self.route_scorer.score_route(route, context)
        except Exception as e:
            logger.error(f"Route scoring failed: {e}")
            # Return a minimal score object
            from app.services.route_scoring_service import RouteScore

            return RouteScore(
                total_score=0.0,
                component_scores={"error": 1.0},
                raw_metrics={"error": str(e)},
                scoring_metadata={"error": True},
            )

    def score_and_compare_routes(
        self,
        routes: List[List[Dict[str, Any]]],
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        Score multiple routes and return them ranked by score

        Args:
            routes: List of routes to score
            context: Optional context for scoring

        Returns:
            List of tuples (route, score) sorted by score descending
        """
        try:
            scored_routes = []
            for route in routes:
                score = self.score_route(route, context)
                scored_routes.append((route, score))

            # Sort by total score (highest first)
            scored_routes.sort(key=lambda x: x[1].total_score, reverse=True)
            return scored_routes
        except Exception as e:
            logger.error(f"Route comparison failed: {e}")
            return []

    def get_metrics(self) -> Optional[UnifiedRoutingMetrics]:
        """Get the last generation metrics"""
        return self.metrics

    def get_last_processing_time(self) -> float:
        """Get the last processing time"""
        return self.last_processing_time

    def clear_geocoding_cache(self) -> None:
        """Clear the geocoding cache"""
        self.geocoding_service.clear_cache()

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "geocoding_cache_size": self.geocoding_service.get_cache_size()
        }

    # ===== BACKWARD COMPATIBILITY METHODS =====
    # These methods maintain compatibility with existing tests and legacy code

    def geocode_stores(
        self, stores: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Geocode stores list - backward compatibility method

        Args:
            stores: List of store dictionaries

        Returns:
            List of stores with geocoded coordinates
        """
        geocoded_stores = []
        for store in stores:
            # Skip if already has coordinates
            if store.get("lat") and store.get("lon"):
                geocoded_stores.append(store)
                continue

            # Geocode using address
            address = store.get("address", "")
            if address:
                coords = self.geocoding_service.get_coordinates(address)
                if coords:
                    store_copy = store.copy()
                    store_copy["lat"], store_copy["lon"] = coords
                    store_copy["latitude"], store_copy["longitude"] = (
                        coords  # Both formats
                    )
                    geocoded_stores.append(store_copy)
                else:
                    # Keep store even if geocoding fails
                    geocoded_stores.append(store)
            else:
                geocoded_stores.append(store)

        return geocoded_stores

    def cluster_stores_by_proximity(
        self, stores: List[Dict[str, Any]], radius_km: float = 2.0
    ) -> List[List[Dict[str, Any]]]:
        """
        Cluster stores by proximity - backward compatibility method

        Args:
            stores: List of store dictionaries
            radius_km: Clustering radius in kilometers

        Returns:
            List of store clusters
        """
        if not stores:
            return []

        try:
            # Import the clustering function
            from app.utils.clustering import cluster_by_proximity

            return cluster_by_proximity(stores, radius_km)
        except ImportError:
            # Fallback: simple clustering based on distance
            return self._simple_proximity_clustering(stores, radius_km)

    def _simple_proximity_clustering(
        self, stores: List[Dict[str, Any]], radius_km: float
    ) -> List[List[Dict[str, Any]]]:
        """Simple fallback clustering implementation"""
        clusters = []
        unprocessed = stores.copy()

        while unprocessed:
            # Start new cluster with first unprocessed store
            current_store = unprocessed.pop(0)
            cluster = [current_store]

            # Find nearby stores
            i = 0
            while i < len(unprocessed):
                store = unprocessed[i]
                if self._stores_within_radius(current_store, store, radius_km):
                    cluster.append(unprocessed.pop(i))
                else:
                    i += 1

            clusters.append(cluster)

        return clusters

    def _stores_within_radius(
        self, store1: Dict[str, Any], store2: Dict[str, Any], radius_km: float
    ) -> bool:
        """Check if two stores are within specified radius"""
        lat1 = store1.get("lat") or store1.get("latitude", 0)
        lon1 = store1.get("lon") or store1.get("longitude", 0)
        lat2 = store2.get("lat") or store2.get("latitude", 0)
        lon2 = store2.get("lon") or store2.get("longitude", 0)

        if not all([lat1, lon1, lat2, lon2]):
            return False

        try:
            from geopy.distance import geodesic

            distance = geodesic((lat1, lon1), (lat2, lon2)).kilometers
            return distance <= radius_km
        except ImportError:
            # Simple distance approximation if geopy not available
            import math

            lat_diff = lat2 - lat1
            lon_diff = lon2 - lon1
            distance = (
                math.sqrt(lat_diff**2 + lon_diff**2) * 111
            )  # Rough km per degree
            return distance <= radius_km

    def _calculate_total_distance(self, route: List[Dict[str, Any]]) -> float:
        """
        Calculate total distance of route - backward compatibility method

        Args:
            route: List of route stops

        Returns:
            Total distance in kilometers
        """
        return self.distance_calculator.calculate_route_distance(route)

    def _calculate_optimization_score(
        self, route: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate optimization score for route - backward compatibility method

        Args:
            route: List of route stops

        Returns:
            Optimization score (0-100)
        """
        if not route or len(route) < 2:
            return 0.0

        # Use the route scorer for comprehensive scoring
        try:
            weights = {
                "distance_weight": 0.6,
                "time_weight": 0.2,
                "priority_weight": 0.2,
            }
            score = self.route_scorer.calculate_comprehensive_score(
                route, weights
            )
            return min(100.0, max(0.0, score))
        except Exception as e:
            logger.warning(f"Error calculating optimization score: {e}")
            # Fallback to simple distance-based scoring
            total_distance = self._calculate_total_distance(route)
            if total_distance == 0:
                return 100.0
            # Normalize score (lower distance = higher score)
            baseline_distance = 100.0  # Arbitrary baseline
            score = max(
                0, min(100, (baseline_distance / total_distance) * 100)
            )
            return round(score, 2)


# Factory function for easy setup
def create_unified_routing_service(
    user_id: Optional[int] = None,
) -> UnifiedRoutingService:
    """Create a fully configured unified routing service"""
    return UnifiedRoutingService(user_id=user_id)


# Legacy compatibility - RoutingService alias
RoutingService = UnifiedRoutingService
