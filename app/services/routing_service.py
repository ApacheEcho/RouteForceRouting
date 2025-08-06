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
    algorithm_metrics: Optional[Dict[str, Any]] = None


# Create aliases for backward compatibility
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
