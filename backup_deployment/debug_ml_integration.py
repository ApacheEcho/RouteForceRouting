#!/usr/bin/env python3
"""
Debug ML Integration Issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_import():
    print("Testing imports...")
    
    try:
        from app.optimization.ml_predictor import MLRoutePredictor, MLConfig
        print("✓ ML predictor imported successfully")
    except Exception as e:
        print(f"✗ Failed to import ML predictor: {e}")
        return False
    
    try:
        from app.services.routing_service import RoutingService
        print("✓ Routing service imported successfully")
    except Exception as e:
        print(f"✗ Failed to import routing service: {e}")
        return False
    
    return True

def test_ml_predictor():
    print("\nTesting ML predictor directly...")
    
    try:
        from app.optimization.ml_predictor import MLRoutePredictor, MLConfig
        config = MLConfig()
        predictor = MLRoutePredictor(config)
        print("✓ ML predictor created successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to create ML predictor: {e}")
        return False

def test_routing_service():
    print("\nTesting routing service...")
    
    try:
        from app.services.routing_service import RoutingService
        rs = RoutingService()
        print("✓ Routing service created successfully")
        
        # Check if ml_predictor attribute exists
        if hasattr(rs, 'ml_predictor'):
            print(f"✓ ml_predictor attribute exists: {rs.ml_predictor}")
        else:
            print("✗ ml_predictor attribute missing")
            print(f"Available attributes: {[attr for attr in dir(rs) if not attr.startswith('_')]}")
            return False
        
        # Test ML methods
        if hasattr(rs, 'predict_route_performance'):
            print("✓ predict_route_performance method exists")
        else:
            print("✗ predict_route_performance method missing")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Failed to create routing service: {e}")
        return False

if __name__ == "__main__":
    print("ML INTEGRATION DEBUG")
    print("=" * 40)
    
    if not test_import():
        sys.exit(1)
    
    if not test_ml_predictor():
        sys.exit(1)
    
    if not test_routing_service():
        sys.exit(1)
    
    print("\n✓ All debug tests passed!")
