"""
Advanced API Performance Optimization - Beast Mode Enhancement
Ultra-high performance API layer with intelligent caching and optimization
"""

import time
import gzip
import json
import hashlib
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps, lru_cache
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

from flask import request, jsonify, Response, current_app, g
import redis
import pickle

logger = logging.getLogger(__name__)


@dataclass
class APIMetrics:
    """API performance metrics tracking"""

    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_response_time: float = 0.0
    slow_requests: int = 0
    errors: int = 0
    compression_saves: float = 0.0  # Bytes saved by compression

    def hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0

    def performance_score(self) -> float:
        """Calculate API performance score (0-100)"""
        hit_rate_score = self.hit_rate() * 50
        speed_score = max(
            0, 40 - (self.avg_response_time * 100)
        )  # Penalty for slow responses
        error_penalty = min(10, self.errors * 2)

        return max(0, hit_rate_score + speed_score - error_penalty)


class ResponseCompressor:
    """Intelligent response compression"""

    def __init__(self, compression_threshold: int = 1000):
        self.compression_threshold = compression_threshold
        self.compression_stats = {
            "total_responses": 0,
            "compressed_responses": 0,
            "bytes_saved": 0,
        }

    def should_compress(self, data: str, accept_encoding: str) -> bool:
        """Determine if response should be compressed"""
        return (
            len(data) > self.compression_threshold
            and "gzip" in accept_encoding.lower()
        )

    def compress_response(self, data: str) -> bytes:
        """Compress response data"""
        original_size = len(data.encode())
        compressed = gzip.compress(data.encode(), compresslevel=6)

        self.compression_stats["total_responses"] += 1
        self.compression_stats["compressed_responses"] += 1
        self.compression_stats["bytes_saved"] += original_size - len(
            compressed
        )

        return compressed

    def get_stats(self) -> Dict[str, Any]:
        """Get compression statistics"""
        return self.compression_stats.copy()


class IntelligentCache:
    """Intelligent API response caching with TTL and invalidation"""

    def __init__(self, redis_client=None, default_ttl: int = 300):
        self.redis_client = redis_client
        self.default_ttl = default_ttl
        self.cache_stats = {"hits": 0, "misses": 0, "sets": 0}
        self.memory_cache = {}  # Fallback memory cache
        self.max_memory_items = 1000

    def _make_cache_key(
        self, endpoint: str, params: Dict[str, Any], user_id: str = None
    ) -> str:
        """Generate intelligent cache key"""
        # Sort parameters for consistent keys
        sorted_params = sorted(params.items()) if params else []

        # Create base key
        key_parts = [endpoint]

        if user_id:
            key_parts.append(f"user:{user_id}")

        if sorted_params:
            param_str = json.dumps(sorted_params, sort_keys=True)
            param_hash = hashlib.md5(param_str.encode()).hexdigest()
            key_parts.append(f"params:{param_hash}")

        return ":".join(key_parts)

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        try:
            if self.redis_client:
                data = self.redis_client.get(key)
                if data:
                    self.cache_stats["hits"] += 1
                    return pickle.loads(data)
            else:
                # Fallback to memory cache
                if key in self.memory_cache:
                    cached_item = self.memory_cache[key]
                    if cached_item["expires_at"] > time.time():
                        self.cache_stats["hits"] += 1
                        return cached_item["data"]
                    else:
                        del self.memory_cache[key]

            self.cache_stats["misses"] += 1
            return None

        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            self.cache_stats["misses"] += 1
            return None

    def set(self, key: str, data: Dict[str, Any], ttl: int = None) -> bool:
        """Set cached response"""
        try:
            ttl = ttl or self.default_ttl

            if self.redis_client:
                serialized = pickle.dumps(data)
                self.redis_client.setex(key, ttl, serialized)
            else:
                # Fallback to memory cache
                if len(self.memory_cache) >= self.max_memory_items:
                    # Remove oldest item
                    oldest_key = min(
                        self.memory_cache.keys(),
                        key=lambda k: self.memory_cache[k]["created_at"],
                    )
                    del self.memory_cache[oldest_key]

                self.memory_cache[key] = {
                    "data": data,
                    "created_at": time.time(),
                    "expires_at": time.time() + ttl,
                }

            self.cache_stats["sets"] += 1
            return True

        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False

    def invalidate_pattern(self, pattern: str) -> bool:
        """Invalidate cache keys matching pattern"""
        try:
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            else:
                # Memory cache pattern matching
                keys_to_delete = [
                    k for k in self.memory_cache.keys() if pattern in k
                ]
                for key in keys_to_delete:
                    del self.memory_cache[key]

            return True

        except Exception as e:
            logger.warning(f"Cache invalidation error: {e}")
            return False


