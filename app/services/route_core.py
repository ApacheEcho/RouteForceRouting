"""
Modernized Route Generation Core - Clean, testable, algorithm-agnostic
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, Tuple

from app.services.distance_service import (
    RouteDistanceCalculator,
    create_distance_calculator,
)

logger = logging.getLogger(__name__)


@dataclass
class RouteConstraints:
    """Type-safe route constraints"""

    max_stores: Optional[int] = None
    max_distance_km: Optional[float] = None
    time_windows: Optional[Dict[str, Dict[str, str]]] = None
    priority_weights: Optional[Dict[str, float]] = None
    visit_date: Optional[datetime] = None


@dataclass
class RouteMetrics:
    """Route quality metrics"""

    total_distance: float
    total_stores: int
    processing_time: float
    algorithm_used: str
    optimization_score: float = 0.0
    constraints_violated: List[str] = None

    def __post_init__(self):
        if self.constraints_violated is None:
            self.constraints_violated = []


class RouteFilter(ABC):
    """Abstract base class for route filters"""

    @abstractmethod
    def apply(
        self, stores: List[Dict[str, Any]], constraints: RouteConstraints
    ) -> List[Dict[str, Any]]:
        """Apply filter to stores based on constraints"""
        ...


class TimeWindowFilter(RouteFilter):
    """Filter stores based on time windows"""

    def apply(
        self, stores: List[Dict[str, Any]], constraints: RouteConstraints
    ) -> List[Dict[str, Any]]:
        """Apply time window filtering"""
        if not constraints.time_windows or not constraints.visit_date:
            return stores

        filtered_stores = []
        current_time = constraints.visit_date.time()

        for store in stores:
            chain = store.get("chain", "")
            if chain in constraints.time_windows:
                try:
                    time_window = constraints.time_windows[chain]
                    start_time = datetime.strptime(
                        time_window["start"], "%H:%M"
                    ).time()
                    end_time = datetime.strptime(
                        time_window["end"], "%H:%M"
                    ).time()

                    if start_time <= current_time <= end_time:
                        filtered_stores.append(store)
                except (KeyError, ValueError) as e:
                    logger.warning(
                        f"Invalid time window for chain {chain}: {e}"
                    )
                    filtered_stores.append(
                        store
                    )  # Include store if parsing fails
            else:
                filtered_stores.append(
                    store
                )  # Include stores without time constraints

        return filtered_stores


class MaxStoresFilter(RouteFilter):
    """Filter stores based on maximum route length"""

    def apply(
        self, stores: List[Dict[str, Any]], constraints: RouteConstraints
    ) -> List[Dict[str, Any]]:
        """Apply maximum stores filtering"""
        if constraints.max_stores and len(stores) > constraints.max_stores:
            # Sort by priority if available, then by name for consistency
            def sort_key(store):
                chain = store.get("chain", "")
                priority = 0
                if (
                    constraints.priority_weights
                    and chain in constraints.priority_weights
                ):
                    priority = constraints.priority_weights[chain]
                return (-priority, store.get("name", ""))

            sorted_stores = sorted(stores, key=sort_key)
            return sorted_stores[: constraints.max_stores]

        return stores


class RouteOptimizer(Protocol):
    """Protocol for route optimization algorithms"""

    def optimize(
        self, stores: List[Dict[str, Any]], constraints: RouteConstraints
    ) -> List[Dict[str, Any]]:
        """Optimize the route order"""
        ...


class PriorityOptimizer:
    """Simple priority-based route optimization"""

    def optimize(
        self, stores: List[Dict[str, Any]], constraints: RouteConstraints
    ) -> List[Dict[str, Any]]:
        """Optimize route by priority and distance"""
        if not stores:
            return []

        def sort_key(store):
            chain = store.get("chain", "")
            priority = 0
            if (
                constraints.priority_weights
                and chain in constraints.priority_weights
            ):
                priority = constraints.priority_weights[chain]
            return (-priority, store.get("name", ""))

        return sorted(stores, key=sort_key)


class GreedyNearestNeighborOptimizer:
    """Greedy nearest neighbor algorithm with priority weighting"""

    def __init__(self, distance_calculator: RouteDistanceCalculator):
        self.distance_calculator = distance_calculator

    def optimize(
        self, stores: List[Dict[str, Any]], constraints: RouteConstraints
    ) -> List[Dict[str, Any]]:
        """Optimize route using nearest neighbor with priority weighting"""
        if len(stores) <= 1:
            return stores

        # Find starting store (highest priority or first store)
        def priority_score(store):
            chain = store.get("chain", "")
            if (
                constraints.priority_weights
                and chain in constraints.priority_weights
            ):
                return constraints.priority_weights[chain]
            return 0

        route = []
        remaining = stores.copy()

        # Start with highest priority store
        current = max(remaining, key=priority_score)
        route.append(current)
        remaining.remove(current)

        # Greedy nearest neighbor for remaining stores
        while remaining:
            next_store = min(
                remaining,
                key=lambda s: self.distance_calculator.calculate_store_distance(
                    current, s
                ),
            )
            route.append(next_store)
            remaining.remove(next_store)
            current = next_store

        return route


class ModernRouteGenerator:
    """Modern, testable route generator with dependency injection"""

    def __init__(
        self,
        filters: List[RouteFilter] = None,
        optimizer: RouteOptimizer = None,
        distance_calculator: RouteDistanceCalculator = None,
    ):
        self.filters = filters or [TimeWindowFilter(), MaxStoresFilter()]
        self.optimizer = optimizer or PriorityOptimizer()
        self.distance_calculator = (
            distance_calculator or create_distance_calculator()
        )

    def generate_route(
        self,
        stores: List[Dict[str, Any]],
        constraints: Optional[RouteConstraints] = None,
    ) -> Tuple[List[Dict[str, Any]], RouteMetrics]:
        """
        Generate optimized route with filtering and optimization

        Args:
            stores: List of store dictionaries
            constraints: Route constraints and parameters

        Returns:
            Tuple of (optimized_route, metrics)
        """
        start_time = datetime.now()
        constraints = constraints or RouteConstraints()

        if not stores:
            empty_metrics = RouteMetrics(
                total_distance=0.0,
                total_stores=0,
                processing_time=0.0,
                algorithm_used="empty_route",
            )
            return [], empty_metrics

        # Apply filters
        filtered_stores = stores.copy()
        for filter_instance in self.filters:
            filtered_stores = filter_instance.apply(
                filtered_stores, constraints
            )

        # Optimize route
        optimized_route = self.optimizer.optimize(filtered_stores, constraints)

        # Calculate metrics
        processing_time = (datetime.now() - start_time).total_seconds()
        total_distance = self.distance_calculator.calculate_route_distance(
            optimized_route
        )

        # Calculate optimization score (simple: stores/distance ratio)
        optimization_score = len(optimized_route) / max(total_distance, 0.1)

        metrics = RouteMetrics(
            total_distance=total_distance,
            total_stores=len(optimized_route),
            processing_time=processing_time,
            algorithm_used=getattr(
                self.optimizer, "__class__", type(self.optimizer)
            ).__name__,
            optimization_score=optimization_score,
        )

        return optimized_route, metrics

    def summarize_route(
        self,
        route: List[Dict[str, Any]],
        original_stores: List[Dict[str, Any]],
        constraints: Optional[RouteConstraints] = None,
    ) -> Dict[str, Any]:
        """Generate route summary with analysis"""
        constraints = constraints or RouteConstraints()

        summary = {
            "total_stops": len(route),
            "original_stores": len(original_stores),
            "stores_filtered": len(original_stores) - len(route),
            "chains_in_route": list(
                {store.get("chain", "Unknown") for store in route}
            ),
            "total_distance_km": self.distance_calculator.calculate_route_distance(
                route
            ),
            "priorities": {},
            "constraints_applied": [],
        }

        # Count priorities
        if constraints.priority_weights:
            for store in route:
                chain = store.get("chain", "Unknown")
                if chain in constraints.priority_weights:
                    priority = constraints.priority_weights[chain]
                    summary["priorities"][str(priority)] = (
                        summary["priorities"].get(str(priority), 0) + 1
                    )

        # Document applied constraints
        if constraints.max_stores:
            summary["constraints_applied"].append(
                f"max_stores: {constraints.max_stores}"
            )
        if constraints.max_distance_km:
            summary["constraints_applied"].append(
                f"max_distance: {constraints.max_distance_km}km"
            )
        if constraints.time_windows:
            summary["constraints_applied"].append(
                f"time_windows: {len(constraints.time_windows)} chains"
            )

        return summary


# Factory functions for easy setup
def create_route_generator(
    algorithm: str = "priority",
) -> ModernRouteGenerator:
    """Create a route generator with specified algorithm"""
    distance_calc = create_distance_calculator()

    if algorithm == "nearest_neighbor":
        optimizer = GreedyNearestNeighborOptimizer(distance_calc)
    else:  # Default to priority
        optimizer = PriorityOptimizer()

    return ModernRouteGenerator(
        filters=[TimeWindowFilter(), MaxStoresFilter()],
        optimizer=optimizer,
        distance_calculator=distance_calc,
    )


# Legacy compatibility functions
def generate_route(
    stores: List[Dict[str, Any]],
    visit_date: Optional[datetime] = None,
    playbook: Optional[Dict] = None,
) -> List[Dict[str, Any]]:
    """Legacy compatibility function"""
    # Convert playbook to constraints
    constraints = RouteConstraints()
    if visit_date:
        constraints.visit_date = visit_date
    if playbook:
        # Convert playbook format to modern constraints
        time_windows = {}
        priority_weights = {}
        for chain, config in playbook.items():
            if not isinstance(config, dict):
                continue  # Skip non-dict values (e.g., max_route_stops)
            if "visit_hours" in config:
                time_windows[chain] = config["visit_hours"]
            if "priority" in config:
                priority_weights[chain] = config["priority"]
        constraints.time_windows = time_windows if time_windows else None
        constraints.priority_weights = (
            priority_weights if priority_weights else None
        )

    generator = create_route_generator("nearest_neighbor")
    route, _ = generator.generate_route(stores, constraints)
    return route


def summarize_route(
    route: List[Dict[str, Any]],
    original_stores: List[Dict[str, Any]],
    playbook: Optional[Dict] = None,
    visit_date: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Legacy compatibility function"""
    # Convert to modern format
    constraints = RouteConstraints()
    if visit_date:
        constraints.visit_date = visit_date
    if playbook:
        time_windows = {}
        priority_weights = {}
        for chain, config in playbook.items():
            if not isinstance(config, dict):
                continue  # Skip non-dict values (e.g., max_route_stops)
            if "visit_hours" in config:
                time_windows[chain] = config["visit_hours"]
            if "priority" in config:
                priority_weights[chain] = config["priority"]
        constraints.time_windows = time_windows if time_windows else None
        constraints.priority_weights = (
            priority_weights if priority_weights else None
        )

    generator = create_route_generator()
    return generator.summarize_route(route, original_stores, constraints)


def print_route_summary(summary: Dict[str, Any]) -> None:
    """Legacy compatibility function"""
    print("\n--- Route Summary ---")
    print(f"Total Stops: {summary.get('total_stops', 0)}")
    print(f"Original Stores: {summary.get('original_stores', 0)}")
    print(f"Stores Filtered: {summary.get('stores_filtered', 0)}")
    print(f"Total Distance: {summary.get('total_distance_km', 0):.2f} km")
    print(f"Chains in Route: {', '.join(summary.get('chains_in_route', []))}")

    priorities = summary.get("priorities", {})
    if priorities:
        print("Priority Distribution:")
        for priority, count in sorted(priorities.items(), reverse=True):
            print(f"  Priority {priority}: {count} stop(s)")

    constraints = summary.get("constraints_applied", [])
    if constraints:
        print(f"Constraints Applied: {', '.join(constraints)}")

    print("----------------------\n")
