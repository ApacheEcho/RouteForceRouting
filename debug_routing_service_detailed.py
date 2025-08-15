#!/usr/bin/env python3

"""Debug script to check RoutingService initialization with more details"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging

logging.basicConfig(level=logging.DEBUG)

from app.services.routing_service import RoutingService
from app.optimization.ml_predictor import MLRoutePredictor, MLConfig

print("Testing RoutingService initialization...")

# First, test if MLRoutePredictor can be initialized directly
try:
    print("Testing MLRoutePredictor direct initialization...")
    ml_predictor = MLRoutePredictor(MLConfig())
    print(f"✓ MLRoutePredictor initialized successfully: {type(ml_predictor)}")
except Exception as e:
    print(f"✗ MLRoutePredictor initialization failed: {str(e)}")

# Now test RoutingService initialization
try:
    print("\nTesting RoutingService initialization...")
    service = RoutingService()
    print(f"✓ RoutingService initialized successfully")

    # Check if ml_predictor attribute exists
    if hasattr(service, "ml_predictor"):
        print(f"✓ ml_predictor attribute exists: {service.ml_predictor}")

        # Check if it's None or an actual MLRoutePredictor
        if service.ml_predictor is None:
            print("⚠️  ml_predictor is None - check initialization error")
        else:
            print(
                f"✓ ml_predictor is initialized: {type(service.ml_predictor)}"
            )
    else:
        print("✗ ml_predictor attribute does not exist")

    # Check the actual constructor code
    print("\nInspecting constructor...")
    import inspect

    source = inspect.getsource(service.__init__)
    print("Constructor source:")
    print(source)

except Exception as e:
    print(f"✗ Error initializing RoutingService: {str(e)}")
    import traceback

    traceback.print_exc()
