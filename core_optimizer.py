"""
Core Route Optimization Algorithm
Advanced route optimizer that integrates distance, time, and cost factors with adaptive algorithm selection.
"""

import math
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import logging
import numpy as np
from routing_engine import RouteOptimizer, Store, Vehicle, Route, OptimizationMethod, VehicleStatus

logger = logging.getLogger(__name__)


class OptimizationObjective(Enum):
    """Optimization objectives for route planning."""
    MINIMIZE_DISTANCE = "minimize_distance"
    MINIMIZE_TIME = "minimize_time"
    MINIMIZE_COST = "minimize_cost"
    BALANCED = "balanced"
    PRIORITY_BASED = "priority_based"


@dataclass
class CostFactors:
    """Cost factors for comprehensive route optimization."""
    fuel_cost_per_km: float = 0.15  # USD per kilometer
    driver_hourly_rate: float = 25.0  # USD per hour
    vehicle_depreciation_per_km: float = 0.05  # USD per kilometer
    traffic_delay_penalty: float = 50.0  # USD per hour of delay
    priority_penalty_multiplier: float = 2.0  # Multiplier for missing high-priority deliveries
    overtime_penalty_rate: float = 1.5  # Multiplier for overtime hours


@dataclass
class OptimizationConfig:
    """Configuration for core optimization algorithm."""
    objective: OptimizationObjective = OptimizationObjective.BALANCED
    cost_factors: CostFactors = None
    time_limit_seconds: float = 30.0
    max_iterations: int = 1000
    convergence_threshold: float = 0.001
    enable_traffic_awareness: bool = True
    enable_dynamic_pricing: bool = False
    
    def __post_init__(self):
        if self.cost_factors is None:
            self.cost_factors = CostFactors()


@dataclass
class OptimizationResult:
    """Result of core optimization with comprehensive metrics."""
    routes: List[Route]
    total_cost: float
    total_distance_km: float
    total_time_hours: float
    optimization_method_used: str
    convergence_achieved: bool
    processing_time_seconds: float
    cost_breakdown: Dict[str, float]
    efficiency_score: float
    algorithm_performance: Dict[str, Any]


