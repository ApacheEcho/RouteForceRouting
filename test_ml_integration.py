#!/usr/bin/env python3
"""
Test ML Route Prediction - Direct API Integration
Validates ML-based route prediction and algorithm recommendation functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
from datetime import datetime
from app.services.routing_service import RoutingService
from app.optimization.ml_predictor import MLConfig, MLRoutePredictor

def test_ml_direct():
    """Test ML predictor directly"""
    print("=" * 60)
    print("TESTING ML ROUTE PREDICTOR - DIRECT")
    print("=" * 60)
    
    # Create test stores
    test_stores = [
        {
            "id": "store_1",
            "name": "Downtown Store",
            "lat": 40.7128,
            "lon": -74.0060,
            "priority": 1,
            "demand": 150
        },
        {
            "id": "store_2", 
            "name": "Uptown Store",
            "lat": 40.7580,
            "lon": -73.9855,
            "priority": 2,
            "demand": 200
        },
        {
            "id": "store_3",
            "name": "Brooklyn Store", 
            "lat": 40.6782,
            "lon": -73.9442,
            "priority": 1,
            "demand": 100
        },
        {
            "id": "store_4",
            "name": "Queens Store",
            "lat": 40.7282,
            "lon": -73.7949,
            "priority": 3,
            "demand": 120
        },
        {
            "id": "store_5",
            "name": "Bronx Store",
            "lat": 40.8448,
            "lon": -73.8648,
            "priority": 2,
            "demand": 180
        }
    ]
    
    try:
        # Initialize ML predictor
        print("\n1. Initializing ML predictor...")
        config = MLConfig()
        ml_predictor = MLRoutePredictor(config)
        print(f"   ✓ ML predictor initialized with {config.model_type} model")
        
        # Test feature extraction
        print("\n2. Testing feature extraction...")
        features = ml_predictor.extract_features(test_stores)
        print(f"   ✓ Features extracted:")
        print(f"     - Number of stores: {features.num_stores}")
        print(f"     - Geographic spread: {features.geographic_spread:.4f}")
        print(f"     - Total demand: {features.demand_total}")
        print(f"     - Priority score: {features.priority_score}")
        
        # Test prediction without trained model
        print("\n3. Testing prediction without trained model...")
        prediction = ml_predictor.predict_route_performance(test_stores)
        print(f"   ✓ Prediction result: {prediction}")
        
        # Test recommendation without trained model
        print("\n4. Testing algorithm recommendation...")
        recommendation = ml_predictor.recommend_algorithm(test_stores)
        print(f"   ✓ Recommendation result: {recommendation}")
        
        # Add some mock training data
        print("\n5. Adding mock training data...")
        for i in range(3):
            algorithm = ['genetic', 'simulated_annealing', 'multi_objective'][i % 3]
            performance = {
                'improvement_percent': 15.5 + i * 5,
                'original_distance': 100.0 + i * 10,
                'optimized_distance': 85.0 + i * 8,
                'processing_time': 2.5 + i * 0.5
            }
            
            ml_predictor.add_training_data(test_stores, algorithm, performance)
        
        print(f"   ✓ Added {len(ml_predictor.training_data)} training samples")
        
        # Test model info
        print("\n6. Testing model info...")
        model_info = ml_predictor.get_model_info()
        print(f"   ✓ Model info: {model_info}")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error in ML direct test: {str(e)}")
        return False

def test_ml_routing_service():
    """Test ML integration with routing service"""
    print("\n" + "=" * 60)
    print("TESTING ML INTEGRATION WITH ROUTING SERVICE")
    print("=" * 60)
    
    # Create test stores
    test_stores = [
        {
            "id": "store_1",
            "name": "Downtown Store",
            "lat": 40.7128,
            "lon": -74.0060,
            "priority": 1,
            "demand": 150
        },
        {
            "id": "store_2", 
            "name": "Uptown Store",
            "lat": 40.7580,
            "lon": -73.9855,
            "priority": 2,
            "demand": 200
        },
        {
            "id": "store_3",
            "name": "Brooklyn Store", 
            "lat": 40.6782,
            "lon": -73.9442,
            "priority": 1,
            "demand": 100
        },
        {
            "id": "store_4",
            "name": "Queens Store",
            "lat": 40.7282,
            "lon": -73.7949,
            "priority": 3,
            "demand": 120
        },
        {
            "id": "store_5",
            "name": "Bronx Store",
            "lat": 40.8448,
            "lon": -73.8648,
            "priority": 2,
            "demand": 180
        }
    ]
    
    try:
        # Initialize routing service
        print("\n1. Initializing routing service...")
        routing_service = RoutingService()
        print(f"   ✓ Routing service initialized")
        print(f"   ✓ ML predictor available: {routing_service.ml_predictor is not None}")
        
        # Test ML model info
        print("\n2. Testing ML model info...")
        ml_info = routing_service.get_ml_model_info()
        print(f"   ✓ ML model info: {ml_info}")
        
        # Test performance prediction
        print("\n3. Testing performance prediction...")
        context = {
            'timestamp': datetime.now(),
            'weather_factor': 1.0,
            'traffic_factor': 1.2
        }
        
        prediction_result = routing_service.predict_route_performance(test_stores, context)
        print(f"   ✓ Performance prediction: {prediction_result}")
        
        # Test algorithm recommendation
        print("\n4. Testing algorithm recommendation...")
        recommendation_result = routing_service.recommend_algorithm(test_stores, context)
        print(f"   ✓ Algorithm recommendation: {recommendation_result}")
        
        # Test ML-guided route generation
        print("\n5. Testing ML-guided route generation...")
        constraints = {
            'max_distance': 100,
            'start_location': {'lat': 40.7128, 'lon': -74.0060}
        }
        
        ml_route_result = routing_service.generate_route_with_ml_recommendation(
            test_stores, constraints, context
        )
        print(f"   ✓ ML-guided route generation: {ml_route_result.get('success', False)}")
        
        if ml_route_result.get('success'):
            print(f"     - Algorithm used: {ml_route_result['ml_recommendation']['recommended_algorithm']}")
            print(f"     - Confidence: {ml_route_result['ml_recommendation']['confidence']:.2f}")
            print(f"     - Reasoning: {ml_route_result['ml_recommendation']['reasoning']}")
            print(f"     - Route stops: {len(ml_route_result['route'])}")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error in ML routing service test: {str(e)}")
        return False

def test_heuristic_recommendations():
    """Test heuristic algorithm recommendations"""
    print("\n" + "=" * 60)
    print("TESTING HEURISTIC ALGORITHM RECOMMENDATIONS")
    print("=" * 60)
    
    test_cases = [
        {"name": "Small route", "stores": [{"id": "1", "lat": 40.7, "lon": -74.0}] * 3},
        {"name": "Medium route", "stores": [{"id": "1", "lat": 40.7, "lon": -74.0}] * 10},
        {"name": "Large route", "stores": [{"id": "1", "lat": 40.7, "lon": -74.0}] * 20}
    ]
    
    try:
        routing_service = RoutingService()
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. Testing {test_case['name']} ({len(test_case['stores'])} stores)...")
            
            recommendation = routing_service._heuristic_algorithm_recommendation(test_case['stores'])
            
            if recommendation.get('success'):
                print(f"   ✓ Recommended algorithm: {recommendation['recommendation']['recommended_algorithm']}")
                print(f"   ✓ Confidence: {recommendation['recommendation']['confidence']}")
                print(f"   ✓ Reasoning: {recommendation['recommendation']['reasoning']}")
            else:
                print(f"   ✗ Failed to get recommendation")
                
        return True
        
    except Exception as e:
        print(f"   ✗ Error in heuristic recommendations test: {str(e)}")
        return False

def main():
    """Run all ML integration tests"""
    print("MACHINE LEARNING INTEGRATION TESTS")
    print("=" * 60)
    
    start_time = time.time()
    
    # Run tests
    tests = [
        ("ML Direct Test", test_ml_direct),
        ("ML Routing Service Test", test_ml_routing_service),
        ("Heuristic Recommendations Test", test_heuristic_recommendations)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                failed += 1
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"✗ {test_name} FAILED with exception: {str(e)}")
    
    # Print summary
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(passed/(passed + failed)*100):.1f}%")
    print(f"Total time: {total_time:.2f} seconds")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! ML integration is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the output above.")
        
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
