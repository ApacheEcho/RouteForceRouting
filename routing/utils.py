import json
import time
import requests
import urllib.parse
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from geopy.distance import geodesic

class GeocodingCache:
    def __init__(self, cache_file: str = "geocoding_cache.json"):
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_cache(self) -> None:
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)

    def get_coordinates(self, address: str) -> Optional[Tuple[float, float]]:
        address = address.strip().lower()
        if address in self.cache:
            return tuple(self.cache[address])

        coords = self._geocode_address(address)
        if coords:
            self.cache[address] = coords
            self._save_cache()
        return coords

    def _geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        try:
            time.sleep(1)  # respectful delay for Nominatim
            url = f"https://nominatim.openstreetmap.org/search"
            params = {
                "q": address,
                "format": "json",
                "limit": 1
            }
            headers = {
                "User-Agent": "RouteForceProBot/1.0"
            }
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data and len(data) > 0:
                return float(data[0]['lat']), float(data[0]['lon'])
        except Exception as e:
            print(f"[Geocoder] Error geocoding '{address}': {e}")
        return None

class AddressCache:
    def __init__(self, cache_file: str = "address_cache.json"):
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_cache(self) -> None:
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)

    def get_encoded_address(self, address: str) -> str:
        address = address.strip().lower()
        if address in self.cache:
            return self.cache[address]

        encoded_address = urllib.parse.quote(address)
        self.cache[address] = encoded_address
        self._save_cache()
        return encoded_address

# Initialize global geocoding cache
geocoding_cache = GeocodingCache()

def calculate_distance(store_a: Dict[str, Any], store_b: Dict[str, Any]) -> float:
    """
    Calculate distance between two store locations.
    
    Args:
        store_a: First store dictionary with 'address' key
        store_b: Second store dictionary with 'address' key
        
    Returns:
        Distance in kilometers
    """
    # Try to get coordinates from stores (if they exist)
    coord_a = None
    coord_b = None
    
    # Check if coordinates already exist
    if 'lat' in store_a and 'lon' in store_a:
        coord_a = (store_a['lat'], store_a['lon'])
    if 'lat' in store_b and 'lon' in store_b:
        coord_b = (store_b['lat'], store_b['lon'])
    
    # If coordinates don't exist, geocode addresses using cache
    if not coord_a:
        coord_a = geocoding_cache.get_coordinates(store_a['address'])
        if coord_a:
            store_a['lat'], store_a['lon'] = coord_a
    
    if not coord_b:
        coord_b = geocoding_cache.get_coordinates(store_b['address'])
        if coord_b:
            store_b['lat'], store_b['lon'] = coord_b
    
    # If geocoding failed, return a large distance
    if not coord_a or not coord_b:
        return float('inf')
    
    # Calculate distance using geodesic
    return geodesic(coord_a, coord_b).km

def calculate_route_distance(route: list[Dict[str, Any]]) -> float:
    """
    Calculate total distance for a route.
    
    Args:
        route: List of store dictionaries
        
    Returns:
        Total distance in kilometers
    """
    if len(route) < 2:
        return 0.0
    
    total_distance = 0.0
    for i in range(len(route) - 1):
        total_distance += calculate_distance(route[i], route[i + 1])
    
    return total_distance

def get_cached_coordinates_count() -> int:
    """
    Get the number of cached coordinates.
    
    Returns:
        Number of cached address-to-coordinate mappings
    """
    return len(geocoding_cache.cache)

def clear_geocoding_cache() -> None:
    """
    Clear the geocoding cache.
    """
    geocoding_cache.cache.clear()
    if geocoding_cache.cache_file.exists():
        geocoding_cache.cache_file.unlink()