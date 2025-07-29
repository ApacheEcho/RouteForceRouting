"""
Main Routing Service - Uses the unified routing service implementation
This is the primary entry point for all routing functionality
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from geopy.distance import geodesic

# Import optimization algorithms
from app.optimization.genetic_algorithm import GeneticAlgorithm, GeneticConfig
from app.optimization.multi_objective import (
    MultiObjectiveConfig,
    MultiObjectiveOptimizer,
)
from app.optimization.simulated_annealing import (
    SimulatedAnnealingConfig,
    SimulatedAnnealingOptimizer,
)

# Import the unified routing service
from app.services.routing_service_unified import (
    UnifiedRoutingMetrics,
    UnifiedRoutingService,
    create_unified_routing_service,
)

# Import Flask for current_app
try:
    from flask import current_app
except ImportError:
    current_app = None

# Import route core
try:
    from app.services.route_core import generate_route as core_generate_route
except ImportError:
    core_generate_route = None

# Import traffic service
try:
    from app.services.traffic_service import TrafficConfig, TrafficService
except ImportError:
    TrafficService = None
    TrafficConfig = None

logger = logging.getLogger(__name__)


# Factory function alias
def create_routing_service(user_id=None):
    """Create a routing service instance"""
    return create_unified_routing_service(user_id)


def cluster_by_proximity(
    stores: List[Dict], radius_km: float = 2.0
) -> List[List[Dict]]:
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


def is_within_radius(store1: Dict, store2: Dict, radius_km: float) -> bool:
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
class LegacyRoutingMetrics:
    """Legacy metrics for route generation performance - for backward compatibility"""

    processing_time: float
    total_stores: int
    filtered_stores: int
    optimization_score: float
    route_id: Optional[int] = None
    clusters_used: int = 0
    distance_saved: float = 0.0
    algorithm_used: str = "default"
    algorithm_metrics: Dict[str, Any] = None


RoutingMetrics = UnifiedRoutingMetrics
RoutingService = UnifiedRoutingService

# Export the main class and any utilities needed by tests
__all__ = [
    "RoutingService",
    "RoutingMetrics",
    "create_unified_routing_service",
    "cluster_by_proximity",
    "is_within_radius",
]


class RoutingServiceBackup:
    # All methods below this line are now properly indented as class methods
    # ...existing code re-indented one level...

    def get_route_by_id(self, route_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific route by ID

        Args:
            route_id: Route ID to retrieve

        Returns:
            Route data or None if not found
        """
        if not self.database_service:
            return None

        try:
            route = self.database_service.get_route_by_id(route_id)
            if route and (not self.user_id or route.user_id == self.user_id):
                return route.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error retrieving route {route_id}: {str(e)}")
            return None

    def _save_stores_to_db(self, stores: List[Dict[str, Any]]) -> None:
        """Save stores to database if they don't already exist"""
        if not self.database_service:
            return

        try:
            from app.models.database import Store

            for store_data in stores:
                # Check if store already exists
                existing_store = Store.query.filter_by(
                    name=store_data.get("name"),
                    latitude=store_data.get("lat"),
                    longitude=store_data.get("lon"),
                    user_id=self.user_id,
                ).first()

                if not existing_store:
                    self.database_service.create_store(
                        name=store_data.get("name", "Unknown"),
                        address=store_data.get("address"),
                        latitude=store_data.get("lat"),
                        longitude=store_data.get("lon"),
                        chain=store_data.get("chain"),
                        store_type=store_data.get("type"),
                        user_id=self.user_id,
                        metadata=store_data,
                    )
        except Exception as e:
            logger.error(f"Error saving stores to database: {str(e)}")

    def _save_route_to_db(
        self,
        route: List[Dict[str, Any]],
        filters: Dict[str, Any],
        metrics: RoutingMetrics,
    ) -> Optional[object]:
        """Save route to database"""
        if not self.database_service:
            return None

        try:
            route_name = f"Route {len(route)} stops - {time.strftime('%Y-%m-%d %H:%M')}"
            route_record = self.database_service.create_route(
                route_data=route,
                name=route_name,
                description=f"Generated with {len(route)} stops",
                total_distance=self._calculate_total_distance(route),
                total_time=metrics.processing_time,
                optimization_score=metrics.optimization_score,
                user_id=self.user_id,
                metadata={
                    "filters": filters,
                    "metrics": {
                        "processing_time": metrics.processing_time,
                        "total_stores": metrics.total_stores,
                        "filtered_stores": metrics.filtered_stores,
                        "optimization_score": metrics.optimization_score,
                    },
                },
            )

            # Create optimization record
            if route_record:
                self.database_service.create_route_optimization(
                    route_id=route_record.id,
                    algorithm_used="proximity_clustering",
                    parameters=filters,
                    execution_time=metrics.processing_time,
                    memory_usage=0,  # TODO: Implement memory tracking
                    optimization_score=metrics.optimization_score,
                )

            return route_record
        except Exception as e:
            logger.error(f"Error saving route to database: {str(e)}")
            return None

    def _calculate_total_distance(self, route: List[Dict[str, Any]]) -> float:
        """Calculate total distance of the route"""
        if not route or len(route) < 2:
            return 0.0

        total_distance = 0.0
        for i in range(len(route) - 1):
            coord1 = (route[i].get("lat", 0), route[i].get("lon", 0))
            coord2 = (route[i + 1].get("lat", 0), route[i + 1].get("lon", 0))

            if coord1 != (0, 0) and coord2 != (0, 0):
                total_distance += geodesic(coord1, coord2).km

        return total_distance

    def _build_constraints(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build routing constraints from filters"""
        constraints = {}

        # Maximum distance constraint
        if filters.get("max_distance"):
            constraints["max_distance"] = float(filters["max_distance"])

        # Maximum stores constraint
        if filters.get("max_stores"):
            constraints["max_stores"] = int(filters["max_stores"])

        # Proximity clustering
        if filters.get("use_clustering", True):
            constraints["use_clustering"] = True
            constraints["cluster_radius"] = float(filters.get("cluster_radius", 2.0))

        return constraints

    def _apply_filters(self, stores: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Apply filtering logic to stores"""
        filtered_stores = stores.copy()

        # Filter by chain
        if filters.get("chain"):
            chain_filter = filters["chain"].lower()
            filtered_stores = [
                store
                for store in filtered_stores
                if store.get("chain", "").lower() == chain_filter
            ]

        # Filter by store type
        if filters.get("store_type"):
            type_filter = filters["store_type"].lower()
            filtered_stores = [
                store
                for store in filtered_stores
                if store.get("type", "").lower() == type_filter
            ]

        # Filter by geographic bounds
        if filters.get("bounds"):
            bounds = filters["bounds"]
            filtered_stores = [
                store
                for store in filtered_stores
                if self._is_within_bounds(store, bounds)
            ]

        # Limit number of stores
        max_stores = filters.get("max_stores")
        if max_stores and len(filtered_stores) > max_stores:
            filtered_stores = filtered_stores[:max_stores]

        return filtered_stores

    def _is_within_bounds(self, store: Dict, bounds: Dict) -> bool:
        """Check if store is within geographic bounds"""
        lat = store.get("lat")
        lon = store.get("lon")

        if lat is None or lon is None:
            return False

        return bounds.get("south", -90) <= lat <= bounds.get(
            "north", 90
        ) and bounds.get("west", -180) <= lon <= bounds.get("east", 180)

    def _calculate_optimization_score(self, route: List[Dict]) -> float:
        """
        Calculate optimization score for the route

        Args:
            route: List of route stops

        Returns:
            Optimization score as percentage (0-100)
        """
        if not route or len(route) < 2:
            return 0.0

        # Calculate total distance
        total_distance = self._calculate_total_distance(route)

        # Simple scoring based on distance efficiency
        # Lower distance = higher score
        if total_distance == 0:
            return 100.0

        # Normalize score (arbitrary baseline of 100km for max score)
        baseline_distance = 100.0
        score = max(0, min(100, (baseline_distance / total_distance) * 100))

        return round(score, 2)

    def get_last_processing_time(self) -> float:
        """Get the last processing time"""
        return self.last_processing_time

    def get_metrics(self) -> Optional[RoutingMetrics]:
        """Get the last routing metrics"""
        return self.metrics

    def generate_route(
        self,
        stores: List[Dict],
        constraints: Dict[str, Any],
        algorithm: str = "default",
    ) -> List[Dict[str, Any]]:
        """
        Generate route from stores with constraints

        Args:
            stores: List of store dictionaries
            constraints: Dictionary of routing constraints
            algorithm: Algorithm to use for optimization

        Returns:
            List of optimized route stops
        """
        start_time = time.time()
        route_id = f"route_{int(time.time() * 1000)}"  # Generate unique route ID

        try:
            if not stores:
                logger.warning("No stores provided")
                return []

            # Broadcast route generation start
            self._broadcast_route_update(
                route_id,
                "generation_started",
                {
                    "total_stores": len(stores),
                    "algorithm": algorithm,
                    "constraints": constraints,
                },
            )

            # Generate route using selected algorithm
            algorithm_filters = {"algorithm": algorithm}
            route, algorithm_metrics = self._generate_route_with_algorithm(
                stores, constraints, algorithm_filters
            )

            if not route:
                logger.warning("Route generation failed")
                self.last_processing_time = time.time() - start_time
                # Broadcast failure
                self._broadcast_route_update(
                    route_id, "generation_failed", {"error": "Route generation failed"}
                )
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

            # Broadcast successful completion
            self._broadcast_route_update(
                route_id,
                "generation_completed",
                {
                    "route": route,
                    "processing_time": processing_time,
                    "optimization_score": optimization_score,
                    "algorithm_used": algorithm_metrics.get("algorithm", "default"),
                    "total_stores": len(stores),
                },
            )

            logger.info(
                f"Route generated successfully in {processing_time:.2f}s with score {optimization_score:.1f}"
            )
            return route

        except Exception as e:
            logger.error(f"Error generating route: {str(e)}")
            self.last_processing_time = time.time() - start_time
            # Broadcast error
            self._broadcast_route_update(
                route_id, "generation_error", {"error": str(e)}
            )
            return []

    def predict_route_performance(
        self, stores: List[Dict], context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Predict route optimization performance using ML

        Args:
            stores: List of store dictionaries
            context: Optional context information

        Returns:
            Dictionary with prediction results
        """
        try:
            if self.ml_predictor:
                prediction = self.ml_predictor.predict_route_performance(
                    stores, context
                )
                return {"success": True, "prediction": prediction}
            else:
                # Fall back to heuristic prediction
                return self._heuristic_performance_prediction(stores)
        except Exception as e:
            logger.error(f"Error predicting route performance: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "prediction": {"predicted_improvement": 0.0, "confidence": 0.0},
            }

    def recommend_algorithm(
        self, stores: List[Dict], context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Recommend the best algorithm for the given stores

        Args:
            stores: List of store dictionaries
            context: Optional context information

        Returns:
            Dictionary with algorithm recommendation
        """
        try:
            if self.ml_predictor:
                recommendation = self.ml_predictor.recommend_algorithm(stores, context)
                return {"success": True, "recommendation": recommendation}
            else:
                # Fall back to heuristic recommendation
                return self._heuristic_algorithm_recommendation(stores)
        except Exception as e:
            logger.error(f"Error recommending algorithm: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "recommendation": {
                    "recommended_algorithm": "default",
                    "confidence": 0.0,
                    "reasoning": f"Error in recommendation: {str(e)}",
                },
            }

    def get_ml_model_info(self) -> Dict[str, Any]:
        """
        Get information about the ML model

        Returns:
            Dictionary with model information
        """
        try:
            if self.ml_predictor:
                return {
                    "success": True,
                    "model_info": self.ml_predictor.get_model_info(),
                }
            else:
                return {
                    "success": False,
                    "model_info": {
                        "model_type": "none",
                        "training_samples": 0,
                        "last_trained": None,
                        "is_trained": False,
                    },
                }
        except Exception as e:
            logger.error(f"Error getting ML model info: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "model_info": {
                    "model_type": "error",
                    "training_samples": 0,
                    "last_trained": None,
                    "is_trained": False,
                },
            }

    def generate_route_with_ml_recommendation(
        self,
        stores: List[Dict],
        constraints: Dict[str, Any],
        context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Generate route using ML-recommended algorithm, then optimize with find_fastest_route.

        Args:
            stores: List of store dictionaries
            constraints: Routing constraints
            context: Optional context information

        Returns:
            Dictionary with route and ML recommendation details
        """
        try:
            # Get ML recommendation
            ml_recommendation = self.recommend_algorithm(stores, context)

            if ml_recommendation["success"]:
                recommended_algo = ml_recommendation["recommendation"][
                    "recommended_algorithm"
                ]

                # Generate route with recommended algorithm
                filters = constraints.copy()
                filters["algorithm"] = recommended_algo

                route = self.generate_route_from_stores(stores, filters)

                # Apply traffic optimization if available
                if self.traffic_service and self.traffic_service.api_available:
                    traffic_result = self.traffic_service.get_traffic_optimized_route(
                        route
                    )
                    if traffic_result["success"]:
                        optimized_route = traffic_result["route"]
                    else:
                        optimized_route = route
                else:
                    optimized_route = route

                return {
                    "success": True,
                    "route": optimized_route,
                    "ml_recommendation": ml_recommendation["recommendation"],
                    "algorithm_used": recommended_algo,
                }
            else:
                # Fall back to default algorithm
                route = self.generate_route_from_stores(stores, constraints)

                # Apply traffic optimization if available
                if self.traffic_service and self.traffic_service.api_available:
                    traffic_result = self.traffic_service.get_traffic_optimized_route(
                        route
                    )
                    if traffic_result["success"]:
                        optimized_route = traffic_result["route"]
                    else:
                        optimized_route = route
                else:
                    optimized_route = route

                return {
                    "success": True,
                    "route": optimized_route,
                    "ml_recommendation": {
                        "recommended_algorithm": "default",
                        "confidence": 0.0,
                        "reasoning": "ML recommendation failed, using default",
                    },
                    "algorithm_used": "default",
                }

        except Exception as e:
            logger.error(f"Error generating route with ML recommendation: {str(e)}")
            return {"success": False, "error": str(e), "route": []}

    def _heuristic_algorithm_recommendation(self, stores: List[Dict]) -> Dict[str, Any]:
        """
        Provide heuristic algorithm recommendation based on simple rules

        Args:
            stores: List of store dictionaries

        Returns:
            Dictionary with heuristic recommendation
        """
        try:
            num_stores = len(stores)

            if num_stores <= 5:
                # Small routes: use default (fast)
                return {
                    "success": True,
                    "recommendation": {
                        "recommended_algorithm": "default",
                        "confidence": 0.8,
                        "reasoning": f"Small route ({num_stores} stores) - default algorithm is sufficient",
                    },
                }
            elif num_stores <= 15:
                # Medium routes: use simulated annealing (fast and effective)
                return {
                    "success": True,
                    "recommendation": {
                        "recommended_algorithm": "simulated_annealing",
                        "confidence": 0.9,
                        "reasoning": f"Medium route ({num_stores} stores) - simulated annealing provides good optimization",
                    },
                }
            else:
                # Large routes: use genetic algorithm (best for complex problems)
                return {
                    "success": True,
                    "recommendation": {
                        "recommended_algorithm": "genetic",
                        "confidence": 0.85,
                        "reasoning": f"Large route ({num_stores} stores) - genetic algorithm handles complexity well",
                    },
                }

        except Exception as e:
            logger.error(f"Error in heuristic recommendation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "recommendation": {
                    "recommended_algorithm": "default",
                    "confidence": 0.0,
                    "reasoning": f"Error in heuristic recommendation: {str(e)}",
                },
            }

    def _heuristic_performance_prediction(self, stores: List[Dict]) -> Dict[str, Any]:
        """
        Provide heuristic performance prediction based on simple rules

        Args:
            stores: List of store dictionaries

        Returns:
            Dictionary with heuristic prediction
        """
        try:
            num_stores = len(stores)

            # Simple heuristic: more stores = more potential for improvement
            if num_stores <= 5:
                predicted_improvement = 2.0
            elif num_stores <= 15:
                predicted_improvement = 10.0
            else:
                predicted_improvement = 20.0

            return {
                "success": True,
                "prediction": {
                    "predicted_improvement": predicted_improvement,
                    "confidence": 0.6,
                },
            }

        except Exception as e:
            logger.error(f"Error in heuristic prediction: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "prediction": {"predicted_improvement": 0.0, "confidence": 0.0},
            }

    def _generate_route_ml(
        self,
        stores: List[Dict[str, Any]],
        constraints: Dict[str, Any],
        filters: Dict[str, Any],
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Generate route using ML-recommended algorithm

        Args:
            stores: List of store dictionaries
            constraints: Routing constraints
            filters: Filters including ML parameters

        Returns:
            Tuple of (route, algorithm_metrics)
        """
        try:
            # Get ML recommendation for best algorithm
            recommendation = self.recommend_algorithm(stores)

            if recommendation["success"]:
                recommended_algo = recommendation["recommendation"][
                    "recommended_algorithm"
                ]

                # Create new filters with recommended algorithm
                ml_filters = filters.copy()
                ml_filters["algorithm"] = recommended_algo

                # Generate route with recommended algorithm
                route, base_metrics = self._generate_route_with_algorithm(
                    stores, constraints, ml_filters
                )

                # Add ML recommendation info to metrics
                algorithm_metrics = {
                    "algorithm": "ml",
                    "ml_recommended_algorithm": recommended_algo,
                    "ml_confidence": recommendation["recommendation"]["confidence"],
                    "ml_reasoning": recommendation["recommendation"]["reasoning"],
                    "base_algorithm_metrics": base_metrics,
                }

                return route, algorithm_metrics
            else:
                # Fall back to default algorithm
                route = core_generate_route(stores, constraints)
                return route, {
                    "algorithm": "ml",
                    "ml_recommended_algorithm": "default",
                    "ml_confidence": 0.0,
                    "ml_reasoning": "ML recommendation failed, using default",
                    "error": recommendation.get("error", "Unknown error"),
                }

        except Exception as e:
            logger.error(f"Error in ML route generation: {str(e)}")
            # Fall back to default algorithm
            route = core_generate_route(stores, constraints)
            return route, {
                "algorithm": "ml",
                "error": str(e),
                "ml_recommended_algorithm": "default",
                "ml_confidence": 0.0,
                "ml_reasoning": f"ML generation failed: {str(e)}",
            }

    def generate_traffic_optimized_route(
        self,
        stores: List[Dict[str, Any]],
        constraints: Optional[Dict[str, Any]] = None,
        start_location: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate route optimized for traffic conditions using Google Maps API

        Args:
            stores: List of store dictionaries
            constraints: Optional routing constraints
            start_location: Optional starting location

        Returns:
            Dictionary with traffic-optimized route and traffic data
        """
        start_time = time.time()

        try:
            if not stores:
                logger.warning("No stores provided for traffic optimization")
                return {"success": False, "error": "No stores provided"}

            if not self.traffic_service:
                logger.warning("Traffic service not available")
                return self._fallback_to_basic_route(
                    stores, "Traffic service not available"
                )

            # Generate traffic-optimized route
            route_id = f"traffic_route_{int(time.time() * 1000)}"

            # Broadcast start
            self._broadcast_route_update(
                route_id,
                "traffic_optimization_started",
                {
                    "total_stores": len(stores),
                    "has_start_location": start_location is not None,
                },
            )

            # Get traffic-optimized route
            traffic_result = self.traffic_service.get_traffic_optimized_route(
                stores, start_location, constraints
            )

            processing_time = time.time() - start_time
            self.last_processing_time = processing_time

            if traffic_result["success"]:
                # Create metrics for traffic optimization
                self.metrics = RoutingMetrics(
                    processing_time=processing_time,
                    total_stores=len(stores),
                    filtered_stores=len(traffic_result["route"]),
                    optimization_score=self._calculate_traffic_optimization_score(
                        traffic_result
                    ),
                    algorithm_used="traffic_optimized",
                    algorithm_metrics=traffic_result.get("traffic_data", {}),
                )

                # Broadcast completion
                self._broadcast_route_update(
                    route_id,
                    "traffic_optimization_completed",
                    {
                        "route_length": len(traffic_result["route"]),
                        "processing_time": processing_time,
                        "total_distance": traffic_result.get("total_distance", 0),
                        "total_duration": traffic_result.get("total_duration", 0),
                        "traffic_delay": traffic_result.get("traffic_delay", 0),
                    },
                )

                logger.info(
                    f"Traffic-optimized route generated in {processing_time:.2f}s"
                )
                return traffic_result
            else:
                # Broadcast failure and fall back
                self._broadcast_route_update(
                    route_id,
                    "traffic_optimization_failed",
                    {"error": traffic_result.get("error", "Unknown error")},
                )

                return self._fallback_to_basic_route(
                    stores, traffic_result.get("error", "Traffic optimization failed")
                )

        except Exception as e:
            logger.error(f"Error in traffic optimization: {str(e)}")
            return self._fallback_to_basic_route(stores, f"Error: {str(e)}")

    def get_traffic_alternatives(
        self, stores: List[Dict[str, Any]], max_alternatives: int = 3
    ) -> Dict[str, Any]:
        """
        Get alternative routes with traffic analysis

        Args:
            stores: List of store dictionaries
            max_alternatives: Maximum number of alternatives

        Returns:
            Dictionary with alternative routes and traffic comparisons
        """
        try:
            if not self.traffic_service:
                return {"success": False, "error": "Traffic service not available"}

            alternatives = self.traffic_service.get_route_alternatives(
                stores, max_alternatives
            )

            if alternatives:
                # Find the best alternative
                best_alternative = min(alternatives, key=lambda x: x["total_duration"])

                return {
                    "success": True,
                    "alternatives": alternatives,
                    "best_alternative": best_alternative,
                    "recommendation": {
                        "route_id": best_alternative["route_id"],
                        "savings": {
                            "time_minutes": (
                                alternatives[0]["total_duration"]
                                - best_alternative["total_duration"]
                            )
                            / 60,
                            "distance_km": (
                                alternatives[0]["total_distance"]
                                - best_alternative["total_distance"]
                            )
                            / 1000,
                        },
                    },
                }
            else:
                return {"success": False, "error": "No alternatives generated"}

        except Exception as e:
            logger.error(f"Error getting traffic alternatives: {str(e)}")
            return {"success": False, "error": str(e)}

    def predict_traffic_for_route(
        self, stores: List[Dict[str, Any]], future_hours: List[int] = [1, 2, 4, 8]
    ) -> Dict[str, Any]:
        """
        Predict traffic conditions for future departure times

        Args:
            stores: List of store dictionaries
            future_hours: Hours in the future to predict

        Returns:
            Dictionary with traffic predictions
        """
        try:
            if not self.traffic_service:
                return {"success": False, "error": "Traffic service not available"}

            predictions = self.traffic_service.predict_traffic_conditions(
                stores, future_hours
            )

            if "success" in predictions and predictions["success"]:
                # Add route optimization recommendation
                best_time = predictions.get("best_time")
                if best_time:
                    predictions["recommendation"] = {
                        "best_departure_time": best_time,
                        "reason": "Minimal traffic delays predicted",
                        "should_delay": best_time
                        != "1h",  # If best time is not 1 hour from now
                    }

                return predictions
            else:
                return predictions

        except Exception as e:
            logger.error(f"Error predicting traffic: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_traffic_segment_data(
        self, origin: Dict[str, Any], destination: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed traffic data for a specific route segment

        Args:
            origin: Origin location
            destination: Destination location

        Returns:
            Traffic data dictionary or None
        """
        try:
            if not self.traffic_service:
                return None

            traffic_data = self.traffic_service.get_traffic_data_for_segment(
                origin, destination
            )

            if traffic_data:
                return {
                    "origin": traffic_data.origin,
                    "destination": traffic_data.destination,
                    "distance_meters": traffic_data.distance_meters,
                    "duration_seconds": traffic_data.duration_seconds,
                    "traffic_duration_seconds": traffic_data.duration_in_traffic_seconds,
                    "traffic_delay_seconds": traffic_data.traffic_delay,
                    "traffic_condition": traffic_data.traffic_condition,
                    "distance_km": traffic_data.distance_meters / 1000,
                    "duration_minutes": traffic_data.duration_seconds / 60,
                    "traffic_duration_minutes": traffic_data.duration_in_traffic_seconds
                    / 60,
                    "traffic_delay_minutes": traffic_data.traffic_delay / 60,
                }

            return None

        except Exception as e:
            logger.error(f"Error getting traffic segment data: {str(e)}")
            return None

    def _fallback_to_basic_route(
        self, stores: List[Dict[str, Any]], reason: str
    ) -> Dict[str, Any]:
        """Fallback to basic route generation when traffic optimization fails"""
        try:
            basic_route = self.generate_route(stores, {})
            return {
                "success": True,
                "route": basic_route,
                "traffic_data": {},
                "fallback_reason": reason,
                "algorithm_used": "basic_fallback",
            }
        except Exception as e:
            logger.error(f"Even basic route generation failed: {str(e)}")
            return {
                "success": False,
                "route": stores,
                "error": f"All route generation methods failed: {reason}, {str(e)}",
            }

    def _calculate_traffic_optimization_score(
        self, traffic_result: Dict[str, Any]
    ) -> float:
        """Calculate optimization score for traffic-optimized route"""
        try:
            if not traffic_result.get("success"):
                return 0.0

            # Base score from traffic efficiency
            total_duration = traffic_result.get("total_duration", 0)
            traffic_delay = traffic_result.get("traffic_delay", 0)

            if total_duration <= 0:
                return 50.0  # Neutral score

            # Calculate efficiency (lower delay = higher score)
            delay_ratio = traffic_delay / total_duration
            efficiency_score = max(0, 100 - (delay_ratio * 100))

            # Bonus for using traffic data
            traffic_bonus = 10 if traffic_result.get("traffic_data") else 0

            return min(100.0, efficiency_score + traffic_bonus)

        except Exception as e:
            logger.error(f"Error calculating traffic optimization score: {str(e)}")
            return 50.0  # Default neutral score

    def generate_route_from_stores(
        self, stores: List[Dict], filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate route from stores using specified filters

        Args:
            stores: List of store dictionaries
            filters: Dictionary of routing filters and algorithm selection

        Returns:
            List of optimized route stops
        """
        start_time = time.time()

        # Get optimization engine if available
        optimization_engine = None
        if current_app and hasattr(current_app, "optimization_engine"):
            optimization_engine = current_app.optimization_engine

        try:
            if not stores:
                logger.warning("No stores provided for route generation")
                return []

            # Track optimization start with performance engine
            if optimization_engine:
                optimization_engine.track_optimization_start(
                    {
                        "algorithm": filters.get("algorithm", "default"),
                        "stores_count": len(stores),
                        "timestamp": time.time(),
                    }
                )

            # Build constraints from filters
            constraints = self._build_constraints(filters)

            # Generate route using specified algorithm
            route, algorithm_metrics = self._generate_route_with_algorithm(
                stores, constraints, filters
            )

            processing_time = time.time() - start_time
            self.last_processing_time = processing_time

            # Calculate and store metrics
            optimization_score = self._calculate_optimization_score(route)
            self.metrics = RoutingMetrics(
                processing_time=processing_time,
                total_stores=len(stores),
                filtered_stores=len(stores),
                optimization_score=optimization_score,
                algorithm_used=algorithm_metrics.get("algorithm", "default"),
                algorithm_metrics=algorithm_metrics,
            )

            # Track optimization completion with performance engine
            if optimization_engine:
                optimization_engine.track_optimization_completion(
                    {
                        "algorithm": algorithm_metrics.get("algorithm", "default"),
                        "stores_count": len(stores),
                        "processing_time": processing_time,
                        "optimization_score": optimization_score,
                        "improvement_percent": algorithm_metrics.get(
                            "improvement_percent", 0
                        ),
                        "timestamp": time.time(),
                    }
                )

            logger.info(
                f"Route generated in {processing_time:.2f}s using {algorithm_metrics.get('algorithm', 'default')} algorithm"
            )
            return route

        except Exception as e:
            logger.error(f"Error generating route from stores: {str(e)}")
            self.last_processing_time = time.time() - start_time

            # Track optimization failure with performance engine
            if optimization_engine:
                optimization_engine.track_optimization_failure(
                    {
                        "algorithm": filters.get("algorithm", "default"),
                        "stores_count": len(stores),
                        "error": str(e),
                        "timestamp": time.time(),
                    }
                )

            return []

    def _broadcast_route_update(self, route_id: str, status: str, data: Dict[str, Any]):
        """Broadcast route update via WebSocket"""
        try:
            # Check if we're in Flask app context and WebSocket is available
            if current_app and hasattr(current_app, "websocket_manager"):
                websocket_manager = current_app.websocket_manager

                update_data = {"route_id": route_id, "status": status, "data": data}

                websocket_manager.broadcast_route_update(route_id, update_data)
                logger.debug(
                    f"Broadcasted WebSocket update for route {route_id}: {status}"
                )

        except Exception as e:
            logger.debug(f"WebSocket broadcast failed (non-critical): {str(e)}")

    def _broadcast_optimization_progress(self, route_id: str, progress: Dict[str, Any]):
        """Broadcast optimization progress via WebSocket"""
        try:
            if current_app and hasattr(current_app, "websocket_manager"):
                websocket_manager = current_app.websocket_manager
                websocket_manager.broadcast_optimization_progress(route_id, progress)
                logger.debug(f"Broadcasted optimization progress for route {route_id}")

        except Exception as e:
            logger.debug(
                f"WebSocket progress broadcast failed (non-critical): {str(e)}"
            )

    def _generate_route_with_algorithm(
        self,
        stores: List[Dict[str, Any]],
        constraints: Dict[str, Any],
        filters: Dict[str, Any],
        route_id: str = None,
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Generate route using specified algorithm

        Args:
            stores: List of store dictionaries
            constraints: Routing constraints
            filters: Filters including algorithm selection
            route_id: Optional route ID for progress tracking

        Returns:
            Tuple of (route, algorithm_metrics)
        """
        algorithm = filters.get("algorithm", "default")
        start_time = time.time()

        try:
            # Broadcast optimization start
            if route_id:
                self._broadcast_optimization_progress(
                    route_id,
                    {
                        "stage": "optimization_started",
                        "algorithm": algorithm,
                        "total_stores": len(stores),
                    },
                )

            # Route generation based on algorithm
            if algorithm == "genetic":
                route, metrics = self._generate_route_genetic(
                    stores, constraints, route_id
                )
            elif algorithm == "simulated_annealing":
                route, metrics = self._generate_route_simulated_annealing(
                    stores, constraints, route_id
                )
            elif algorithm == "multi_objective":
                route, metrics = self._generate_route_multi_objective(
                    stores, constraints, route_id
                )
            elif algorithm == "ml":
                route, metrics = self._generate_route_ml(stores, constraints, filters)
            else:
                # Default proximity clustering
                route, metrics = self._generate_route_default(
                    stores, constraints, route_id
                )

            processing_time = time.time() - start_time
            metrics.update(
                {
                    "total_processing_time": processing_time,
                    "stores_processed": len(stores),
                }
            )

            # Broadcast optimization completion
            if route_id:
                self._broadcast_optimization_progress(
                    route_id,
                    {
                        "stage": "optimization_completed",
                        "algorithm": algorithm,
                        "processing_time": processing_time,
                        "route_length": len(route) if route else 0,
                    },
                )

            return route, metrics

        except Exception as e:
            logger.error(f"Error in route generation with {algorithm}: {str(e)}")
            # Fall back to default algorithm
            route, metrics = self._generate_route_default(stores, constraints, route_id)
            metrics.update({"error": str(e), "fallback_used": True})
            return route, metrics

    def _generate_route_default(
        self, stores: List[Dict], constraints: Dict, route_id: str = None
    ) -> tuple[List[Dict], Dict]:
        """Generate route using default proximity clustering"""
        try:
            # Use proximity clustering if enabled
            if constraints.get("use_clustering", True):
                cluster_radius = constraints.get("cluster_radius", 2.0)
                clusters = cluster_by_proximity(stores, cluster_radius)

                # Flatten clusters back to route
                route = []
                for cluster in clusters:
                    route.extend(cluster)
            else:
                route = stores.copy()

            return route, {
                "algorithm": "default",
                "clusters_used": (
                    len(cluster_by_proximity(stores))
                    if constraints.get("use_clustering")
                    else 0
                ),
                "optimization_method": "proximity_clustering",
            }

        except Exception as e:
            logger.error(f"Error in default route generation: {str(e)}")
            return stores.copy(), {
                "algorithm": "default",
                "error": str(e),
                "fallback": True,
            }

    def _generate_route_genetic(
        self, stores: List[Dict], constraints: Dict, route_id: str = None
    ) -> tuple[List[Dict], Dict]:
        """Generate route using genetic algorithm"""
        try:
            if route_id:
                self._broadcast_optimization_progress(
                    route_id,
                    {
                        "stage": "genetic_initialization",
                        "message": "Initializing genetic algorithm...",
                    },
                )

            # Use optimized genetic algorithm configuration
            config = GeneticConfig(
                population_size=min(100, len(stores) * 5),  # Adaptive population size
                generations=200,
                mutation_rate=0.02,
                crossover_rate=0.8,
                elite_size=20,
            )
            genetic_optimizer = GeneticAlgorithm(config)

            # Use the new optimize method which returns (route, metrics)
            optimized_route, optimization_metrics = genetic_optimizer.optimize(
                stores, constraints
            )

            if route_id:
                self._broadcast_optimization_progress(
                    route_id,
                    {
                        "stage": "genetic_completed",
                        "generations": optimization_metrics.get("generations", 0),
                        "improvement": optimization_metrics.get(
                            "improvement_percent", 0
                        ),
                    },
                )

            # Return route and enhanced metrics
            return optimized_route, {
                "algorithm": "genetic",
                "generations_completed": optimization_metrics.get("generations", 0),
                "initial_distance_km": optimization_metrics.get("initial_distance", 0),
                "final_distance_km": optimization_metrics.get("final_distance", 0),
                "improvement_percent": optimization_metrics.get(
                    "improvement_percent", 0
                ),
                "population_size": config.population_size,
                "execution_time": optimization_metrics.get("execution_time", 0),
            }

        except Exception as e:
            logger.error(f"Error in genetic algorithm: {str(e)}")
            return self._generate_route_default(stores, constraints, route_id)

    def _generate_route_simulated_annealing(
        self, stores: List[Dict], constraints: Dict, route_id: str = None
    ) -> tuple[List[Dict], Dict]:
        """Generate route using simulated annealing"""
        try:
            if route_id:
                self._broadcast_optimization_progress(
                    route_id,
                    {
                        "stage": "sa_initialization",
                        "message": "Initializing simulated annealing...",
                    },
                )

            config = SimulatedAnnealingConfig()
            sa_optimizer = SimulatedAnnealingOptimizer(config)

            route_data = sa_optimizer.optimize_route(stores, constraints)

            if route_id:
                self._broadcast_optimization_progress(
                    route_id,
                    {
                        "stage": "sa_completed",
                        "iterations": config.max_iterations,
                        "temperature": config.initial_temperature,
                    },
                )

            return route_data.get("route", stores), {
                "algorithm": "simulated_annealing",
                "iterations": config.max_iterations,
                "initial_temperature": config.initial_temperature,
                "cooling_rate": config.cooling_rate,
                "final_cost": route_data.get("cost", 0),
            }

        except Exception as e:
            logger.error(f"Error in simulated annealing: {str(e)}")
            return self._generate_route_default(stores, constraints, route_id)

    def _generate_route_multi_objective(
        self, stores: List[Dict], constraints: Dict, route_id: str = None
    ) -> tuple[List[Dict], Dict]:
        """Generate route using multi-objective optimization"""
        try:
            if route_id:
                self._broadcast_optimization_progress(
                    route_id,
                    {
                        "stage": "mo_initialization",
                        "message": "Initializing multi-objective optimization...",
                    },
                )

            config = MultiObjectiveConfig()
            mo_optimizer = MultiObjectiveOptimizer(config)

            route_data = mo_optimizer.optimize_route(stores, constraints)

            if route_id:
                self._broadcast_optimization_progress(
                    route_id,
                    {
                        "stage": "mo_completed",
                        "objectives": ["distance", "time", "priority"],
                        "pareto_solutions": route_data.get("pareto_solutions", 1),
                    },
                )

            return route_data.get("route", stores), {
                "algorithm": "multi_objective",
                "objectives": ["distance", "time", "priority"],
                "pareto_solutions": route_data.get("pareto_solutions", 1),
                "final_scores": route_data.get("scores", {}),
            }

        except Exception as e:
            logger.error(f"Error in multi-objective optimization: {str(e)}")
            return self._generate_route_default(stores, constraints, route_id)


# Export the main class and any utilities needed by tests
__all__ = ["RoutingService", "cluster_by_proximity", "is_within_radius"]
