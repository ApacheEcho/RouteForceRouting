from typing import List, Dict, Any, Optional
import logging
import time
from dataclasses import dataclass
from geopy.distance import geodesic

logger = logging.getLogger(__name__)


@dataclass
class RoutingMetrics:
    """Metrics for route generation performance"""

    processing_time: float
    total_stores: int
    filtered_stores: int
    optimization_score: float
    route_id: Optional[int] = None


class RoutingService:
    """Service for route generation with database integration"""

    def __init__(self, user_id: Optional[int] = None):
        self.user_id = user_id
        self.last_processing_time = 0.0
        self.metrics = None

        # Database service (optional)
        try:
            from app.services.database_service import DatabaseService

            self.database_service = DatabaseService()
        except ImportError:
            self.database_service = None

    def generate_route(
        self, stores: List[Dict], constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate route from stores with constraints"""
        start_time = time.time()

        try:
            from routing.core import generate_route as core_generate_route

            route = core_generate_route(stores, constraints)

            self.last_processing_time = time.time() - start_time

            # Calculate metrics
            self.metrics = RoutingMetrics(
                processing_time=self.last_processing_time,
                total_stores=len(stores),
                filtered_stores=len(route) if route else 0,
                optimization_score=self._calculate_optimization_score(route),
            )

            return route or []

        except Exception as e:
            logger.error(f"Error generating route: {e}")
            self.last_processing_time = time.time() - start_time
            return []

    def _calculate_optimization_score(self, route: List[Dict]) -> float:
        """Calculate optimization score for the route"""
        if not route or len(route) < 2:
            return 0.0

        # Simple scoring based on route length
        return min(100.0, 100.0 - (len(route) - 1) * 2)

    def get_last_processing_time(self) -> float:
        """Get the last processing time"""
        return self.last_processing_time

    def get_metrics(self) -> Optional[RoutingMetrics]:
        """Get the last routing metrics"""
        return self.metrics
