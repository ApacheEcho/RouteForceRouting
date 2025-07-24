"""
Modern Geocoding Service - Clean, testable, dependency-injected design
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Protocol, Tuple

import requests

from app.services.metrics_service import track_geocoding

logger = logging.getLogger(__name__)


@dataclass
class GeocodingConfig:
    """Configuration for geocoding services"""

    cache_file: str = "geocoding_cache.json"
    timeout: int = 10
    delay_seconds: float = 1.0
    user_agent: str = "RouteForceProBot/1.0"
    max_retries: int = 3


class GeocodingProvider(Protocol):
    """Protocol for geocoding providers"""

    def geocode(self, address: str) -> Optional[Tuple[float, float]]:
        """Geocode an address to lat/lon coordinates"""
        ...


class CacheStorage(ABC):
    """Abstract cache storage interface"""

    @abstractmethod
    def get(self, key: str) -> Optional[Tuple[float, float]]:
        """Get coordinates from cache"""
        ...

    @abstractmethod
    def set(self, key: str, value: Tuple[float, float]) -> None:
        """Set coordinates in cache"""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear all cached data"""
        ...

    @abstractmethod
    def size(self) -> int:
        """Get cache size"""
        ...


class JSONFileCache(CacheStorage):
    """JSON file-based cache implementation"""

    def __init__(self, cache_file: str):
        self.cache_file = Path(cache_file)
        self._cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Tuple[float, float]]:
        """Load cache from file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    data = json.load(f)
                    # Convert lists back to tuples
                    return {k: tuple(v) for k, v in data.items()}
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Error loading cache file {self.cache_file}: {e}")
        return {}

    def _save_cache(self) -> None:
        """Save cache to file"""
        try:
            with open(self.cache_file, "w") as f:
                # Convert tuples to lists for JSON serialization
                data = {k: list(v) for k, v in self._cache.items()}
                json.dump(data, f, indent=2)
        except IOError as e:
            logger.error(f"Error saving cache file {self.cache_file}: {e}")

    def get(self, key: str) -> Optional[Tuple[float, float]]:
        """Get coordinates from cache"""
        return self._cache.get(key.strip().lower())

    def set(self, key: str, value: Tuple[float, float]) -> None:
        """Set coordinates in cache"""
        self._cache[key.strip().lower()] = value
        self._save_cache()

    def clear(self) -> None:
        """Clear all cached data"""
        self._cache.clear()
        if self.cache_file.exists():
            self.cache_file.unlink()

    def size(self) -> int:
        """Get cache size"""
        return len(self._cache)


class NominatimGeocoder:
    """Nominatim (OpenStreetMap) geocoding provider"""

    def __init__(self, config: GeocodingConfig):
        self.config = config
        self.base_url = "https://nominatim.openstreetmap.org/search"

    @track_geocoding
    def geocode(self, address: str) -> Optional[Tuple[float, float]]:
        """Geocode address using Nominatim"""
        try:
            # Respectful delay for free service
            time.sleep(self.config.delay_seconds)

            params = {"q": address.strip(), "format": "json", "limit": 1}
            headers = {"User-Agent": self.config.user_agent}

            response = requests.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=self.config.timeout,
            )
            response.raise_for_status()

            data = response.json()
            if data and len(data) > 0:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                return (lat, lon)

        except requests.RequestException as e:
            logger.warning(f"Network error geocoding '{address}': {e}")
        except (ValueError, KeyError) as e:
            logger.warning(f"Data parsing error geocoding '{address}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error geocoding '{address}': {e}")

        return None


class ModernGeocodingService:
    """Modern, testable geocoding service with dependency injection"""

    def __init__(
        self,
        cache: CacheStorage,
        provider: GeocodingProvider,
        config: Optional[GeocodingConfig] = None,
    ):
        self.cache = cache
        self.provider = provider
        self.config = config or GeocodingConfig()

    @track_geocoding
    def get_coordinates(self, address: str) -> Optional[Tuple[float, float]]:
        """Get coordinates for an address, using cache when possible"""
        if not address or not address.strip():
            return None

        # Check cache first
        cached_coords = self.cache.get(address)
        if cached_coords:
            return cached_coords

        # Geocode with provider
        coords = self.provider.geocode(address)
        if coords:
            # Cache the result
            self.cache.set(address, coords)
            return coords

        return None

    def clear_cache(self) -> None:
        """Clear the geocoding cache"""
        self.cache.clear()

    def get_cache_size(self) -> int:
        """Get the number of cached coordinates"""
        return self.cache.size()


# Factory function for easy setup
def create_geocoding_service(
    config: Optional[GeocodingConfig] = None,
) -> ModernGeocodingService:
    """Create a properly configured geocoding service"""
    config = config or GeocodingConfig()
    cache = JSONFileCache(config.cache_file)
    provider = NominatimGeocoder(config)
    return ModernGeocodingService(cache, provider, config)


# Legacy compatibility - global instance
_global_service = None


def get_global_geocoding_service() -> ModernGeocodingService:
    """Get the global geocoding service instance (for legacy compatibility)"""
    global _global_service
    if _global_service is None:
        _global_service = create_geocoding_service()
    return _global_service
