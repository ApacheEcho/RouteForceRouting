"""
Legacy routing utilities - Modernized with clean service architecture
This module provides backward compatibility while using modern services internally
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from app.services.distance_service import create_distance_calculator
# Import modern services
from app.services.geocoding_service import create_geocoding_service

logger = logging.getLogger(__name__)

# Create global service instances for backward compatibility
_geocoding_service = create_geocoding_service()
_distance_calculator = create_distance_calculator()


# Legacy compatibility classes (deprecated - use modern services instead)
class GeocodingCache:
    """
    Legacy geocoding cache - DEPRECATED
    Use app.services.geocoding_service.ModernGeocodingService instead
    """

    def __init__(self, cache_file: str = "geocoding_cache.json"):
        logger.warning(
            "GeocodingCache is deprecated. Use ModernGeocodingService instead."
        )
        self.service = create_geocoding_service()

    def get_coordinates(self, address: str) -> Optional[Tuple[float, float]]:
        """Get coordinates for address"""
        return self.service.get_coordinates(address)

    @property
    def cache(self) -> Dict:
        """Access to cache data (for compatibility)"""
        return {"size": self.service.get_cache_size()}


class AddressCache:
    """
    Legacy address cache - DEPRECATED
    Modern services handle encoding internally
    """

    def __init__(self, cache_file: str = "address_cache.json"):
        logger.warning(
            "AddressCache is deprecated. Modern services handle encoding internally."
        )

    def get_encoded_address(self, address: str) -> str:
        """Get URL-encoded address"""
        import urllib.parse

        return urllib.parse.quote(address.strip())


# Initialize global geocoding cache for backward compatibility
geocoding_cache = GeocodingCache()


def calculate_distance(store_a: Dict[str, Any], store_b: Dict[str, Any]) -> float:
    """
    Calculate distance between two store locations (legacy compatibility)

    Args:
        store_a: First store dictionary
        store_b: Second store dictionary

    Returns:
        Distance in kilometers
    """
    return _distance_calculator.calculate_store_distance(store_a, store_b)


def calculate_route_distance(route: List[Dict[str, Any]]) -> float:
    """
    Calculate total distance for a route (legacy compatibility)

    Args:
        route: List of store dictionaries

    Returns:
        Total distance in kilometers
    """
    return _distance_calculator.calculate_route_distance(route)


def get_cached_coordinates_count() -> int:
    """
    Get the number of cached coordinates (legacy compatibility)

    Returns:
        Number of cached address-to-coordinate mappings
    """
    return _geocoding_service.get_cache_size()


def clear_geocoding_cache() -> None:
    """
    Clear the geocoding cache (legacy compatibility)
    """
    _geocoding_service.clear_cache()


# Modern API recommendations
def get_modern_geocoding_service():
    """
    Get the modern geocoding service instance

    Returns:
        ModernGeocodingService instance
    """
    return _geocoding_service


def get_modern_distance_calculator():
    """
    Get the modern distance calculator instance

    Returns:
        RouteDistanceCalculator instance
    """
    return _distance_calculator


# Legacy function exports for backward compatibility
def get_coordinates(address: str) -> Optional[Tuple[float, float]]:
    """
    Legacy function: Get coordinates for an address
    DEPRECATED: Use app.services.geocoding_service directly
    """
    return _geocoding_service.get_coordinates(address)
