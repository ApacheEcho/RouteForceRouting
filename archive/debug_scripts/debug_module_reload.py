#!/usr/bin/env python3

"""Debug script to check module reloading"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import importlib
import logging

logging.basicConfig(level=logging.DEBUG)

# First, import and check the module
print("Testing module import and reload...")

try:
    # Import the module
    from app.services import routing_service

    print(f"✓ Module imported successfully")

    # Check the class definition
    RoutingService = routing_service.RoutingService
    print(f"✓ Class found: {RoutingService}")

    # Check the init method
    init_method = RoutingService.__init__
    print(f"✓ Init method: {init_method}")

    # Reload the module
    importlib.reload(routing_service)
    print(f"✓ Module reloaded")

    # Try to initialize the service again
    service = routing_service.RoutingService()
    print(f"✓ Service initialized after reload")

    # Check attributes
    print(
        f"Service attributes: {[attr for attr in dir(service) if not attr.startswith('_')]}"
    )

    # Check if ml_predictor exists
    if hasattr(service, "ml_predictor"):
        print(f"✓ ml_predictor exists: {service.ml_predictor}")
    else:
        print("✗ ml_predictor missing")

    # Check the actual file content at the init method
    print("\nChecking file content at init...")
    with open(
        "/Users/frank/RouteForceRouting/app/services/routing_service.py", "r"
    ) as f:
        lines = f.readlines()
        for i, line in enumerate(lines[76:100], 77):
            print(f"{i:3d}: {line.rstrip()}")

except Exception as e:
    print(f"✗ Error: {str(e)}")
    import traceback

    traceback.print_exc()
