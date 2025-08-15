"""
Main Routing Service - Uses the unified routing service implementation
This is the primary entry point for all routing functionality
"""

# Import the unified routing service
from app.services.routing_service_unified import (
    UnifiedRoutingMetrics as RoutingMetrics,
)
from app.services.routing_service_unified import (
    UnifiedRoutingService as RoutingService,
)
from app.services.routing_service_unified import create_unified_routing_service

# Re-export for backwards compatibility
__all__ = [
    "RoutingService",
    "RoutingMetrics",
    "create_unified_routing_service",
]


# Factory function alias
def create_routing_service(user_id=None):
    """Create a routing service instance"""
    return create_unified_routing_service(user_id)
