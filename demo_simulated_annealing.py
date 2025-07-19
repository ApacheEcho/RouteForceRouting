#!/usr/bin/env python3
"""
Comprehensive demo for Simulated Annealing integration
Tests the SA algorithm with various configurations and provides detailed output
"""
import requests
import json
import time
from typing import List, Dict, Any

# Test both direct and API integration
def test_direct_integration():
    """Test direct SA integration"""
    print("🔥 Testing Direct Simulated Annealing Integration")
    print("=" * 60)
    
    # Import the SA classes
    from app.optimization.simulated_annealing import SimulatedAnnealingOptimizer, SimulatedAnnealingConfig
    
    # Create realistic test data
    stores = [
        {"name": "Store_A", "latitude": 37.7749, "longitude": -122.4194},
        {"name": "Store_B", "latitude": 37.7849, "longitude": -122.4094},
        {"name": "Store_C", "latitude": 37.7649, "longitude": -122.4294},
        {"name": "Store_D", "latitude": 37.7549, "longitude": -122.4394},
        {"name": "Store_E", "latitude": 37.7949, "longitude": -122.3994},
        {"name": "Store_F", "latitude": 37.7449, "longitude": -122.4494},
        {"name": "Store_G", "latitude": 37.8049, "longitude": -122.3894},
        {"name": "Store_H", "latitude": 37.7349, "longitude": -122.4594}
    ]
    
    print(f"Created {len(stores)} test stores with coordinates")
    
    # Test with robust configuration
    config = SimulatedAnnealingConfig(
        initial_temperature=2000.0,
        final_temperature=0.1,
        cooling_rate=0.99,
        max_iterations=10000,
        iterations_per_temp=100,
        reheat_threshold=1000,
        min_improvement_threshold=0.001
    )
    
    print("Configuration:")
    print(f"  Initial temperature: {config.initial_temperature}")
    print(f"  Final temperature: {config.final_temperature}")
    print(f"  Cooling rate: {config.cooling_rate}")
    print(f"  Max iterations: {config.max_iterations}")
    print(f"  Iterations per temp: {config.iterations_per_temp}")
    
    # Run optimization
    sa = SimulatedAnnealingOptimizer(config)
    
    start_time = time.time()
    optimized_route, metrics = sa.optimize(stores)
    processing_time = time.time() - start_time
    
    print(f"\n✅ Direct SA completed in {processing_time:.3f}s")
    print(f"Route length: {len(optimized_route)} stops")
    print(f"Algorithm: {metrics.get('algorithm', 'unknown')}")
    print(f"Initial distance: {metrics.get('initial_distance', 0):.2f}")
    print(f"Final distance: {metrics.get('final_distance', 0):.2f}")
    print(f"Improvement: {metrics.get('improvement_percent', 0):.2f}%")
    print(f"Iterations: {metrics.get('total_iterations', 0)}")
    print(f"Accepted moves: {metrics.get('accepted_moves', 0)}")
    print(f"Acceptance rate: {metrics.get('acceptance_rate', 0):.2f}")
    
    return metrics.get('improvement_percent', 0) > 0

def test_api_integration():
    """Test SA API integration"""
    print("\n🌐 Testing API Simulated Annealing Integration")
    print("=" * 60)
    
    # Test data
    stores = [
        {"name": "Store_A", "latitude": 37.7749, "longitude": -122.4194},
        {"name": "Store_B", "latitude": 37.7849, "longitude": -122.4094},
        {"name": "Store_C", "latitude": 37.7649, "longitude": -122.4294},
        {"name": "Store_D", "latitude": 37.7549, "longitude": -122.4394},
        {"name": "Store_E", "latitude": 37.7949, "longitude": -122.3994},
        {"name": "Store_F", "latitude": 37.7449, "longitude": -122.4494},
        {"name": "Store_G", "latitude": 37.8049, "longitude": -122.3894},
        {"name": "Store_H", "latitude": 37.7349, "longitude": -122.4594}
    ]
    
    print(f"Testing API with {len(stores)} stores")
    
    # Test main API endpoint
    print("\n1. Testing main /routes endpoint with SA:")
    request_data = {
        "stores": stores,
        "constraints": {},
        "options": {
            "algorithm": "simulated_annealing",
            "sa_initial_temperature": 2000.0,
            "sa_final_temperature": 0.1,
            "sa_cooling_rate": 0.99,
            "sa_max_iterations": 5000,
            "sa_iterations_per_temp": 100,
            "sa_reheat_threshold": 1000,
            "sa_min_improvement_threshold": 0.001
        }
    }
    
    try:
        response = requests.post("http://localhost:5002/api/v1/routes", json=request_data)
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Main API endpoint successful")
            print(f"   Algorithm used: {data['metadata'].get('algorithm_used', 'unknown')}")
            print(f"   Processing time: {data['metadata'].get('processing_time', 0):.3f}s")
            print(f"   Optimization score: {data['metadata'].get('optimization_score', 0):.1f}")
            
            # Check algorithm metrics
            if 'algorithm_metrics' in data['metadata']:
                alg_metrics = data['metadata']['algorithm_metrics']
                print(f"   Algorithm metrics keys: {list(alg_metrics.keys())}")
                print(f"   Algorithm from metrics: {alg_metrics.get('algorithm', 'unknown')}")
                if 'improvement_percent' in alg_metrics:
                    print(f"   Improvement: {alg_metrics['improvement_percent']:.2f}%")
        else:
            print(f"❌ Main API endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Main API endpoint error: {str(e)}")
    
    # Test dedicated SA endpoint
    print("\n2. Testing dedicated SA endpoint:")
    sa_request_data = {
        "stores": stores,
        "constraints": {},
        "sa_config": {
            "initial_temperature": 2000.0,
            "final_temperature": 0.1,
            "cooling_rate": 0.99,
            "max_iterations": 5000,
            "iterations_per_temp": 100,
            "reheat_threshold": 1000,
            "min_improvement_threshold": 0.001
        }
    }
    
    try:
        response = requests.post("http://localhost:5002/api/v1/routes/optimize/simulated_annealing", json=sa_request_data)
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Dedicated SA endpoint successful")
            print(f"   Algorithm used: {data['metadata'].get('algorithm_used', 'unknown')}")
            print(f"   Processing time: {data['metadata'].get('processing_time', 0):.3f}s")
            print(f"   Optimization score: {data['metadata'].get('optimization_score', 0):.1f}")
            
            # Check SA specific metrics
            if 'simulated_annealing_metrics' in data:
                sa_metrics = data['simulated_annealing_metrics']
                print(f"   SA metrics keys: {list(sa_metrics.keys())}")
                print(f"   Algorithm from SA metrics: {sa_metrics.get('algorithm', 'unknown')}")
                if 'improvement_percent' in sa_metrics:
                    print(f"   Improvement: {sa_metrics['improvement_percent']:.2f}%")
                if 'total_iterations' in sa_metrics:
                    print(f"   Total iterations: {sa_metrics['total_iterations']}")
                if 'accepted_moves' in sa_metrics:
                    print(f"   Accepted moves: {sa_metrics['accepted_moves']}")
            
            return True
        else:
            print(f"❌ Dedicated SA endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Dedicated SA endpoint error: {str(e)}")
    
    return False

