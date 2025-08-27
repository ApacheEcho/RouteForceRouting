"""
Modern Distance Calculation Utilities - Clean, testable, performant
"""

import logging
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from geopy.distance import geodesic

from app.services.metrics_service import track_distance_calculation

logger = logging.getLogger(__name__)


@dataclass
class Coordinates:
    """Type-safe coordinate representation"""

    latitude: float
    longitude: float

    def __post_init__(self):
        # Validate coordinate ranges
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"Invalid latitude: {self.latitude}")
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"Invalid longitude: {self.longitude}")

    def to_tuple(self) -> tuple[float, float]:
        """Convert to (lat, lon) tuple"""
        return (self.latitude, self.longitude)


class DistanceCalculator:
    """Modern distance calculation with multiple algorithms"""

    @staticmethod
    @track_distance_calculation
    def haversine_distance(coord1: Coordinates, coord2: Coordinates) -> float:
        """
        Calculate distance using Haversine formula (faster, less accurate)

        Args:
            coord1: First coordinate point
            coord2: Second coordinate point

        Returns:
            Distance in kilometers
        """
        # Convert to radians
        lat1, lon1 = math.radians(coord1.latitude), math.radians(coord1.longitude)
        lat2, lon2 = math.radians(coord2.latitude), math.radians(coord2.longitude)

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        # Earth's radius in kilometers
        earth_radius_km = 6371.0
        return earth_radius_km * c

    @staticmethod
    @track_distance_calculation
    def geodesic_distance(coord1: Coordinates, coord2: Coordinates) -> float:
        """
        Calculate distance using geodesic method (more accurate)

        Args:
            coord1: First coordinate point
            coord2: Second coordinate point

        Returns:
            Distance in kilometers
        """
        return geodesic(coord1.to_tuple(), coord2.to_tuple()).km

    @staticmethod
    def manhattan_distance(coord1: Coordinates, coord2: Coordinates) -> float:
        """
        Calculate Manhattan distance (useful for city grid systems)

        Args:
            coord1: First coordinate point
            coord2: Second coordinate point

        Returns:
            Distance in kilometers (approximate)
        """
        # Approximate conversion: 1 degree ≈ 111 km
        lat_diff = abs(coord1.latitude - coord2.latitude) * 111
        lon_diff = (
            abs(coord1.longitude - coord2.longitude)
            * 111
            * math.cos(math.radians((coord1.latitude + coord2.latitude) / 2))
        )
        return lat_diff + lon_diff


class CoordinateExtractor:
    """Extract coordinates from various store data formats"""

    @staticmethod
    def extract_coordinates(store: dict[str, Any]) -> Coordinates | None:
        """
        Extract coordinates from store dictionary with multiple format support

        Args:
            store: Store dictionary that may contain coordinates in various formats

        Returns:
            Coordinates object if found, None otherwise
        """
        # Try different coordinate key combinations
        coordinate_keys = [
            ("lat", "lon"),
            ("lat", "lng"),
            ("latitude", "longitude"),
            ("lat", "long"),
            ("y", "x"),  # Some GIS systems use x/y
        ]

        for lat_key, lon_key in coordinate_keys:
            if lat_key in store and lon_key in store:
                try:
                    lat = float(store[lat_key])
                    lon = float(store[lon_key])
                    return Coordinates(lat, lon)
                except (ValueError, TypeError):
                    continue

        # Check for nested location object
        if "location" in store:
            location = store["location"]
            if isinstance(location, dict):
                return CoordinateExtractor.extract_coordinates(location)

        return None


