"""
Integration example for Core Route Optimization Algorithm
Shows how to integrate the new CoreRouteOptimizer with the existing RouteForce application.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core_optimizer import (
    CoreRouteOptimizer,
    OptimizationConfig,
    OptimizationObjective,
    CostFactors
)
from routing_engine import RouteOptimizer, Store, Vehicle, VehicleStatus


class EnhancedRouteService:
    """
    Enhanced routing service that combines the existing RouteOptimizer 
    with the new CoreRouteOptimizer for advanced optimization capabilities.
    """
    
    def __init__(self):
        """Initialize the enhanced routing service."""
        self.legacy_optimizer = RouteOptimizer()
        self.core_optimizer = CoreRouteOptimizer()
        
    def optimize_routes_basic(self, stores, vehicles, method="nearest_neighbor"):
        """
        Basic route optimization using the existing RouteOptimizer.
        Maintained for backward compatibility.
        """
        # Convert string method to OptimizationMethod enum
        from routing_engine import OptimizationMethod
        
        method_map = {
            "nearest_neighbor": OptimizationMethod.NEAREST_NEIGHBOR,
            "genetic_algorithm": OptimizationMethod.GENETIC_ALGORITHM,
            "simulated_annealing": OptimizationMethod.SIMULATED_ANNEALING,
            "two_opt": OptimizationMethod.TWO_OPT,
            "clarke_wright": OptimizationMethod.CLARKE_WRIGHT
        }
        
        optimization_method = method_map.get(method, OptimizationMethod.NEAREST_NEIGHBOR)
        
        return self.legacy_optimizer.optimize_multi_vehicle_routes(
            stores, vehicles, optimization_method
        )
    
    def optimize_routes_advanced(
        self, 
        stores, 
        vehicles, 
        optimization_config=None, 
        constraints=None
    ):
        """
        Advanced route optimization using the new CoreRouteOptimizer.
        Provides multi-objective optimization with cost awareness.
        """
        if optimization_config is None:
            optimization_config = OptimizationConfig()
            
        optimizer = CoreRouteOptimizer(optimization_config)
        return optimizer.optimize_routes(stores, vehicles, constraints)
    
    def optimize_routes_auto(
        self, 
        stores, 
        vehicles, 
        use_advanced=True, 
        cost_factors=None,
        objective=OptimizationObjective.BALANCED
    ):
        """
        Automatic route optimization that chooses the best approach.
        
        Args:
            stores: List of Store objects
            vehicles: List of Vehicle objects  
            use_advanced: Whether to use advanced CoreRouteOptimizer (default: True)
            cost_factors: Optional CostFactors for advanced optimization
            objective: Optimization objective for advanced mode
            
        Returns:
            Optimization result (routes and metrics)
        """
        
        if use_advanced and len(stores) > 0:
            # Use advanced CoreRouteOptimizer
            config = OptimizationConfig(
                objective=objective,
                cost_factors=cost_factors
            )
            return self.optimize_routes_advanced(stores, vehicles, config)
        else:
            # Fall back to basic optimization
            routes = self.optimize_routes_basic(stores, vehicles)
            # Convert to result format for consistency
            return self._convert_legacy_result(routes)
    
    def _convert_legacy_result(self, routes):
        """Convert legacy route result to new result format."""
        total_distance = sum(route.total_distance_km for route in routes)
        total_time = sum(route.estimated_duration_hours for route in routes)
        
        # Simplified result for legacy compatibility
        class LegacyResult:
            def __init__(self, routes, total_distance, total_time):
                self.routes = routes
                self.total_distance_km = total_distance
                self.total_time_hours = total_time
                self.total_cost = 0.0  # Not calculated in legacy mode
                self.efficiency_score = 50.0  # Default score
                self.optimization_method_used = "legacy"
                
        return LegacyResult(routes, total_distance, total_time)


def demo_integration():
    """Demonstrate integration of the core optimizer with existing system."""
    print("🔗 CORE OPTIMIZER INTEGRATION DEMONSTRATION")
    print("=" * 60)
    
    # Create sample data
    stores = [
        Store(
            store_id="STORE_001",
            name="Downtown Market",
            address="123 Main St",
            coordinates={"lat": 40.7128, "lng": -74.0060},
            delivery_window="09:00-17:00",
            priority="high",
            estimated_service_time=15,
            packages=5,
            weight_kg=25.0
        ),
        Store(
            store_id="STORE_002",
            name="Uptown Shop",
            address="456 Broadway",
            coordinates={"lat": 40.7831, "lng": -73.9712},
            delivery_window="10:00-18:00",
            priority="medium",
            estimated_service_time=20,
            packages=8,
            weight_kg=40.0
        )
    ]
    
    vehicles = [
        Vehicle(
            vehicle_id="VAN_001",
            capacity_kg=500.0,
            max_packages=50,
            max_driving_hours=8.0,
            status=VehicleStatus.AVAILABLE,
            driver_id="DRIVER_001"
        )
    ]
    
    # Initialize enhanced service
    service = EnhancedRouteService()
    
    # Demo 1: Basic optimization (legacy compatibility)
    print("\n📊 DEMO 1: Basic Optimization (Legacy Mode)")
    print("-" * 40)
    basic_result = service.optimize_routes_basic(stores, vehicles)
    print(f"Routes generated: {len(basic_result)}")
    print(f"Total distance: {sum(r.total_distance_km for r in basic_result):.2f} km")
    print(f"Total time: {sum(r.estimated_duration_hours for r in basic_result):.2f} hours")
    
    # Demo 2: Advanced optimization with cost awareness
    print("\n📊 DEMO 2: Advanced Optimization (Core Algorithm)")
    print("-" * 50)
    
    # Configure for cost-aware optimization
    cost_factors = CostFactors(
        fuel_cost_per_km=0.18,
        driver_hourly_rate=28.0,
        vehicle_depreciation_per_km=0.06
    )
    
    config = OptimizationConfig(
        objective=OptimizationObjective.MINIMIZE_COST,
        cost_factors=cost_factors
    )
    
    advanced_result = service.optimize_routes_advanced(stores, vehicles, config)
    print(f"Routes generated: {len(advanced_result.routes)}")
    print(f"Total distance: {advanced_result.total_distance_km:.2f} km")
    print(f"Total time: {advanced_result.total_time_hours:.2f} hours")
    print(f"Total cost: ${advanced_result.total_cost:.2f}")
    print(f"Efficiency score: {advanced_result.efficiency_score:.2f}")
    print(f"Algorithm used: {advanced_result.optimization_method_used}")
    
    # Demo 3: Automatic optimization with smart selection
    print("\n📊 DEMO 3: Automatic Optimization (Smart Selection)")
    print("-" * 52)
    
    auto_result = service.optimize_routes_auto(
        stores, 
        vehicles,
        use_advanced=True,
        objective=OptimizationObjective.BALANCED
    )
    print(f"Routes generated: {len(auto_result.routes)}")
    print(f"Total distance: {auto_result.total_distance_km:.2f} km")
    print(f"Total time: {auto_result.total_time_hours:.2f} hours")
    print(f"Total cost: ${auto_result.total_cost:.2f}")
    print(f"Efficiency score: {auto_result.efficiency_score:.2f}")
    
    print("\n✅ INTEGRATION DEMONSTRATION COMPLETED!")
    print("The enhanced routing service provides:")
    print("  • Backward compatibility with existing RouteOptimizer")
    print("  • Advanced multi-objective optimization capabilities")
    print("  • Automatic algorithm selection based on problem characteristics")
    print("  • Cost-aware routing with detailed cost breakdowns")
    print("  • Seamless integration with existing application architecture")


def create_api_endpoint_example():
    """Example of how to create an API endpoint using the core optimizer."""
    
    api_example = '''
# Example Flask API endpoint using the CoreRouteOptimizer

from flask import Flask, request, jsonify
from core_optimizer import CoreRouteOptimizer, OptimizationConfig, CostFactors
from routing_engine import Store, Vehicle, VehicleStatus

app = Flask(__name__)

@app.route('/api/optimize-routes', methods=['POST'])
def optimize_routes_endpoint():
    """
    API endpoint for advanced route optimization.
    
    Expected JSON payload:
    {
        "stores": [...],  # List of store objects
        "vehicles": [...],  # List of vehicle objects
        "config": {  # Optional optimization configuration
            "objective": "balanced|minimize_cost|minimize_time|priority_based",
            "cost_factors": {
                "fuel_cost_per_km": 0.15,
                "driver_hourly_rate": 25.0,
                ...
            },
            "time_limit_seconds": 30.0
        },
        "constraints": {  # Optional constraints
            "max_radius_km": 50.0,
            "min_priority": "medium"
        }
    }
    """
    try:
        data = request.get_json()
        
        # Parse stores and vehicles from request
        stores = [Store(**store_data) for store_data in data.get('stores', [])]
        vehicles = [Vehicle(**vehicle_data) for vehicle_data in data.get('vehicles', [])]
        
        # Parse optimization configuration
        config_data = data.get('config', {})
        cost_factors = None
        if 'cost_factors' in config_data:
            cost_factors = CostFactors(**config_data['cost_factors'])
        
        config = OptimizationConfig(
            objective=config_data.get('objective', 'balanced'),
            cost_factors=cost_factors,
            time_limit_seconds=config_data.get('time_limit_seconds', 30.0)
        )
        
        # Parse constraints
        constraints = data.get('constraints', {})
        
        # Perform optimization
        optimizer = CoreRouteOptimizer(config)
        result = optimizer.optimize_routes(stores, vehicles, constraints)
        
        # Format response
        response = {
            "success": True,
            "result": {
                "routes": [
                    {
                        "route_id": route.route_id,
                        "vehicle_id": route.vehicle_id,
                        "stops": route.stops,
                        "total_distance_km": route.total_distance_km,
                        "estimated_duration_hours": route.estimated_duration_hours,
                        "total_weight_kg": route.total_weight_kg,
                        "total_packages": route.total_packages
                    }
                    for route in result.routes
                ],
                "metrics": {
                    "total_cost": result.total_cost,
                    "total_distance_km": result.total_distance_km,
                    "total_time_hours": result.total_time_hours,
                    "efficiency_score": result.efficiency_score,
                    "processing_time_seconds": result.processing_time_seconds,
                    "optimization_method_used": result.optimization_method_used
                },
                "cost_breakdown": result.cost_breakdown
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True)
'''
    
    print("\n💻 API ENDPOINT EXAMPLE")
    print("=" * 30)
    print("Here's how to create a Flask API endpoint using the CoreRouteOptimizer:")
    print(api_example)


if __name__ == "__main__":
    demo_integration()
    create_api_endpoint_example()