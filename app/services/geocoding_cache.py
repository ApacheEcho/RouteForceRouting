"""
Enhanced Geocoding Cache Service - AUTO-PILOT PERFORMANCE OPTIMIZATION
Implements Redis-based caching with file fallback for maximum performance
"""

import redis
import json
import logging
from typing import Optional, Dict, Any
from flask import current_app

logger = logging.getLogger(__name__)


class GeocodingCache:
    """High-performance geocoding cache with Redis and file fallback"""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_client = None
        self.redis_available = False
        self.file_cache = {}
        self.cache_file = "geocoding_cache.json"

        # Initialize Redis connection
        self._init_redis(redis_url)

        # Load file cache as fallback
        self._load_file_cache()

    def _init_redis(self, redis_url: str) -> None:
        """Initialize Redis connection with error handling"""
        try:
            self.redis_client = redis.from_url(
                redis_url, decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            self.redis_available = True
            logger.info("✅ Redis cache initialized successfully")
        except Exception as e:
            self.redis_available = False
            logger.warning(f"⚠️ Redis unavailable, using file cache: {e}")

    def get(self, address: str) -> Optional[Dict[str, float]]:
        """Get coordinates from cache with Redis priority"""
        cache_key = self._normalize_address(address)

        # Try Redis first (fastest)
        if self.redis_available:
            try:
                cached_data = self.redis_client.get(f"geocode:{cache_key}")
                if cached_data:
                    logger.debug(f"🎯 Redis cache hit for: {address}")
                    return json.loads(cached_data)
            except Exception as e:
                logger.warning(f"Redis read error: {e}")
                self.redis_available = False

        # Fallback to file cache
        result = self.file_cache.get(cache_key)
        if result:
            logger.debug(f"📁 File cache hit for: {address}")

        return result

    def set(self, address: str, coordinates: Dict[str, float]) -> None:
        """Store coordinates in both Redis and file cache"""
        cache_key = self._normalize_address(address)

        # Store in Redis (primary)
        if self.redis_available:
            try:
                self.redis_client.setex(
                    f"geocode:{cache_key}",
                    86400 * 30,  # 30 days TTL
                    json.dumps(coordinates),
                )
                logger.debug(f"💾 Stored in Redis: {address}")
            except Exception as e:
                logger.warning(f"Redis write error: {e}")
                self.redis_available = False

        # Always update file cache as backup
        self.file_cache[cache_key] = coordinates
        self._save_file_cache()
        logger.debug(f"📁 Stored in file cache: {address}")

    def _normalize_address(self, address: str) -> str:
        """Normalize address for consistent caching"""
        return address.lower().strip().replace(" ", "_").replace(",", "_")

    def _load_file_cache(self) -> None:
        """Load file-based cache as fallback"""
        try:
            with open(self.cache_file, "r") as f:
                self.file_cache = json.load(f)
            logger.info(
                f"📁 Loaded {len(self.file_cache)} entries from file cache"
            )
        except FileNotFoundError:
            self.file_cache = {}
            logger.info("📁 Creating new file cache")
        except Exception as e:
            logger.error(f"Error loading file cache: {e}")
            self.file_cache = {}

    def _save_file_cache(self) -> None:
        """Save file-based cache with error handling"""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.file_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving file cache: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        redis_keys = 0
        if self.redis_available:
            try:
                redis_keys = len(self.redis_client.keys("geocode:*"))
            except Exception:
                pass

        return {
            "redis_available": self.redis_available,
            "redis_entries": redis_keys,
            "file_entries": len(self.file_cache),
            "total_entries": redis_keys + len(self.file_cache),
        }

    def clear_cache(self) -> None:
        """Clear all cache entries"""
        if self.redis_available:
            try:
                keys = self.redis_client.keys("geocode:*")
                if keys:
                    self.redis_client.delete(*keys)
                logger.info("🗑️ Cleared Redis cache")
            except Exception as e:
                logger.error(f"Error clearing Redis cache: {e}")

        self.file_cache.clear()
        self._save_file_cache()
        logger.info("🗑️ Cleared file cache")


# Global cache instance
_geocoding_cache = None


def get_geocoding_cache() -> GeocodingCache:
    """Get or create global geocoding cache instance"""
    global _geocoding_cache
    if _geocoding_cache is None:
        redis_url = current_app.config.get(
            "REDIS_URL", "redis://localhost:6379/0"
        )
        _geocoding_cache = GeocodingCache(redis_url)
    return _geocoding_cache
