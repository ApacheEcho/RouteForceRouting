#!/usr/bin/env python3
"""
Debug script to check routing service SA integration
"""
from app.services.routing_service import RoutingService

def debug_routing_service():
    """Debug routing service SA integration"""
    print("🔍 Debugging Routing Service SA Integration")
    print("=" * 60)
    
    # Test stores
    stores = [
        {"name": "Store_A", "latitude": 37.7749, "longitude": -122.4194},
        {"name": "Store_B", "latitude": 37.7849, "longitude": -122.4094},
        {"name": "Store_C", "latitude": 37.7649, "longitude": -122.4294},
        {"name": "Store_D", "latitude": 37.7549, "longitude": -122.4394}
    ]
    
    print(f"Testing with {len(stores)} stores")
    
    # Test routing service with SA
    routing_service = RoutingService()
    
    # Test SA algorithm parameters
    algorithm_params = {
        'sa_initial_temperature': 2000.0,
        'sa_final_temperature': 0.1,
        'sa_cooling_rate': 0.99,
        'sa_max_iterations': 5000,
        'sa_iterations_per_temp': 100,
        'sa_reheat_threshold': 1000,
        'sa_min_improvement_threshold': 0.001
    }
    
    print(f"Algorithm parameters: {algorithm_params}")
    
    # Test the algorithm selection path
    print("\nTesting algorithm selection...")
    
    # First test the generate_route_from_stores method
    route = routing_service.generate_route_from_stores(
        stores, 
        constraints={}, 
        save_to_db=False,
        algorithm='simulated_annealing',
        algorithm_params=algorithm_params
    )
    
    print(f"Route generated: {len(route)} stops")
    
    # Get metrics
    metrics = routing_service.get_metrics()
    if metrics:
        print(f"Metrics object: {metrics}")
        print(f"Algorithm used: {metrics.algorithm_used}")
        print(f"Processing time: {metrics.processing_time:.3f}s")
        print(f"Optimization score: {metrics.optimization_score:.1f}")
        
        if metrics.algorithm_metrics:
            print(f"Algorithm metrics: {metrics.algorithm_metrics}")
    
    # Test directly calling the internal method
    print("\nTesting internal _generate_route_with_algorithm method...")
    
    # Build the filters the same way as generate_route_from_stores
    algorithm_filters = {'algorithm': 'simulated_annealing'}
    algorithm_filters.update(algorithm_params)
    
    print(f"Algorithm filters: {algorithm_filters}")
    
    # Call the internal method directly
    route2, metrics2 = routing_service._generate_route_with_algorithm(
        stores, {}, algorithm_filters
    )
    
    print(f"Internal method route: {len(route2)} stops")
    print(f"Internal method metrics: {metrics2}")
    
    # Test the SA method directly
    print("\nTesting _generate_route_simulated_annealing method...")
    
    route3, metrics3 = routing_service._generate_route_simulated_annealing(
        stores, {}, algorithm_filters
    )
    
    print(f"SA method route: {len(route3)} stops")
    print(f"SA method metrics: {metrics3}")

if __name__ == "__main__":
    debug_routing_service()
