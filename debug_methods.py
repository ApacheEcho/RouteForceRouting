#!/usr/bin/env python3
"""
Debug script to check routing service methods
"""
from app.services.routing_service import RoutingService


def debug_methods():
    """Debug routing service methods"""
    print("🔍 Debugging Routing Service Methods")
    print("=" * 60)

    # Create routing service
    routing_service = RoutingService()

    # Get all methods
    methods = [
        method
        for method in dir(routing_service)
        if not method.startswith("__")
    ]

    print("Available methods:")
    for method in sorted(methods):
        print(f"  - {method}")

    # Check if SA method exists
    if hasattr(routing_service, "_generate_route_simulated_annealing"):
        print("\n✅ _generate_route_simulated_annealing method exists")
    else:
        print("\n❌ _generate_route_simulated_annealing method does not exist")

    # Check for genetic method
    if hasattr(routing_service, "_generate_route_genetic"):
        print("✅ _generate_route_genetic method exists")
    else:
        print("❌ _generate_route_genetic method does not exist")

    # Check for main generation method
    if hasattr(routing_service, "_generate_route_with_algorithm"):
        print("✅ _generate_route_with_algorithm method exists")
    else:
        print("❌ _generate_route_with_algorithm method does not exist")


if __name__ == "__main__":
    debug_methods()
