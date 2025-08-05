#!/usr/bin/env python3
"""
Demonstration script for the Core Route Optimization Algorithm
Shows the optimizer in action with realistic scenarios.
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
from routing_engine import Store, Vehicle, VehicleStatus
from datetime import datetime
import json


def create_demo_stores():
    """Create a set of demo stores for testing."""
    return [
        Store(
            store_id="MANHATTAN_001",
            name="Manhattan Central Market",
            address="100 Broadway, New York, NY",
            coordinates={"lat": 40.7128, "lng": -74.0060},
            delivery_window="09:00-17:00",
            priority="high",
            estimated_service_time=20,
            packages=10,
            weight_kg=45.0
        ),
        Store(
            store_id="BROOKLYN_001",
            name="Brooklyn Heights Store",
            address="200 Montague St, Brooklyn, NY",
            coordinates={"lat": 40.6892, "lng": -73.9942},
            delivery_window="10:00-18:00",
            priority="medium",
            estimated_service_time=15,
            packages=8,
            weight_kg=35.0
        ),
        Store(
            store_id="QUEENS_001",
            name="Queens Plaza Market",
            address="23-01 44th Drive, Long Island City, NY",
            coordinates={"lat": 40.7505, "lng": -73.9370},
            delivery_window="08:00-16:00",
            priority="high",
            estimated_service_time=25,
            packages=12,
            weight_kg=55.0
        ),
        Store(
            store_id="BRONX_001",
            name="Bronx Community Store",
            address="451 E 149th St, Bronx, NY",
            coordinates={"lat": 40.8176, "lng": -73.9182},
            delivery_window="11:00-19:00",
            priority="medium",
            estimated_service_time=18,
            packages=6,
            weight_kg=28.0
        ),
        Store(
            store_id="STATEN_ISLAND_001",
            name="Staten Island Mall Store",
            address="2655 Richmond Avenue, Staten Island, NY",
            coordinates={"lat": 40.5795, "lng": -74.1502},
            delivery_window="09:00-17:00",
            priority="low",
            estimated_service_time=22,
            packages=7,
            weight_kg=32.0
        ),
        Store(
            store_id="MIDTOWN_001",
            name="Midtown Express",
            address="350 5th Avenue, New York, NY",
            coordinates={"lat": 40.7484, "lng": -73.9857},
            delivery_window="12:00-20:00",
            priority="high",
            estimated_service_time=12,
            packages=4,
            weight_kg=18.0
        ),
        Store(
            store_id="LOWER_EAST_001",
            name="Lower East Side Market",
            address="88 Orchard St, New York, NY",
            coordinates={"lat": 40.7184, "lng": -73.9891},
            delivery_window="10:00-18:00",
            priority="medium",
            estimated_service_time=16,
            packages=9,
            weight_kg=38.0
        )
    ]


def create_demo_vehicles():
    """Create a set of demo vehicles."""
    return [
        Vehicle(
            vehicle_id="VAN_NYC_001",
            capacity_kg=800.0,
            max_packages=60,
            max_driving_hours=8.0,
            status=VehicleStatus.AVAILABLE,
            current_location={"lat": 40.7128, "lng": -74.0060},
            driver_id="DRIVER_JOHN"
        ),
        Vehicle(
            vehicle_id="TRUCK_NYC_001",
            capacity_kg=1500.0,
            max_packages=100,
            max_driving_hours=10.0,
            status=VehicleStatus.AVAILABLE,
            current_location={"lat": 40.7128, "lng": -74.0060},
            driver_id="DRIVER_SARAH"
        ),
        Vehicle(
            vehicle_id="VAN_NYC_002",
            capacity_kg=600.0,
            max_packages=40,
            max_driving_hours=8.0,
            status=VehicleStatus.AVAILABLE,
            current_location={"lat": 40.7128, "lng": -74.0060},
            driver_id="DRIVER_MIKE"
        )
    ]


def print_optimization_result(result, scenario_name):
    """Print detailed optimization results."""
    print(f"\n{'='*60}")
    print(f"OPTIMIZATION RESULTS - {scenario_name}")
    print(f"{'='*60}")
    
    print(f"Algorithm Used: {result.optimization_method_used}")
    print(f"Processing Time: {result.processing_time_seconds:.3f} seconds")
    print(f"Convergence Achieved: {result.convergence_achieved}")
    print(f"Efficiency Score: {result.efficiency_score:.2f}/100")
    
    print(f"\n📊 SUMMARY METRICS:")
    print(f"  • Total Routes Generated: {len(result.routes)}")
    print(f"  • Total Distance: {result.total_distance_km:.2f} km")
    print(f"  • Total Time: {result.total_time_hours:.2f} hours")
    print(f"  • Total Cost: ${result.total_cost:.2f}")
    
    print(f"\n💰 COST BREAKDOWN:")
    for cost_type, amount in result.cost_breakdown.items():
        percentage = (amount / result.total_cost * 100) if result.total_cost > 0 else 0
        print(f"  • {cost_type.replace('_', ' ').title()}: ${amount:.2f} ({percentage:.1f}%)")
    
    print(f"\n🚐 ROUTE DETAILS:")
    for i, route in enumerate(result.routes, 1):
        print(f"  Route {i} (Vehicle: {route.vehicle_id}):")
        print(f"    - Stops: {len(route.stops)}")
        print(f"    - Distance: {route.total_distance_km:.2f} km")
        print(f"    - Duration: {route.estimated_duration_hours:.2f} hours")
        print(f"    - Weight: {route.total_weight_kg:.1f} kg")
        print(f"    - Packages: {route.total_packages}")
        
        if route.stops:
            print(f"    - Store Sequence:")
            for stop in route.stops:
                print(f"      {stop['sequence']}. {stop['store_name']} ({stop['priority']} priority)")


def demo_scenario_1_balanced_optimization():
    """Demo Scenario 1: Balanced optimization (default)."""
    print("🎯 DEMO SCENARIO 1: Balanced Optimization")
    print("Optimizing for balance between distance, time, and cost")
    
    optimizer = CoreRouteOptimizer()
    stores = create_demo_stores()
    vehicles = create_demo_vehicles()
    
    result = optimizer.optimize_routes(stores, vehicles)
    print_optimization_result(result, "Balanced Optimization")
    
    return result


def demo_scenario_2_cost_minimization():
    """Demo Scenario 2: Cost minimization focus."""
    print("\n🎯 DEMO SCENARIO 2: Cost Minimization Focus")
    print("Optimizing primarily for cost reduction")
    
    # Configure for cost minimization with higher cost factors
    cost_factors = CostFactors(
        fuel_cost_per_km=0.25,  # Higher fuel cost
        driver_hourly_rate=35.0,  # Higher driver cost
        vehicle_depreciation_per_km=0.08,
        traffic_delay_penalty=100.0,
        overtime_penalty_rate=2.0
    )
    
    config = OptimizationConfig(
        objective=OptimizationObjective.MINIMIZE_COST,
        cost_factors=cost_factors,
        time_limit_seconds=45.0
    )
    
    optimizer = CoreRouteOptimizer(config)
    stores = create_demo_stores()
    vehicles = create_demo_vehicles()
    
    result = optimizer.optimize_routes(stores, vehicles)
    print_optimization_result(result, "Cost Minimization")
    
    return result


def demo_scenario_3_priority_based():
    """Demo Scenario 3: Priority-based optimization."""
    print("\n🎯 DEMO SCENARIO 3: Priority-Based Optimization")
    print("Optimizing with high priority for urgent deliveries")
    
    config = OptimizationConfig(
        objective=OptimizationObjective.PRIORITY_BASED,
        time_limit_seconds=30.0
    )
    
    optimizer = CoreRouteOptimizer(config)
    stores = create_demo_stores()
    vehicles = create_demo_vehicles()
    
    # Add constraint to prioritize high-priority stores
    constraints = {
        'min_priority': 'medium'  # Only medium and high priority stores
    }
    
    result = optimizer.optimize_routes(stores, vehicles, constraints)
    print_optimization_result(result, "Priority-Based Optimization")
    
    return result


def demo_scenario_4_constrained_optimization():
    """Demo Scenario 4: Optimization with geographic and capacity constraints."""
    print("\n🎯 DEMO SCENARIO 4: Constrained Optimization")
    print("Optimizing with geographic and capacity constraints")
    
    optimizer = CoreRouteOptimizer()
    stores = create_demo_stores()
    vehicles = create_demo_vehicles()
    
    # Apply geographic constraint (only stores within 30km of Manhattan)
    constraints = {
        'max_radius_km': 30.0,
        'depot_location': {'lat': 40.7128, 'lng': -74.0060},
        'time_windows': {
            'high_priority': {'start': '09:00', 'end': '17:00'},
            'medium_priority': {'start': '10:00', 'end': '18:00'}
        }
    }
    
    result = optimizer.optimize_routes(stores, vehicles, constraints)
    print_optimization_result(result, "Constrained Optimization")
    
    return result


def demo_performance_comparison():
    """Demo performance comparison across different scenarios."""
    print("\n📈 PERFORMANCE COMPARISON")
    print("="*60)
    
    scenarios = [
        ("Balanced", demo_scenario_1_balanced_optimization),
        ("Cost-Focused", demo_scenario_2_cost_minimization),
        ("Priority-Based", demo_scenario_3_priority_based),
        ("Constrained", demo_scenario_4_constrained_optimization)
    ]
    
    results = {}
    for name, demo_func in scenarios:
        result = demo_func()
        results[name] = {
            'total_cost': result.total_cost,
            'total_distance': result.total_distance_km,
            'total_time': result.total_time_hours,
            'efficiency_score': result.efficiency_score,
            'processing_time': result.processing_time_seconds,
            'num_routes': len(result.routes)
        }
    
    print("\n📊 COMPARISON TABLE:")
    print(f"{'Scenario':<15} {'Cost ($)':<10} {'Distance (km)':<15} {'Time (hrs)':<12} {'Efficiency':<12} {'Routes':<8}")
    print("-" * 80)
    
    for scenario, metrics in results.items():
        print(f"{scenario:<15} "
              f"{metrics['total_cost']:<10.2f} "
              f"{metrics['total_distance']:<15.2f} "
              f"{metrics['total_time']:<12.2f} "
              f"{metrics['efficiency_score']:<12.1f} "
              f"{metrics['num_routes']:<8}")
    
    return results


def demo_algorithm_statistics():
    """Demo optimization statistics and learning."""
    print("\n📊 ALGORITHM STATISTICS DEMO")
    print("="*60)
    
    optimizer = CoreRouteOptimizer()
    
    # Run multiple optimizations to build history
    stores = create_demo_stores()
    vehicles = create_demo_vehicles()
    
    print("Running multiple optimizations to build statistics...")
    
    for i in range(3):
        print(f"  Running optimization {i+1}/3...")
        # Vary store count for different scenarios
        scenario_stores = stores[:3+i*2]  # 3, 5, 7 stores
        result = optimizer.optimize_routes(scenario_stores, vehicles)
    
    # Get and display statistics
    stats = optimizer.get_optimization_statistics()
    
    print(f"\n📈 OPTIMIZATION STATISTICS:")
    print(f"  • Total Optimizations Run: {stats['total_optimizations']}")
    print(f"  • Average Processing Time: {stats['avg_processing_time']:.3f} seconds")
    print(f"  • Average Efficiency Score: {stats['avg_efficiency_score']:.2f}")
    
    print(f"\n🔧 ALGORITHM USAGE:")
    for algorithm, count in stats['algorithm_usage'].items():
        percentage = count / stats['total_optimizations'] * 100
        print(f"  • {algorithm}: {count} times ({percentage:.1f}%)")
    
    print(f"\n📏 PROBLEM SIZE DISTRIBUTION:")
    for size_category, count in stats['problem_size_distribution'].items():
        percentage = count / stats['total_optimizations'] * 100
        print(f"  • {size_category}: {count} problems ({percentage:.1f}%)")


def main():
    """Main demo function."""
    print("🚀 CORE ROUTE OPTIMIZATION ALGORITHM DEMONSTRATION")
    print("=" * 60)
    print("This demo showcases the advanced core route optimization algorithm")
    print("that integrates distance, time, and cost factors with adaptive")
    print("algorithm selection for robust, efficient, and scalable routing.")
    print("=" * 60)
    
    try:
        # Run individual scenario demos
        demo_scenario_1_balanced_optimization()
        demo_scenario_2_cost_minimization()
        demo_scenario_3_priority_based()
        demo_scenario_4_constrained_optimization()
        
        # Run performance comparison
        print("\n" + "="*60)
        comparison_results = demo_performance_comparison()
        
        # Run algorithm statistics demo
        demo_algorithm_statistics()
        
        print("\n✅ DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("The Core Route Optimization Algorithm has demonstrated:")
        print("  • Multi-objective optimization (distance, time, cost)")
        print("  • Adaptive algorithm selection based on problem characteristics")
        print("  • Robust constraint handling and filtering")
        print("  • Comprehensive cost modeling with detailed breakdowns")
        print("  • Scalable architecture suitable for various problem sizes")
        print("  • Efficient optimization with convergence guarantees")
        print("  • Performance monitoring and learning capabilities")
        
    except Exception as e:
        print(f"\n❌ DEMO FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)