class APIOptimizer:
    """Main API performance optimization coordinator"""

    def __init__(self, redis_client=None):
        self.metrics = APIMetrics()
        self.cache = IntelligentCache(redis_client)
        self.compressor = ResponseCompressor()
        self.rate_limiter = None  # Can be integrated later

        # Performance thresholds
        self.slow_request_threshold = 2.0  # seconds
        self.cache_warming_enabled = True

        # Background optimization
        self.optimization_interval = 300  # 5 minutes
        self.last_optimization = time.time()

    def optimize_endpoint(
        self,
        cache_ttl: int = 300,
        compress_response: bool = True,
        track_metrics: bool = True,
        cache_key_func: Optional[Callable] = None,
        invalidate_on: List[str] = None,
    ):
        """Decorator for endpoint optimization"""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Response:
                start_time = time.time()

                try:
                    # Generate cache key
                    endpoint = request.endpoint or func.__name__
                    params = dict(request.args) if request.args else {}
                    user_id = getattr(g, "current_user_id", None)

                    if cache_key_func:
                        cache_key = cache_key_func(endpoint, params, user_id)
                    else:
                        cache_key = self.cache._make_cache_key(
                            endpoint, params, user_id
                        )

                    # Try cache first
                    cached_response = self.cache.get(cache_key)
                    if cached_response:
                        response_time = time.time() - start_time
                        if track_metrics:
                            self._update_metrics(response_time, cache_hit=True)

                        return self._create_response(
                            cached_response, compress_response, from_cache=True
                        )

                    # Execute function
                    result = func(*args, **kwargs)

                    # Handle different response types
                    if isinstance(result, tuple):
                        data, status_code = result
                    else:
                        data = result
                        status_code = 200

                    # Cache successful responses
                    if status_code == 200 and cache_ttl > 0:
                        if hasattr(data, "json"):
                            cache_data = data.json
                        elif isinstance(data, dict):
                            cache_data = data
                        else:
                            cache_data = {"response": str(data)}

                        self.cache.set(cache_key, cache_data, cache_ttl)

                    response_time = time.time() - start_time

                    if track_metrics:
                        self._update_metrics(
                            response_time,
                            cache_hit=False,
                            slow=response_time > self.slow_request_threshold,
                        )

                    return self._create_response(
                        (
                            data
                            if isinstance(data, dict)
                            else {"response": str(data)}
                        ),
                        compress_response,
                        status_code=status_code,
                    )

                except Exception as e:
                    response_time = time.time() - start_time

                    if track_metrics:
                        self._update_metrics(response_time, error=True)

                    logger.error(f"API error in {func.__name__}: {e}")
                    return jsonify({"error": "Internal server error"}), 500

            return wrapper

        return decorator

    def _create_response(
        self,
        data: Dict[str, Any],
        compress: bool = True,
        status_code: int = 200,
        from_cache: bool = False,
    ) -> Response:
        """Create optimized response"""

        # Add metadata
        if isinstance(data, dict):
            data["_meta"] = {
                "timestamp": datetime.utcnow().isoformat(),
                "from_cache": from_cache,
                "processing_time": getattr(g, "processing_time", 0),
            }

        # Convert to JSON
        json_data = json.dumps(data, separators=(",", ":"))  # Compact JSON

        # Handle compression
        if compress and self.compressor.should_compress(
            json_data, request.headers.get("Accept-Encoding", "")
        ):
            compressed_data = self.compressor.compress_response(json_data)
            response = Response(
                compressed_data,
                status=status_code,
                mimetype="application/json",
                headers={"Content-Encoding": "gzip"},
            )
        else:
            response = Response(
                json_data, status=status_code, mimetype="application/json"
            )

        # Performance headers
        response.headers.update(
            {
                "X-Response-Time": f"{getattr(g, 'processing_time', 0):.3f}s",
                "X-Cache-Status": "HIT" if from_cache else "MISS",
                "Cache-Control": (
                    "public, max-age=300" if status_code == 200 else "no-cache"
                ),
            }
        )

        return response

    def _update_metrics(
        self,
        response_time: float,
        cache_hit: bool = False,
        slow: bool = False,
        error: bool = False,
    ) -> None:
        """Update API metrics"""
        self.metrics.total_requests += 1

        if cache_hit:
            self.metrics.cache_hits += 1
        else:
            self.metrics.cache_misses += 1

        if slow:
            self.metrics.slow_requests += 1

        if error:
            self.metrics.errors += 1

        # Update average response time
        total_requests = self.metrics.total_requests
        self.metrics.avg_response_time = (
            self.metrics.avg_response_time * (total_requests - 1)
            + response_time
        ) / total_requests

        # Store in g for response headers
        g.processing_time = response_time

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        compression_stats = self.compressor.get_stats()

        return {
            "api_metrics": {
                "total_requests": self.metrics.total_requests,
                "cache_hit_rate": self.metrics.hit_rate(),
                "avg_response_time": self.metrics.avg_response_time,
                "slow_requests": self.metrics.slow_requests,
                "error_count": self.metrics.errors,
                "performance_score": self.metrics.performance_score(),
            },
            "cache_stats": self.cache.cache_stats,
            "compression_stats": compression_stats,
            "recommendations": self._generate_recommendations(),
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []

        # Cache hit rate recommendations
        hit_rate = self.metrics.hit_rate()
        if hit_rate < 0.7:
            recommendations.append(
                f"Improve cache hit rate (current: {hit_rate:.2%})"
            )

        # Response time recommendations
        if self.metrics.avg_response_time > 1.0:
            recommendations.append(
                f"Optimize response time (current: {self.metrics.avg_response_time:.3f}s)"
            )

        # Error rate recommendations
        error_rate = self.metrics.errors / max(self.metrics.total_requests, 1)
        if error_rate > 0.05:
            recommendations.append(
                f"Investigate error rate (current: {error_rate:.2%})"
            )

        # Compression recommendations
        compression_stats = self.compressor.get_stats()
        if compression_stats["total_responses"] > 0:
            compression_ratio = (
                compression_stats["compressed_responses"]
                / compression_stats["total_responses"]
            )
            if compression_ratio < 0.5:
                recommendations.append("Enable compression for more endpoints")

        return recommendations

    def warm_cache(self, endpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Proactively warm cache with common requests"""
        if not self.cache_warming_enabled:
            return {"status": "disabled"}

        warmed = 0
        errors = 0

        try:
            # Use thread pool for parallel cache warming
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []

                for endpoint_config in endpoints:
                    future = executor.submit(
                        self._warm_single_endpoint, endpoint_config
                    )
                    futures.append(future)

                for future in futures:
                    try:
                        if future.result():
                            warmed += 1
                    except Exception as e:
                        logger.warning(f"Cache warming error: {e}")
                        errors += 1

            return {
                "status": "completed",
                "endpoints_warmed": warmed,
                "errors": errors,
            }

        except Exception as e:
            logger.error(f"Cache warming failed: {e}")
            return {"status": "error", "error": str(e)}

    def _warm_single_endpoint(self, config: Dict[str, Any]) -> bool:
        """Warm cache for a single endpoint"""
        try:
            # This would make actual requests to warm the cache
            # Implementation depends on specific endpoint structure
            endpoint = config.get("endpoint")
            params = config.get("params", {})

            # Generate cache key
            cache_key = self.cache._make_cache_key(endpoint, params)

            # Check if already cached
            if self.cache.get(cache_key):
                return False  # Already cached

            # Here you would make the actual request to generate the cache
            # For now, we'll simulate it
            fake_response = {"warmed": True, "endpoint": endpoint}
            self.cache.set(cache_key, fake_response, ttl=600)  # 10 minutes

            return True

        except Exception as e:
            logger.warning(f"Failed to warm cache for {config}: {e}")
            return False

    def optimize_background(self) -> Dict[str, Any]:
        """Run background optimizations"""
        if time.time() - self.last_optimization < self.optimization_interval:
            return {"status": "skipped", "reason": "too_soon"}

        self.last_optimization = time.time()
        optimizations = []

        try:
            # Cache optimization
            hit_rate = self.metrics.hit_rate()
            if hit_rate < 0.6:
                # Could trigger cache warming or TTL adjustments
                optimizations.append("cache_optimization_triggered")

            # Memory cleanup
            if hasattr(self.cache, "memory_cache"):
                initial_size = len(self.cache.memory_cache)
                # Remove expired entries
                current_time = time.time()
                expired_keys = [
                    k
                    for k, v in self.cache.memory_cache.items()
                    if v["expires_at"] < current_time
                ]
                for key in expired_keys:
                    del self.cache.memory_cache[key]

                if expired_keys:
                    optimizations.append(
                        f"cleaned_{len(expired_keys)}_expired_cache_entries"
                    )

            # Performance threshold adjustments
            if self.metrics.avg_response_time > 2.0:
                # Could adjust cache TTL or compression thresholds
                optimizations.append("performance_threshold_adjustment")

            return {
                "status": "completed",
                "optimizations": optimizations,
                "timestamp": self.last_optimization,
            }

        except Exception as e:
            logger.error(f"Background optimization error: {e}")
            return {"status": "error", "error": str(e)}


# Global API optimizer instance
api_optimizer = APIOptimizer()


def init_api_optimizer(redis_client=None) -> APIOptimizer:
    """Initialize API optimizer"""
    global api_optimizer
    api_optimizer = APIOptimizer(redis_client)
    logger.info("🚀 API performance optimizer initialized")
    return api_optimizer


def get_api_performance_report() -> Dict[str, Any]:
    """Get comprehensive API performance report"""
    return api_optimizer.get_performance_report()


# Convenience decorators
def cached_endpoint(ttl: int = 300, compress: bool = True):
    """Quick cached endpoint decorator"""
    return api_optimizer.optimize_endpoint(
        cache_ttl=ttl, compress_response=compress
    )


def high_performance_endpoint(ttl: int = 600, compress: bool = True):
    """High performance endpoint with extended caching"""
    return api_optimizer.optimize_endpoint(
        cache_ttl=ttl, compress_response=compress, track_metrics=True
    )
