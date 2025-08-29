"""
RouteForceRouting - Core routing engine with multi-vehicle optimization.
"""

import math
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class OptimizationMethod(Enum):
    """Available route optimization methods."""

    NEAREST_NEIGHBOR = "nearest_neighbor"
    GENETIC_ALGORITHM = "genetic_algorithm"
    SIMULATED_ANNEALING = "simulated_annealing"
    TWO_OPT = "two_opt"
    CLARKE_WRIGHT = "clarke_wright"


class VehicleStatus(Enum):
    """Vehicle availability status."""

    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"


@dataclass
class Vehicle:
    """Vehicle configuration and constraints."""

    vehicle_id: str
    capacity_kg: float
    max_packages: int
    max_driving_hours: float
    status: VehicleStatus = VehicleStatus.AVAILABLE
    current_location: Optional[Dict[str, float]] = None
    driver_id: Optional[str] = None

    def __post_init__(self):
        if self.current_location is None:
            # Default depot location (Manhattan)
            self.current_location = {"lat": 40.7128, "lng": -74.0060}


@dataclass
class Store:
    """Store delivery destination."""

    store_id: str
    name: str
    address: str
    coordinates: Dict[str, float]
    delivery_window: str
    priority: str
    estimated_service_time: int
    packages: int
    weight_kg: float
    special_requirements: Optional[Dict[str, Any]] = None


@dataclass
class Route:
    """Optimized delivery route."""

    route_id: str
    vehicle_id: str
    driver_id: Optional[str]
    stops: List[Dict[str, Any]]
    total_distance_km: float
    estimated_duration_hours: float
    total_weight_kg: float
    total_packages: int
    optimization_method: str
    created_at: datetime
    status: str = "planned"


