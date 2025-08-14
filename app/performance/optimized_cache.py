"""
Advanced Redis Caching Optimization - Beast Mode Enhancement
High-performance caching layer with intelligent cache management
"""

import json
import time
import hashlib
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from contextlib import contextmanager
import redis
import pickle
from flask import current_app
from flask_caching import Cache

logger = logging.getLogger(__name__)


@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    avg_get_time: float = 0.0
    avg_set_time: float = 0.0
    memory_usage: int = 0  # bytes
    timestamp: float = field(default_factory=time.time)
    
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    def efficiency_score(self) -> float:
        """Calculate cache efficiency score (0-100)"""
        hit_rate = self.hit_rate()
        time_penalty = max(0, (self.avg_get_time - 0.001) * 100)  # Penalty for slow gets
        error_penalty = self.errors * 5  # Penalty for errors
        
        score = (hit_rate * 100) - time_penalty - error_penalty
        return max(0.0, min(100.0, score))


class OptimizedRedisCache:
    """Advanced Redis cache with performance optimization"""
    
    def __init__(self, redis_url: str = None, namespace: str = "routeforce"):
        self.redis_url = redis_url or "redis://localhost:6379/0"
        self.namespace = namespace
        self.metrics = CacheMetrics()
        
        # Cache configuration
        self.default_timeout = 300  # 5 minutes
        self.max_key_length = 250
        self.compression_threshold = 1024  # Compress values > 1KB
        
        # Performance settings
        self.enable_compression = True
        self.enable_serialization_optimization = True
        self.batch_size = 100
        
        # Connection pool settings
        self.connection_pool = None
        self.redis_client = None
        
        self._setup_redis()
        
    def _setup_redis(self) -> None:
        """Setup optimized Redis connection"""
        try:
            # Create connection pool for better performance
            self.connection_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                max_connections=20,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )
            
            self.redis_client = redis.Redis(connection_pool=self.connection_pool)
            
            # Test connection
            self.redis_client.ping()
            
            logger.info(f"🚀 Redis cache initialized: {self.redis_url}")
            
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            # Fallback to memory cache
            self.redis_client = None
    
    def _make_key(self, key: str, version: str = None) -> str:
        """Create optimized cache key"""
        if version:
            key = f"{key}:v{version}"
            
        # Add namespace
        full_key = f"{self.namespace}:{key}"
        
        # Handle long keys
        if len(full_key) > self.max_key_length:
            # Create hash for long keys
            key_hash = hashlib.md5(full_key.encode()).hexdigest()
            full_key = f"{self.namespace}:hash:{key_hash}"
            
        return full_key
    
    def _serialize_value(self, value: Any) -> bytes:
        """Optimized value serialization"""
        if self.enable_serialization_optimization:
            # Use pickle for complex objects, json for simple ones
            if isinstance(value, (str, int, float, bool, list, dict)):
                serialized = json.dumps(value).encode()
                prefix = b'json:'
            else:
                serialized = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
                prefix = b'pickle:'
        else:
            serialized = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
            prefix = b'pickle:'
        
        # Optional compression
        if self.enable_compression and len(serialized) > self.compression_threshold:
            import zlib
            compressed = zlib.compress(serialized)
            if len(compressed) < len(serialized):
                return b'compressed:' + prefix + compressed
        
        return prefix + serialized
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Optimized value deserialization"""
        if data.startswith(b'compressed:'):
            import zlib
            data = data[11:]  # Remove 'compressed:' prefix
            if data.startswith(b'json:'):
                data = zlib.decompress(data[5:])
                return json.loads(data.decode())
            elif data.startswith(b'pickle:'):
                data = zlib.decompress(data[7:])
                return pickle.loads(data)
        elif data.startswith(b'json:'):
            return json.loads(data[5:].decode())
        elif data.startswith(b'pickle:'):
            return pickle.loads(data[7:])
        else:
            # Legacy format
            return pickle.loads(data)
    
    def get(self, key: str, default=None, version: str = None) -> Any:
        """Get value from cache with performance tracking"""
        start_time = time.time()
        
        try:
            if not self.redis_client:
                return default
                
            cache_key = self._make_key(key, version)
            data = self.redis_client.get(cache_key)
            
            if data is None:
                self.metrics.misses += 1
                return default
                
            value = self._deserialize_value(data)
            self.metrics.hits += 1
            
            return value
            
        except Exception as e:
            self.metrics.errors += 1
            logger.warning(f"Cache get error for key {key}: {e}")
            return default
            
        finally:
            # Update performance metrics
            get_time = time.time() - start_time
            self._update_avg_get_time(get_time)
    
    def set(self, key: str, value: Any, timeout: int = None, version: str = None) -> bool:
        """Set value in cache with performance tracking"""
        start_time = time.time()
        
        try:
            if not self.redis_client:
                return False
                
            cache_key = self._make_key(key, version)
            serialized_value = self._serialize_value(value)
            timeout = timeout or self.default_timeout
            
            result = self.redis_client.setex(cache_key, timeout, serialized_value)
            self.metrics.sets += 1
            
            return bool(result)
            
        except Exception as e:
            self.metrics.errors += 1
            logger.warning(f"Cache set error for key {key}: {e}")
            return False
            
        finally:
            # Update performance metrics
            set_time = time.time() - start_time
            self._update_avg_set_time(set_time)
    
    def delete(self, key: str, version: str = None) -> bool:
        """Delete key from cache"""
        try:
            if not self.redis_client:
                return False
                
            cache_key = self._make_key(key, version)
            result = self.redis_client.delete(cache_key)
            self.metrics.deletes += 1
            
            return bool(result)
            
        except Exception as e:
            self.metrics.errors += 1
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False
    
    def get_many(self, keys: List[str], version: str = None) -> Dict[str, Any]:
        """Get multiple values efficiently"""
        if not self.redis_client or not keys:
            return {}
        
        try:
            cache_keys = [self._make_key(key, version) for key in keys]
            
            # Use pipeline for better performance
            pipe = self.redis_client.pipeline()
            for cache_key in cache_keys:
                pipe.get(cache_key)
            
            results = pipe.execute()
            
            # Process results
            cache_data = {}
            for i, (original_key, result) in enumerate(zip(keys, results)):
                if result is not None:
                    try:
                        cache_data[original_key] = self._deserialize_value(result)
                        self.metrics.hits += 1
                    except Exception as e:
                        logger.warning(f"Deserialization error for key {original_key}: {e}")
                        self.metrics.errors += 1
                else:
                    self.metrics.misses += 1
                    
            return cache_data
            
        except Exception as e:
            self.metrics.errors += 1
            logger.warning(f"Cache get_many error: {e}")
            return {}
    
    def set_many(self, data: Dict[str, Any], timeout: int = None, version: str = None) -> bool:
        """Set multiple values efficiently"""
        if not self.redis_client or not data:
            return False
        
        try:
            timeout = timeout or self.default_timeout
            
            # Use pipeline for better performance
            pipe = self.redis_client.pipeline()
            
            for key, value in data.items():
                cache_key = self._make_key(key, version)
                serialized_value = self._serialize_value(value)
                pipe.setex(cache_key, timeout, serialized_value)
            
            results = pipe.execute()
            self.metrics.sets += len(data)
            
            return all(results)
            
        except Exception as e:
            self.metrics.errors += 1
            logger.warning(f"Cache set_many error: {e}")
            return False
    
    def clear(self, pattern: str = None) -> bool:
        """Clear cache with optional pattern"""
        try:
            if not self.redis_client:
                return False
                
            if pattern:
                # Clear keys matching pattern
                full_pattern = f"{self.namespace}:{pattern}"
                keys = self.redis_client.keys(full_pattern)
                if keys:
                    self.redis_client.delete(*keys)
            else:
                # Clear all keys in namespace
                keys = self.redis_client.keys(f"{self.namespace}:*")
                if keys:
                    self.redis_client.delete(*keys)
                    
            return True
            
        except Exception as e:
            self.metrics.errors += 1
            logger.warning(f"Cache clear error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            info = self.redis_client.info() if self.redis_client else {}
            
            return {
                "metrics": {
                    "hits": self.metrics.hits,
                    "misses": self.metrics.misses,
                    "hit_rate": self.metrics.hit_rate(),
                    "sets": self.metrics.sets,
                    "deletes": self.metrics.deletes,
                    "errors": self.metrics.errors,
                    "avg_get_time": self.metrics.avg_get_time,
                    "avg_set_time": self.metrics.avg_set_time,
                    "efficiency_score": self.metrics.efficiency_score(),
                },
                "redis_info": {
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory": info.get("used_memory", 0),
                    "used_memory_human": info.get("used_memory_human", "0B"),
                    "keyspace": info.get("db0", {}),
                },
                "configuration": {
                    "namespace": self.namespace,
                    "default_timeout": self.default_timeout,
                    "compression_enabled": self.enable_compression,
                    "compression_threshold": self.compression_threshold,
                }
            }
            
        except Exception as e:
            logger.warning(f"Error getting cache stats: {e}")
            return {"error": str(e)}
    
    def _update_avg_get_time(self, get_time: float) -> None:
        """Update average get time"""
        total_requests = self.metrics.hits + self.metrics.misses
        if total_requests > 0:
            self.metrics.avg_get_time = (
                (self.metrics.avg_get_time * (total_requests - 1) + get_time)
                / total_requests
            )
    
    def _update_avg_set_time(self, set_time: float) -> None:
        """Update average set time"""
        if self.metrics.sets > 0:
            self.metrics.avg_set_time = (
                (self.metrics.avg_set_time * (self.metrics.sets - 1) + set_time)
                / self.metrics.sets
            )
    
    @contextmanager
    def batch_operations(self):
        """Context manager for batch operations"""
        if not self.redis_client:
            yield None
            return
            
        pipe = self.redis_client.pipeline()
        try:
            yield pipe
            pipe.execute()
        except Exception as e:
            logger.error(f"Batch operation error: {e}")
            raise


class CacheOptimizer:
    """Automatic cache optimization system"""
    
    def __init__(self, cache: OptimizedRedisCache):
        self.cache = cache
        self.optimization_interval = 300  # 5 minutes
        self.last_optimization = time.time()
    
    def should_optimize(self) -> bool:
        """Check if optimization should run"""
        return (time.time() - self.last_optimization) > self.optimization_interval
    
    def optimize(self) -> Dict[str, Any]:
        """Run cache optimization"""
        if not self.should_optimize():
            return {"status": "skipped", "reason": "too_soon"}
        
        self.last_optimization = time.time()
        optimizations = []
        
        try:
            stats = self.cache.get_stats()
            metrics = stats.get("metrics", {})
            
            # Hit rate optimization
            hit_rate = metrics.get("hit_rate", 0)
            if hit_rate < 0.7:  # Less than 70% hit rate
                optimizations.append("low_hit_rate_detected")
                # Could trigger cache warming or timeout adjustments
            
            # Error rate optimization
            error_rate = metrics.get("errors", 0) / max(
                metrics.get("hits", 0) + metrics.get("misses", 0), 1
            )
            if error_rate > 0.05:  # More than 5% errors
                optimizations.append("high_error_rate_detected")
            
            # Performance optimization
            avg_get_time = metrics.get("avg_get_time", 0)
            if avg_get_time > 0.01:  # Slower than 10ms
                optimizations.append("slow_get_performance")
            
            return {
                "status": "completed",
                "optimizations": optimizations,
                "metrics": metrics,
                "timestamp": self.last_optimization,
            }
            
        except Exception as e:
            logger.error(f"Cache optimization error: {e}")
            return {"status": "error", "error": str(e)}


# Global optimized cache instance
optimized_cache = OptimizedRedisCache()
cache_optimizer = CacheOptimizer(optimized_cache)


def init_optimized_cache(redis_url: str = None, namespace: str = "routeforce") -> OptimizedRedisCache:
    """Initialize optimized cache"""
    global optimized_cache, cache_optimizer
    
    optimized_cache = OptimizedRedisCache(redis_url=redis_url, namespace=namespace)
    cache_optimizer = CacheOptimizer(optimized_cache)
    
    logger.info("🚀 Optimized cache system initialized")
    return optimized_cache


def get_cache_performance_report() -> Dict[str, Any]:
    """Get comprehensive cache performance report"""
    stats = optimized_cache.get_stats()
    optimization_report = cache_optimizer.optimize()
    
    return {
        "cache_stats": stats,
        "optimization_report": optimization_report,
        "recommendations": _generate_cache_recommendations(stats),
    }


def _generate_cache_recommendations(stats: Dict[str, Any]) -> List[str]:
    """Generate cache optimization recommendations"""
    recommendations = []
    metrics = stats.get("metrics", {})
    
    hit_rate = metrics.get("hit_rate", 0)
    if hit_rate < 0.8:
        recommendations.append(f"Improve cache hit rate (current: {hit_rate:.2%})")
    
    efficiency_score = metrics.get("efficiency_score", 0)
    if efficiency_score < 80:
        recommendations.append(f"Optimize cache efficiency (current: {efficiency_score:.1f}/100)")
    
    errors = metrics.get("errors", 0)
    if errors > 10:
        recommendations.append(f"Investigate cache errors (current: {errors})")
    
    avg_get_time = metrics.get("avg_get_time", 0)
    if avg_get_time > 0.005:  # 5ms
        recommendations.append(f"Optimize cache get performance (current: {avg_get_time*1000:.1f}ms)")
    
    return recommendations
