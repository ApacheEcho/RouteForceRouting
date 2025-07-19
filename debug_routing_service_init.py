#!/usr/bin/env python3

"""Debug script to check RoutingService initialization"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.routing_service import RoutingService

print("Testing RoutingService initialization...")

try:
    # Initialize routing service
    service = RoutingService()
    print(f"✓ RoutingService initialized successfully")
    
    # Check if ml_predictor attribute exists
    if hasattr(service, 'ml_predictor'):
        print(f"✓ ml_predictor attribute exists: {service.ml_predictor}")
        
        # Check if it's None or an actual MLRoutePredictor
        if service.ml_predictor is None:
            print("⚠️  ml_predictor is None - check initialization error")
        else:
            print(f"✓ ml_predictor is initialized: {type(service.ml_predictor)}")
            
            # Test if ML methods are available
            methods = ['predict_route_performance', 'recommend_algorithm', 'add_training_data']
            for method in methods:
                if hasattr(service, method):
                    print(f"✓ Method {method} exists")
                else:
                    print(f"✗ Method {method} missing")
    else:
        print("✗ ml_predictor attribute does not exist")
        
    # List all attributes
    print("\nAll attributes:")
    for attr in dir(service):
        if not attr.startswith('_'):
            print(f"  - {attr}")
            
except Exception as e:
    print(f"✗ Error initializing RoutingService: {str(e)}")
    import traceback
    traceback.print_exc()