def test_routing_service_integration():
    """Test routing service SA integration"""
    print("\n🔧 Testing Routing Service SA Integration")
    print("=" * 60)
    
    from app.services.routing_service import RoutingService
    
    # Test stores
    stores = [
        {"name": "Store_A", "latitude": 37.7749, "longitude": -122.4194},
        {"name": "Store_B", "latitude": 37.7849, "longitude": -122.4094},
        {"name": "Store_C", "latitude": 37.7649, "longitude": -122.4294},
        {"name": "Store_D", "latitude": 37.7549, "longitude": -122.4394},
        {"name": "Store_E", "latitude": 37.7949, "longitude": -122.3994},
        {"name": "Store_F", "latitude": 37.7449, "longitude": -122.4494}
    ]
    
    print(f"Testing routing service with {len(stores)} stores")
    
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
    
    start_time = time.time()
    route = routing_service.generate_route_from_stores(
        stores, 
        constraints={}, 
        save_to_db=False,
        algorithm='simulated_annealing',
        algorithm_params=algorithm_params
    )
    processing_time = time.time() - start_time
    
    print(f"✅ Routing service SA completed in {processing_time:.3f}s")
    print(f"Route length: {len(route)} stops")
    
    # Get metrics
    metrics = routing_service.get_metrics()
    if metrics:
        print(f"Algorithm used: {metrics.algorithm_used}")
        print(f"Processing time: {metrics.processing_time:.3f}s")
        print(f"Optimization score: {metrics.optimization_score:.1f}")
        
        if metrics.algorithm_metrics:
            print(f"Algorithm metrics type: {type(metrics.algorithm_metrics)}")
            print(f"Algorithm metrics keys: {list(metrics.algorithm_metrics.keys()) if isinstance(metrics.algorithm_metrics, dict) else 'Not a dict'}")
            
            if isinstance(metrics.algorithm_metrics, dict):
                alg_metrics = metrics.algorithm_metrics
                print(f"Algorithm from metrics: {alg_metrics.get('algorithm', 'unknown')}")
                if 'improvement_percent' in alg_metrics:
                    print(f"Improvement: {alg_metrics['improvement_percent']:.2f}%")
                if 'total_iterations' in alg_metrics:
                    print(f"Total iterations: {alg_metrics['total_iterations']}")
        
        return metrics.algorithm_used == 'simulated_annealing'
    
    return False

def main():
    """Run comprehensive SA integration tests"""
    print("🚀 RouteForce Simulated Annealing - Comprehensive Integration Demo")
    print("=" * 70)
    
    # Run tests
    test_results = []
    
    # Test direct integration
    try:
        direct_result = test_direct_integration()
        test_results.append(("Direct Integration", direct_result))
    except Exception as e:
        print(f"❌ Direct integration error: {str(e)}")
        test_results.append(("Direct Integration", False))
    
    # Test routing service integration
    try:
        routing_result = test_routing_service_integration()
        test_results.append(("Routing Service Integration", routing_result))
    except Exception as e:
        print(f"❌ Routing service integration error: {str(e)}")
        test_results.append(("Routing Service Integration", False))
    
    # Test API integration
    try:
        api_result = test_api_integration()
        test_results.append(("API Integration", api_result))
    except Exception as e:
        print(f"❌ API integration error: {str(e)}")
        test_results.append(("API Integration", False))
    
    # Print summary
    print("\n" + "=" * 70)
    print("🎯 Comprehensive Test Results")
    print("=" * 70)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:30} | {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} integration tests passed")
    
    if passed == total:
        print("🎉 All Simulated Annealing integration tests passed!")
        print("\n📋 Summary:")
        print("✅ Simulated Annealing algorithm is properly integrated")
        print("✅ Direct SA optimization works correctly")
        print("✅ Routing service SA integration works")
        print("✅ API endpoints support SA optimization")
        print("✅ SA provides significant route improvements")
        return True
    else:
        print("⚠️  Some integration tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