class RouteDistanceCalculator:
    """Calculate distances for routes and store collections"""

    def __init__(self, distance_method: str = "geodesic"):
        """
        Initialize with preferred distance calculation method

        Args:
            distance_method: "geodesic", "haversine", or "manhattan"
        """
        self.distance_method = distance_method
        self._calculator = DistanceCalculator()

    def _calculate_distance(self, coord1: Coordinates, coord2: Coordinates) -> float:
        """Calculate distance using configured method"""
        if self.distance_method == "haversine":
            return self._calculator.haversine_distance(coord1, coord2)
        elif self.distance_method == "manhattan":
            return self._calculator.manhattan_distance(coord1, coord2)
        else:  # Default to geodesic
            return self._calculator.geodesic_distance(coord1, coord2)

    def calculate_store_distance(
        self, store1: dict[str, Any], store2: dict[str, Any]
    ) -> float:
        """
        Calculate distance between two stores

        Args:
            store1: First store dictionary
            store2: Second store dictionary

        Returns:
            Distance in kilometers, or float('inf') if coordinates unavailable
        """
        coord1 = CoordinateExtractor.extract_coordinates(store1)
        coord2 = CoordinateExtractor.extract_coordinates(store2)

        if coord1 is None or coord2 is None:
            logger.warning(
                f"Missing coordinates for distance calculation: {store1.get('name', 'Unknown')} -> {store2.get('name', 'Unknown')}"
            )
            return float("inf")

        return self._calculate_distance(coord1, coord2)

    def calculate_route_distance(self, route: list[dict[str, Any]]) -> float:
        """
        Calculate total distance for a route

        Args:
            route: List of store dictionaries representing the route

        Returns:
            Total distance in kilometers
        """
        if len(route) < 2:
            return 0.0

        total_distance = 0.0
        for i in range(len(route) - 1):
            distance = self.calculate_store_distance(route[i], route[i + 1])
            if distance == float("inf"):
                logger.warning(f"Infinite distance detected in route at position {i}")
                return float("inf")
            total_distance += distance

        return total_distance

    def calculate_distance_matrix(
        self, stores: list[dict[str, Any]]
    ) -> list[list[float]]:
        """
        Calculate distance matrix for all store pairs

        Args:
            stores: List of store dictionaries

        Returns:
            2D list representing distance matrix
        """
        n = len(stores)
        matrix = [[0.0 for _ in range(n)] for _ in range(n)]

        for i in range(n):
            for j in range(i + 1, n):
                distance = self.calculate_store_distance(stores[i], stores[j])
                matrix[i][j] = distance
                matrix[j][i] = distance  # Symmetric matrix

        return matrix


class ProximityClusterer:
    """Cluster stores by proximity for route optimization"""

    def __init__(self, distance_calculator: RouteDistanceCalculator):
        self.distance_calculator = distance_calculator

    def cluster_by_radius(
        self, stores: list[dict[str, Any]], radius_km: float = 2.0
    ) -> list[list[dict[str, Any]]]:
        """
        Cluster stores within a specified radius

        Args:
            stores: List of store dictionaries
            radius_km: Maximum distance for clustering in kilometers

        Returns:
            List of clusters, each containing nearby stores
        """
        clusters = []
        remaining_stores = stores.copy()

        while remaining_stores:
            # Start new cluster with first remaining store
            seed_store = remaining_stores.pop(0)
            cluster = [seed_store]

            # Find stores within radius of any store in current cluster
            i = 0
            while i < len(remaining_stores):
                store = remaining_stores[i]
                # Check if store is within radius of any store in cluster
                within_radius = any(
                    self.distance_calculator.calculate_store_distance(
                        store, cluster_store
                    )
                    <= radius_km
                    for cluster_store in cluster
                )

                if within_radius:
                    cluster.append(remaining_stores.pop(i))
                else:
                    i += 1

            clusters.append(cluster)

        return clusters


# Factory functions for easy setup
def create_distance_calculator(method: str = "geodesic") -> RouteDistanceCalculator:
    """Create a distance calculator with specified method"""
    return RouteDistanceCalculator(method)


def create_proximity_clusterer(method: str = "geodesic") -> ProximityClusterer:
    """Create a proximity clusterer with specified distance method"""
    distance_calc = create_distance_calculator(method)
    return ProximityClusterer(distance_calc)


# Legacy compatibility functions
def calculate_distance(store_a: dict[str, Any], store_b: dict[str, Any]) -> float:
    """Legacy compatibility function"""
    calculator = create_distance_calculator()
    return calculator.calculate_store_distance(store_a, store_b)


def calculate_route_distance(route: list[dict[str, Any]]) -> float:
    """Legacy compatibility function"""
    calculator = create_distance_calculator()
    return calculator.calculate_route_distance(route)