class RouteOptimizer:
    """Core route optimization engine with multi-vehicle support."""

    def __init__(self, depot_location: Dict[str, float] = None):
        """Initialize route optimizer with depot location."""
        self.depot_location = depot_location or {
            "lat": 40.7128,
            "lng": -74.0060,
        }
        self.optimization_cache = {}

    def calculate_distance(
        self, point1: Dict[str, float], point2: Dict[str, float]
    ) -> float:
        """Calculate distance between two geographic points using Haversine formula."""
        lat1, lng1 = math.radians(point1["lat"]), math.radians(point1["lng"])
        lat2, lng2 = math.radians(point2["lat"]), math.radians(point2["lng"])

        dlat = lat2 - lat1
        dlng = lng2 - lng1

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        # Earth's radius in kilometers
        earth_radius_km = 6371.0
        return earth_radius_km * c

    def create_distance_matrix(
        self, locations: List[Dict[str, float]]
    ) -> List[List[float]]:
        """Create distance matrix for all location pairs."""
        n = len(locations)
        matrix = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(i + 1, n):
                distance = self.calculate_distance(locations[i], locations[j])
                matrix[i][j] = distance
                matrix[j][i] = distance

        return matrix

    def nearest_neighbor_tsp(
        self, stores: List[Store], start_location: Dict[str, float] = None
    ) -> List[Store]:
        """Solve TSP using nearest neighbor heuristic."""
        if not stores:
            return []

        if len(stores) == 1:
            return stores

        start_loc = start_location or self.depot_location
        unvisited = stores.copy()
        route = []

        # Find nearest store to starting location
        current_location = start_loc

        while unvisited:
            nearest_store = min(
                unvisited,
                key=lambda s: self.calculate_distance(
                    current_location, s.coordinates
                ),
            )
            route.append(nearest_store)
            unvisited.remove(nearest_store)
            current_location = nearest_store.coordinates

        return route

    def two_opt_improvement(self, route: List[Store]) -> List[Store]:
        """Improve route using 2-opt local search."""
        if len(route) < 4:
            return route

        improved = True
        best_route = route.copy()

        while improved:
            improved = False
            for i in range(1, len(best_route) - 2):
                for j in range(i + 1, len(best_route)):
                    if j - i == 1:
                        continue  # Skip adjacent edges

                    # Calculate current distance
                    current_dist = self.calculate_distance(
                        best_route[i - 1].coordinates,
                        best_route[i].coordinates,
                    ) + self.calculate_distance(
                        best_route[j - 1].coordinates,
                        best_route[j].coordinates,
                    )

                    # Calculate distance after 2-opt swap
                    new_dist = self.calculate_distance(
                        best_route[i - 1].coordinates,
                        best_route[j - 1].coordinates,
                    ) + self.calculate_distance(
                        best_route[i].coordinates, best_route[j].coordinates
                    )

                    if new_dist < current_dist:
                        # Perform 2-opt swap
                        best_route[i:j] = best_route[i:j][::-1]
                        improved = True
                        break

                if improved:
                    break

        return best_route

    def distribute_stores_to_vehicles(
        self, stores: List[Store], vehicles: List[Vehicle]
    ) -> Dict[str, List[Store]]:
        """Distribute stores across available vehicles using capacity constraints."""
        available_vehicles = [
            v for v in vehicles if v.status == VehicleStatus.AVAILABLE
        ]

        if not available_vehicles:
            raise ValueError("No available vehicles for route assignment")

        # Sort stores by priority and delivery window urgency
        priority_weights = {"high": 3, "medium": 2, "low": 1}

        def get_urgency_score(store: Store) -> float:
            priority_score = priority_weights.get(store.priority, 1)

            # Calculate time window urgency (earlier windows = higher urgency)
            window_start = store.delivery_window.split("-")[0]
            hour = int(window_start.split(":")[0])
            time_urgency = 24 - hour  # Earlier times get higher scores

            return priority_score * 10 + time_urgency

        sorted_stores = sorted(stores, key=get_urgency_score, reverse=True)

        # Initialize vehicle assignments
        vehicle_assignments = {v.vehicle_id: [] for v in available_vehicles}
        vehicle_loads = {
            v.vehicle_id: {"weight": 0.0, "packages": 0}
            for v in available_vehicles
        }

        # Assign stores using best-fit decreasing algorithm
        for store in sorted_stores:
            best_vehicle = None
            min_capacity_waste = float("inf")

            for vehicle in available_vehicles:
                current_load = vehicle_loads[vehicle.vehicle_id]

                # Check if store fits in vehicle
                if (
                    current_load["weight"] + store.weight_kg
                    <= vehicle.capacity_kg
                    and current_load["packages"] + store.packages
                    <= vehicle.max_packages
                ):
                    # Calculate capacity waste (prefer fuller vehicles)
                    weight_utilization = (
                        current_load["weight"] + store.weight_kg
                    ) / vehicle.capacity_kg
                    package_utilization = (
                        current_load["packages"] + store.packages
                    ) / vehicle.max_packages
                    avg_utilization = (
                        weight_utilization + package_utilization
                    ) / 2

                    capacity_waste = 1.0 - avg_utilization

                    if capacity_waste < min_capacity_waste:
                        min_capacity_waste = capacity_waste
                        best_vehicle = vehicle

            if best_vehicle:
                vehicle_assignments[best_vehicle.vehicle_id].append(store)
                vehicle_loads[best_vehicle.vehicle_id][
                    "weight"
                ] += store.weight_kg
                vehicle_loads[best_vehicle.vehicle_id][
                    "packages"
                ] += store.packages
            else:
                # Store doesn't fit in any vehicle - needs special handling
                print(
                    f"Warning: Store {store.store_id} doesn't fit in any available vehicle"
                )

        # Remove empty assignments
        return {
            vid: stores
            for vid, stores in vehicle_assignments.items()
            if stores
        }

    def optimize_multi_vehicle_routes(
        self,
        stores: List[Store],
        vehicles: List[Vehicle],
        method: OptimizationMethod = OptimizationMethod.NEAREST_NEIGHBOR,
    ) -> List[Route]:
        """Optimize routes for multiple vehicles."""
        if not stores:
            return []

        # Distribute stores across vehicles
        vehicle_assignments = self.distribute_stores_to_vehicles(
            stores, vehicles
        )

        if not vehicle_assignments:
            raise ValueError("No feasible vehicle assignments found")

        optimized_routes = []

        for vehicle_id, assigned_stores in vehicle_assignments.items():
            if not assigned_stores:
                continue

            vehicle = next(v for v in vehicles if v.vehicle_id == vehicle_id)

            # Optimize route for this vehicle
            if method == OptimizationMethod.NEAREST_NEIGHBOR:
                optimized_sequence = self.nearest_neighbor_tsp(
                    assigned_stores, vehicle.current_location
                )
            elif method == OptimizationMethod.TWO_OPT:
                initial_route = self.nearest_neighbor_tsp(
                    assigned_stores, vehicle.current_location
                )
                optimized_sequence = self.two_opt_improvement(initial_route)
            else:
                # Default to nearest neighbor
                optimized_sequence = self.nearest_neighbor_tsp(
                    assigned_stores, vehicle.current_location
                )

            # Calculate route metrics
            route_metrics = self.calculate_route_metrics(
                optimized_sequence, vehicle.current_location
            )

            # Create route object
            route = Route(
                route_id=f"ROUTE_{vehicle_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                vehicle_id=vehicle_id,
                driver_id=vehicle.driver_id,
                stops=self.format_route_stops(optimized_sequence),
                total_distance_km=route_metrics["total_distance"],
                estimated_duration_hours=route_metrics["estimated_duration"],
                total_weight_kg=sum(
                    store.weight_kg for store in optimized_sequence
                ),
                total_packages=sum(
                    store.packages for store in optimized_sequence
                ),
                optimization_method=method.value,
                created_at=datetime.now(),
            )

            optimized_routes.append(route)

        return optimized_routes

    def calculate_route_metrics(
        self, stores: List[Store], start_location: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate total distance and estimated duration for a route."""
        if not stores:
            return {"total_distance": 0.0, "estimated_duration": 0.0}

        total_distance = 0.0
        total_service_time = 0.0
        current_location = start_location

        for store in stores:
            # Add travel distance
            distance = self.calculate_distance(
                current_location, store.coordinates
            )
            total_distance += distance

            # Add service time
            total_service_time += store.estimated_service_time

            current_location = store.coordinates

        # Add return to depot distance
        total_distance += self.calculate_distance(
            current_location, start_location
        )

        # Estimate driving time (assume 70 km/h average speed in urban areas)
        driving_time_hours = total_distance / 70.0
        service_time_hours = total_service_time / 60.0

        # Add buffer time for traffic, breaks, etc. (5% overhead)
        estimated_duration = (driving_time_hours + service_time_hours) * 1.05

        return {
            "total_distance": round(total_distance, 2),
            "estimated_duration": round(estimated_duration, 2),
        }

    def format_route_stops(self, stores: List[Store]) -> List[Dict[str, Any]]:
        """Format stores as route stops with sequence numbers."""
        stops = []
        for i, store in enumerate(stores):
            stop = {
                "sequence": i + 1,
                "store_id": store.store_id,
                "store_name": store.name,
                "address": store.address,
                "coordinates": store.coordinates,
                "delivery_window": store.delivery_window,
                "priority": store.priority,
                "estimated_service_time": store.estimated_service_time,
                "packages": store.packages,
                "weight_kg": store.weight_kg,
            }
            stops.append(stop)
        return stops

    def validate_route_constraints(
        self, route: Route, constraints: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Validate route against business constraints."""
        validation_results = {}

        # Check driving time limit
        max_driving_hours = constraints.get("max_driving_hours", 8)
        validation_results["within_driving_time_limit"] = (
            route.estimated_duration_hours <= max_driving_hours
        )

        # Check weight capacity
        max_weight = constraints.get("max_weight_kg", 1000)
        validation_results["within_weight_capacity"] = (
            route.total_weight_kg <= max_weight
        )

        # Check package capacity
        max_packages = constraints.get("max_packages", 50)
        validation_results["within_package_capacity"] = (
            route.total_packages <= max_packages
        )

        # Check maximum stops
        max_stops = constraints.get("max_stops", 20)
        validation_results["within_stop_limit"] = len(route.stops) <= max_stops

        return validation_results


class PerformanceMonitor:
    """Monitor and analyze route optimization performance."""

    def __init__(self):
        self.performance_metrics = []

    def benchmark_optimization(
        self,
        stores: List[Store],
        vehicles: List[Vehicle],
        methods: List[OptimizationMethod] = None,
    ) -> Dict[str, Any]:
        """Benchmark different optimization methods."""
        if methods is None:
            methods = [
                OptimizationMethod.NEAREST_NEIGHBOR,
                OptimizationMethod.TWO_OPT,
            ]

        optimizer = RouteOptimizer()
        benchmark_results = {}

        for method in methods:
            start_time = datetime.now()

            try:
                routes = optimizer.optimize_multi_vehicle_routes(
                    stores, vehicles, method
                )
                end_time = datetime.now()

                execution_time = (end_time - start_time).total_seconds()

                # Calculate aggregate metrics
                total_distance = sum(
                    route.total_distance_km for route in routes
                )
                total_duration = sum(
                    route.estimated_duration_hours for route in routes
                )
                total_routes = len(routes)

                benchmark_results[method.value] = {
                    "execution_time_seconds": execution_time,
                    "total_routes_generated": total_routes,
                    "total_distance_km": total_distance,
                    "total_estimated_duration_hours": total_duration,
                    "avg_distance_per_route": (
                        total_distance / total_routes
                        if total_routes > 0
                        else 0
                    ),
                    "stores_processed": len(stores),
                    "vehicles_used": total_routes,
                }

            except Exception as e:
                benchmark_results[method.value] = {
                    "error": str(e),
                    "execution_time_seconds": 0,
                }

        return benchmark_results

    def analyze_route_efficiency(self, route: Route) -> Dict[str, float]:
        """Analyze efficiency metrics for a single route."""
        if not route.stops:
            return {"efficiency_score": 0.0}

        # Calculate efficiency metrics
        distance_per_stop = route.total_distance_km / len(route.stops)
        time_per_stop = route.estimated_duration_hours / len(route.stops)
        weight_utilization = (
            route.total_weight_kg / 1000.0
        )  # Assume 1000kg capacity

        # Priority distribution analysis
        priorities = [stop.get("priority", "medium") for stop in route.stops]
        high_priority_ratio = priorities.count("high") / len(priorities)

        # Calculate composite efficiency score (0-100)
        efficiency_score = (
            min(100, 50 / distance_per_stop) * 0.3  # Distance efficiency (30%)
            + min(100, 2 / time_per_stop) * 0.3  # Time efficiency (30%)
            + min(100, weight_utilization * 100)
            * 0.2  # Weight utilization (20%)
            + high_priority_ratio * 100 * 0.2  # Priority handling (20%)
        )

        return {
            "efficiency_score": round(efficiency_score, 2),
            "distance_per_stop_km": round(distance_per_stop, 2),
            "time_per_stop_hours": round(time_per_stop, 2),
            "weight_utilization_percent": round(weight_utilization * 100, 2),
            "high_priority_ratio": round(high_priority_ratio, 2),
        }
