#!/usr/bin/env python3
"""
Test ML API Endpoints
Validates ML-based route prediction and algorithm recommendation API endpoints
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import requests
from datetime import datetime

def test_ml_api_endpoints():
    """Test ML API endpoints"""
    print("=" * 60)
    print("TESTING ML API ENDPOINTS")
    print("=" * 60)
    
    base_url = "http://localhost:5000/api/v1"
    
    # Test data
    test_data = {
        "stores": [
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
        ],
        "context": {
            "weather_factor": 1.0,
            "traffic_factor": 1.2,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    # Test health endpoint (should include ML endpoints)
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            ml_endpoints = [ep for ep in health_data.get('endpoints', {}).keys() if 'ml' in ep]
            print(f"   ✓ Health endpoint OK, ML endpoints found: {ml_endpoints}")
        else:
            print(f"   ✗ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Health endpoint error: {str(e)}")
    
    # Test ML model info endpoint
    print("\n2. Testing ML model info endpoint...")
    try:
        response = requests.get(f"{base_url}/ml/model-info")
        if response.status_code == 200:
            model_info = response.json()
            print(f"   ✓ ML model info: {model_info}")
        else:
            print(f"   ✗ ML model info failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ ML model info error: {str(e)}")
    
    # Test ML prediction endpoint
    print("\n3. Testing ML prediction endpoint...")
    try:
        response = requests.post(f"{base_url}/ml/predict", json=test_data)
        if response.status_code == 200:
            prediction = response.json()
            print(f"   ✓ ML prediction: {prediction}")
        else:
            print(f"   ✗ ML prediction failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ✗ ML prediction error: {str(e)}")
    
    # Test ML recommendation endpoint
    print("\n4. Testing ML recommendation endpoint...")
    try:
        response = requests.post(f"{base_url}/ml/recommend", json=test_data)
        if response.status_code == 200:
            recommendation = response.json()
            print(f"   ✓ ML recommendation: {recommendation}")
        else:
            print(f"   ✗ ML recommendation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ✗ ML recommendation error: {str(e)}")
    
    # Test ML-guided route generation
    print("\n5. Testing ML-guided route generation...")
    try:
        ml_route_data = {
            **test_data,
            "constraints": {
                "max_distance": 100,
                "start_location": {"lat": 40.7128, "lon": -74.0060}
            }
        }
        
        response = requests.post(f"{base_url}/routes/generate/ml", json=ml_route_data)
        if response.status_code == 200:
            route_result = response.json()
            print(f"   ✓ ML-guided route generation: {route_result.get('success', False)}")
            
            if route_result.get('success'):
                print(f"     - Algorithm used: {route_result.get('ml_recommendation', {}).get('algorithm', 'Unknown')}")
                print(f"     - Confidence: {route_result.get('ml_recommendation', {}).get('confidence', 0):.2f}")
                print(f"     - Route stops: {len(route_result.get('route', []))}")
        else:
            print(f"   ✗ ML-guided route generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ✗ ML-guided route generation error: {str(e)}")
    
    # Test ML training endpoint
    print("\n6. Testing ML training endpoint...")
    try:
        response = requests.post(f"{base_url}/ml/train", json={})
        if response.status_code == 200:
            training_result = response.json()
            print(f"   ✓ ML training: {training_result}")
        else:
            print(f"   ✗ ML training failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ✗ ML training error: {str(e)}")

def test_error_handling():
    """Test ML API error handling"""
    print("\n" + "=" * 60)
    print("TESTING ML API ERROR HANDLING")
    print("=" * 60)
    
    base_url = "http://localhost:5000/api/v1"
    
    # Test missing stores data
    print("\n1. Testing missing stores data...")
    try:
        response = requests.post(f"{base_url}/ml/predict", json={})
        if response.status_code == 400:
            print("   ✓ Correctly rejected missing stores data")
        else:
            print(f"   ✗ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error testing missing stores: {str(e)}")
    
    # Test empty stores array
    print("\n2. Testing empty stores array...")
    try:
        response = requests.post(f"{base_url}/ml/predict", json={"stores": []})
        if response.status_code == 400:
            print("   ✓ Correctly rejected empty stores array")
        else:
            print(f"   ✗ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error testing empty stores: {str(e)}")
    
    # Test invalid JSON
    print("\n3. Testing invalid JSON...")
    try:
        response = requests.post(f"{base_url}/ml/predict", data="invalid json")
        if response.status_code == 400:
            print("   ✓ Correctly rejected invalid JSON")
        else:
            print(f"   ✗ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error testing invalid JSON: {str(e)}")

def main():
    """Run all ML API tests"""
    print("MACHINE LEARNING API TESTS")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000/api/v1/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not running or not responding correctly")
            print("Please start the server with: python app.py")
            return False
    except Exception as e:
        print("❌ Cannot connect to server")
        print("Please start the server with: python app.py")
        return False
    
    print("✓ Server is running and responding")
    
    start_time = time.time()
    
    # Run tests
    test_ml_api_endpoints()
    test_error_handling()
    
    # Print summary
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total time: {total_time:.2f} seconds")
    print("\n🎉 ML API tests completed!")
    print("Check the output above for any errors or issues.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