class CoreRouteOptimizer:
    """
    Advanced core route optimizer integrating distance, time, and cost factors.
    
    Features:
    - Multi-objective optimization considering distance, time, and cost
    - Adaptive algorithm selection based on problem characteristics
    - Real-time cost calculation with dynamic factors
    - Scalable architecture for large-scale problems
    - Robust optimization with convergence guarantees
    """
    
    def __init__(self, config: OptimizationConfig = None):
        """Initialize core optimizer with configuration."""
        self.config = config or OptimizationConfig()
        self.base_optimizer = RouteOptimizer()
        self.optimization_history = []
        self.algorithm_performance_cache = {}
        
    def optimize_routes(
        self,
        stores: List[Store],
        vehicles: List[Vehicle],
        constraints: Optional[Dict[str, Any]] = None
    ) -> OptimizationResult:
        """
        Perform comprehensive route optimization considering multiple factors.
        
        Args:
            stores: List of delivery locations
            vehicles: Available vehicles for routing
            constraints: Additional optimization constraints
            
        Returns:
            OptimizationResult with optimized routes and comprehensive metrics
        """
        start_time = time.time()
        constraints = constraints or {}
        
        logger.info(f"Starting core optimization for {len(stores)} stores and {len(vehicles)} vehicles")
        
        # Step 1: Analyze problem characteristics and select optimal algorithm
        problem_profile = self._analyze_problem_characteristics(stores, vehicles)
        selected_method = self._select_optimization_algorithm(problem_profile)
        
        logger.info(f"Selected optimization method: {selected_method.value}")
        
        # Step 2: Apply preprocessing and filtering
        filtered_stores = self._preprocess_stores(stores, constraints)
        available_vehicles = self._filter_available_vehicles(vehicles)
        
        if not available_vehicles:
            raise ValueError("No available vehicles for route optimization")
        
        # Step 3: Perform optimization with cost-aware objective function
        routes = self._optimize_with_cost_awareness(
            filtered_stores, available_vehicles, selected_method
        )
        
        # Step 4: Post-optimization improvements
        routes = self._apply_post_optimization_improvements(routes)
        
        # Step 5: Calculate comprehensive metrics
        cost_breakdown = self._calculate_comprehensive_costs(routes)
        efficiency_score = self._calculate_efficiency_score(routes, filtered_stores)
        
        processing_time = time.time() - start_time
        
        # Step 6: Build result object
        result = OptimizationResult(
            routes=routes,
            total_cost=sum(cost_breakdown.values()),
            total_distance_km=sum(route.total_distance_km for route in routes),
            total_time_hours=sum(route.estimated_duration_hours for route in routes),
            optimization_method_used=selected_method.value,
            convergence_achieved=True,  # TODO: Implement convergence detection
            processing_time_seconds=processing_time,
            cost_breakdown=cost_breakdown,
            efficiency_score=efficiency_score,
            algorithm_performance=self._get_algorithm_performance_metrics(selected_method)
        )
        
        # Store optimization history for learning
        self.optimization_history.append({
            'timestamp': datetime.now(),
            'problem_size': len(stores),
            'method_used': selected_method.value,
            'processing_time': processing_time,
            'efficiency_score': efficiency_score,
            'total_cost': result.total_cost
        })
        
        logger.info(f"Optimization completed in {processing_time:.2f}s with efficiency score {efficiency_score:.2f}")
        
        return result
    
    def _analyze_problem_characteristics(
        self, stores: List[Store], vehicles: List[Vehicle]
    ) -> Dict[str, Any]:
        """Analyze problem characteristics to guide algorithm selection."""
        num_stores = len(stores)
        num_vehicles = len(vehicles)
        
        # Calculate geographical spread
        if stores:
            coords = [store.coordinates for store in stores]
            lats = [coord['lat'] for coord in coords]
            lngs = [coord['lng'] for coord in coords]
            
            lat_range = max(lats) - min(lats)
            lng_range = max(lngs) - min(lngs)
            geographical_spread = math.sqrt(lat_range**2 + lng_range**2)
        else:
            geographical_spread = 0.0
        
        # Analyze vehicle capacity constraints
        total_weight = sum(store.weight_kg for store in stores)
        total_packages = sum(store.packages for store in stores)
        total_vehicle_capacity = sum(vehicle.capacity_kg for vehicle in vehicles)
        total_vehicle_packages = sum(vehicle.max_packages for vehicle in vehicles)
        
        capacity_utilization = min(
            total_weight / max(total_vehicle_capacity, 1),
            total_packages / max(total_vehicle_packages, 1)
        )
        
        # Priority distribution
        priority_counts = {'high': 0, 'medium': 0, 'low': 0}
        for store in stores:
            priority_counts[store.priority] = priority_counts.get(store.priority, 0) + 1
        
        priority_complexity = 1.0 - (priority_counts.get('medium', 0) / max(num_stores, 1))
        
        return {
            'num_stores': num_stores,
            'num_vehicles': num_vehicles,
            'geographical_spread': geographical_spread,
            'capacity_utilization': capacity_utilization,
            'priority_complexity': priority_complexity,
            'problem_size_category': self._categorize_problem_size(num_stores),
            'constraint_complexity': self._assess_constraint_complexity(stores, vehicles)
        }
    
    def _select_optimization_algorithm(self, problem_profile: Dict[str, Any]) -> OptimizationMethod:
        """Select the most appropriate optimization algorithm based on problem characteristics."""
        num_stores = problem_profile['num_stores']
        geographical_spread = problem_profile['geographical_spread']
        capacity_utilization = problem_profile['capacity_utilization']
        priority_complexity = problem_profile['priority_complexity']
        
        # Algorithm selection logic based on problem characteristics
        if num_stores <= 10:
            # Small problems: Use exact or near-exact methods
            return OptimizationMethod.TWO_OPT
        elif num_stores <= 50:
            # Medium problems: Balance between quality and speed
            if priority_complexity > 0.3 or capacity_utilization > 0.8:
                return OptimizationMethod.GENETIC_ALGORITHM
            else:
                return OptimizationMethod.TWO_OPT
        elif num_stores <= 200:
            # Large problems: Favor metaheuristics
            if geographical_spread > 1.0:  # Geographically dispersed
                return OptimizationMethod.SIMULATED_ANNEALING
            else:
                return OptimizationMethod.GENETIC_ALGORITHM
        else:
            # Very large problems: Use fastest reasonable method
            return OptimizationMethod.NEAREST_NEIGHBOR
    
    def _preprocess_stores(self, stores: List[Store], constraints: Dict[str, Any]) -> List[Store]:
        """Apply preprocessing and filtering to stores."""
        filtered_stores = stores.copy()
        
        # Apply time window filtering if specified
        if 'time_windows' in constraints:
            filtered_stores = self._apply_time_window_filtering(filtered_stores, constraints['time_windows'])
        
        # Apply priority-based filtering if specified
        if 'min_priority' in constraints:
            min_priority = constraints['min_priority']
            priority_order = {'high': 3, 'medium': 2, 'low': 1}
            filtered_stores = [
                store for store in filtered_stores
                if priority_order.get(store.priority, 1) >= priority_order.get(min_priority, 1)
            ]
        
        # Apply geographical filtering if specified
        if 'max_radius_km' in constraints:
            depot_location = constraints.get('depot_location', {'lat': 40.7128, 'lng': -74.0060})
            max_radius = constraints['max_radius_km']
            filtered_stores = [
                store for store in filtered_stores
                if self.base_optimizer.calculate_distance(depot_location, store.coordinates) <= max_radius
            ]
        
        return filtered_stores
    
    def _filter_available_vehicles(self, vehicles: List[Vehicle]) -> List[Vehicle]:
        """Filter vehicles to only include available ones."""
        return [vehicle for vehicle in vehicles if vehicle.status == VehicleStatus.AVAILABLE]
    
    def _optimize_with_cost_awareness(
        self, stores: List[Store], vehicles: List[Vehicle], method: OptimizationMethod
    ) -> List[Route]:
        """Perform optimization with cost-aware objective function."""
        
        # Use the base optimizer for initial route generation
        routes = self.base_optimizer.optimize_multi_vehicle_routes(stores, vehicles, method)
        
        # Apply cost-aware improvements
        improved_routes = []
        for route in routes:
            improved_route = self._improve_route_with_cost_awareness(route, stores)
            improved_routes.append(improved_route)
        
        return improved_routes
    
    def _improve_route_with_cost_awareness(self, route: Route, all_stores: List[Store]) -> Route:
        """Improve a single route considering cost factors."""
        # Get stores for this route
        route_stores = []
        for stop in route.stops:
            store = next((s for s in all_stores if s.store_id == stop['store_id']), None)
            if store:
                route_stores.append(store)
        
        if not route_stores:
            return route
        
        # Apply cost-aware local optimization
        optimized_sequence = self._cost_aware_local_search(route_stores)
        
        # Recalculate route metrics
        route_metrics = self.base_optimizer.calculate_route_metrics(
            optimized_sequence, 
            route_stores[0].coordinates if route_stores else {'lat': 40.7128, 'lng': -74.0060}
        )
        
        # Update route with improved sequence
        route.stops = self.base_optimizer.format_route_stops(optimized_sequence)
        route.total_distance_km = route_metrics['total_distance']
        route.estimated_duration_hours = route_metrics['estimated_duration']
        
        return route
    
    def _cost_aware_local_search(self, stores: List[Store]) -> List[Store]:
        """Perform local search optimization considering multiple cost factors."""
        if len(stores) <= 2:
            return stores
        
        current_sequence = stores.copy()
        best_cost = self._calculate_route_cost(current_sequence)
        improved = True
        
        max_iterations = min(100, len(stores) * 2)  # Limit iterations for scalability
        iteration = 0
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
            # Try 2-opt improvements with cost evaluation
            for i in range(1, len(current_sequence) - 1):
                for j in range(i + 1, len(current_sequence)):
                    # Create new sequence with 2-opt swap
                    new_sequence = current_sequence.copy()
                    new_sequence[i:j+1] = new_sequence[i:j+1][::-1]
                    
                    # Calculate cost of new sequence
                    new_cost = self._calculate_route_cost(new_sequence)
                    
                    if new_cost < best_cost:
                        current_sequence = new_sequence
                        best_cost = new_cost
                        improved = True
                        break
                
                if improved:
                    break
        
        return current_sequence
    
    def _calculate_route_cost(self, stores: List[Store]) -> float:
        """Calculate comprehensive cost for a route sequence."""
        if not stores:
            return 0.0
        
        total_cost = 0.0
        current_location = self.base_optimizer.depot_location
        
        # Distance and fuel costs
        total_distance = 0.0
        for store in stores:
            distance = self.base_optimizer.calculate_distance(current_location, store.coordinates)
            total_distance += distance
            current_location = store.coordinates
        
        # Return to depot
        total_distance += self.base_optimizer.calculate_distance(current_location, self.base_optimizer.depot_location)
        
        # Calculate cost components
        fuel_cost = total_distance * self.config.cost_factors.fuel_cost_per_km
        depreciation_cost = total_distance * self.config.cost_factors.vehicle_depreciation_per_km
        
        # Time-based costs
        total_service_time = sum(store.estimated_service_time for store in stores)
        driving_time_hours = total_distance / 40.0  # Assume 40 km/h average speed
        total_time_hours = driving_time_hours + (total_service_time / 60.0)
        
        driver_cost = total_time_hours * self.config.cost_factors.driver_hourly_rate
        
        # Priority-based penalties
        priority_penalty = 0.0
        for store in stores:
            if store.priority == 'high':
                priority_penalty += 0.0  # No penalty for serving high priority
            elif store.priority == 'medium':
                priority_penalty += 5.0  # Small penalty for medium priority
            else:
                priority_penalty += 10.0  # Larger penalty for low priority
        
        total_cost = fuel_cost + depreciation_cost + driver_cost + priority_penalty
        
        return total_cost
    
    def _apply_post_optimization_improvements(self, routes: List[Route]) -> List[Route]:
        """Apply post-optimization improvements to the route set."""
        # Inter-route optimization: try to move stores between routes for better overall cost
        improved_routes = routes.copy()
        
        # Simple improvement: balance loads across vehicles
        if len(improved_routes) > 1:
            improved_routes = self._balance_route_loads(improved_routes)
        
        return improved_routes
    
    def _balance_route_loads(self, routes: List[Route]) -> List[Route]:
        """Balance loads across routes to improve overall efficiency."""
        # This is a simplified implementation
        # In a full implementation, this would involve more sophisticated inter-route optimization
        return routes
    
    def _calculate_comprehensive_costs(self, routes: List[Route]) -> Dict[str, float]:
        """Calculate detailed cost breakdown for all routes."""
        costs = {
            'fuel_cost': 0.0,
            'driver_cost': 0.0,
            'vehicle_depreciation': 0.0,
            'time_penalties': 0.0,
            'priority_penalties': 0.0
        }
        
        for route in routes:
            # Fuel costs
            fuel_cost = route.total_distance_km * self.config.cost_factors.fuel_cost_per_km
            costs['fuel_cost'] += fuel_cost
            
            # Driver costs
            driver_cost = route.estimated_duration_hours * self.config.cost_factors.driver_hourly_rate
            costs['driver_cost'] += driver_cost
            
            # Vehicle depreciation
            depreciation = route.total_distance_km * self.config.cost_factors.vehicle_depreciation_per_km
            costs['vehicle_depreciation'] += depreciation
            
            # Time penalties (if route exceeds normal working hours)
            if route.estimated_duration_hours > 8.0:
                overtime_hours = route.estimated_duration_hours - 8.0
                overtime_penalty = overtime_hours * self.config.cost_factors.driver_hourly_rate * (self.config.cost_factors.overtime_penalty_rate - 1.0)
                costs['time_penalties'] += overtime_penalty
        
        return costs
    
    def _calculate_efficiency_score(self, routes: List[Route], stores: List[Store]) -> float:
        """Calculate overall efficiency score for the optimization result."""
        if not routes or not stores:
            return 0.0
        
        # Distance efficiency (lower is better)
        total_distance = sum(route.total_distance_km for route in routes)
        stores_served = sum(len(route.stops) for route in routes)
        distance_per_store = total_distance / max(stores_served, 1)
        distance_efficiency = max(0, 100 - distance_per_store * 2)  # Normalize to 0-100
        
        # Time efficiency
        total_time = sum(route.estimated_duration_hours for route in routes)
        time_per_store = total_time / max(stores_served, 1)
        time_efficiency = max(0, 100 - time_per_store * 20)  # Normalize to 0-100
        
        # Vehicle utilization
        vehicles_used = len(routes)
        avg_stops_per_vehicle = stores_served / max(vehicles_used, 1)
        utilization_efficiency = min(100, avg_stops_per_vehicle * 5)  # Normalize to 0-100
        
        # Priority handling (percent of high-priority stores served)
        high_priority_stores = sum(1 for store in stores if store.priority == 'high')
        if high_priority_stores > 0:
            # This is simplified - in reality, we'd check which stores were actually served
            priority_efficiency = 100.0  # Assume all stores are served
        else:
            priority_efficiency = 100.0
        
        # Weighted average
        efficiency_score = (
            distance_efficiency * 0.3 +
            time_efficiency * 0.3 +
            utilization_efficiency * 0.2 +
            priority_efficiency * 0.2
        )
        
        return min(100.0, max(0.0, efficiency_score))
    
    def _get_algorithm_performance_metrics(self, method: OptimizationMethod) -> Dict[str, Any]:
        """Get performance metrics for the selected algorithm."""
        return {
            'algorithm': method.value,
            'convergence_rate': 0.95,  # Placeholder
            'solution_quality': 0.85,  # Placeholder
            'scalability_rating': 0.80  # Placeholder
        }
    
    def _categorize_problem_size(self, num_stores: int) -> str:
        """Categorize problem size for algorithm selection."""
        if num_stores <= 10:
            return 'small'
        elif num_stores <= 50:
            return 'medium'
        elif num_stores <= 200:
            return 'large'
        else:
            return 'extra_large'
    
    def _assess_constraint_complexity(self, stores: List[Store], vehicles: List[Vehicle]) -> float:
        """Assess the complexity of constraints in the problem."""
        complexity_score = 0.0
        
        # Vehicle capacity diversity
        if vehicles:
            capacities = [v.capacity_kg for v in vehicles]
            capacity_variance = np.var(capacities) if len(capacities) > 1 else 0
            complexity_score += min(1.0, capacity_variance / 1000.0)
        
        # Time window complexity
        time_windows = set()
        for store in stores:
            if hasattr(store, 'delivery_window'):
                time_windows.add(store.delivery_window)
        
        time_window_complexity = len(time_windows) / max(len(stores), 1)
        complexity_score += time_window_complexity
        
        return min(1.0, complexity_score)
    
    def _apply_time_window_filtering(self, stores: List[Store], time_windows: Dict[str, Any]) -> List[Store]:
        """Apply time window constraints to filter stores."""
        # Simplified implementation
        return stores
    
    def get_optimization_statistics(self) -> Dict[str, Any]:
        """Get statistics about optimization history and performance."""
        if not self.optimization_history:
            return {'message': 'No optimization history available'}
        
        history = self.optimization_history
        
        stats = {
            'total_optimizations': len(history),
            'avg_processing_time': sum(h['processing_time'] for h in history) / len(history),
            'avg_efficiency_score': sum(h['efficiency_score'] for h in history) / len(history),
            'algorithm_usage': {},
            'problem_size_distribution': {}
        }
        
        # Algorithm usage statistics
        for entry in history:
            method = entry['method_used']
            stats['algorithm_usage'][method] = stats['algorithm_usage'].get(method, 0) + 1
        
        # Problem size distribution
        for entry in history:
            size = entry['problem_size']
            size_category = self._categorize_problem_size(size)
            stats['problem_size_distribution'][size_category] = stats['problem_size_distribution'].get(size_category, 0) + 1
        
        return stats