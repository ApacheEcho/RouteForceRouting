"""
Type Definitions for RouteForce Routing System - AUTO-PILOT ENHANCEMENT
Comprehensive type definitions for better code safety and IDE support
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Tuple, TypedDict, Union


# Core Data Types
class StoreDict(TypedDict):
    """Type definition for store data"""

    id: int | str
    name: str
    latitude: float
    longitude: float
    address: str | None
    priority: int | None
    demand: float | None


class RouteConstraints(TypedDict, total=False):
    """Type definition for routing constraints"""

    max_distance: float | None
    max_time: int | None
    avoid_tolls: bool | None
    avoid_highways: bool | None
    start_time: str | None
    end_time: str | None


class OptimizationOptions(TypedDict, total=False):
    """Type definition for optimization options"""

    algorithm: str
    ga_population_size: int | None
    ga_generations: int | None
    ga_mutation_rate: float | None
    ga_crossover_rate: float | None
    sa_initial_temp: float | None
    sa_cooling_rate: float | None


class RouteMetadata(TypedDict):
    """Type definition for route metadata"""

    algorithm_used: str
    processing_time: float
    optimization_score: float
    route_stores: int
    total_distance: float | None
    estimated_time: float | None


class AlgorithmMetrics(TypedDict, total=False):
    """Type definition for algorithm-specific metrics"""

    algorithm: str
    generations: int | None
    population_size: int | None
    improvement_percent: float | None
    initial_distance: float | None
    final_distance: float | None
    best_fitness: float | None
    convergence_rate: float | None


# Enums for better type safety
class AlgorithmType(Enum):
    """Available optimization algorithms"""

    DEFAULT = "default"
    GENETIC = "genetic"
    SIMULATED_ANNEALING = "simulated_annealing"
    MULTI_OBJECTIVE = "multi_objective"


class CacheType(Enum):
    """Available cache backends"""

    REDIS = "redis"
    MEMORY = "memory"
    FILE = "file"


class SecurityLevel(Enum):
    """Security levels for operations"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Protocol definitions for better interface contracts
class OptimizationAlgorithm(Protocol):
    """Protocol for optimization algorithms"""

    def optimize(
        self, stores: list[StoreDict], constraints: RouteConstraints | None = None
    ) -> tuple[list[StoreDict], AlgorithmMetrics]:
        """Optimize route for given stores and constraints"""
        ...


class CacheBackend(Protocol):
    """Protocol for cache backends"""

    def get(self, key: str) -> Any | None:
        """Get value from cache"""
        ...

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache"""
        ...

    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        ...


# Data classes for complex types
@dataclass
class RouteRequest:
    """Data class for route generation requests"""

    stores: list[StoreDict]
    constraints: RouteConstraints | None = None
    options: OptimizationOptions | None = None
    user_id: int | None = None
    session_id: str | None = None


@dataclass
class RouteResponse:
    """Data class for route generation responses"""

    route: list[StoreDict]
    metadata: RouteMetadata
    algorithm_metrics: AlgorithmMetrics | None = None
    success: bool = True
    error: str | None = None


@dataclass
class SecurityContext:
    """Data class for security context"""

    user_id: int | None
    ip_address: str
    user_agent: str
    api_key: str | None = None
    security_level: SecurityLevel = SecurityLevel.MEDIUM


@dataclass
class PerformanceMetrics:
    """Data class for performance tracking"""

    cpu_usage: float
    memory_usage: float
    response_time: float
    request_count: int
    error_rate: float
    cache_hit_rate: float | None = None


# Type aliases for complex types
StoreList = list[StoreDict]
RouteData = list[StoreDict]
MetricsData = dict[str, Union[int, float, str, list[float]]]
ConfigDict = dict[str, Any]
ErrorContext = dict[str, Any]

# Function type annotations
from collections.abc import Callable

RouteOptimizer = Callable[
    [StoreList, Optional[RouteConstraints]], tuple[RouteData, AlgorithmMetrics]
]
ValidationFunction = Callable[[Any], tuple[bool, str]]
CacheKeyGenerator = Callable[[str], str]
ErrorHandler = Callable[[Exception, ErrorContext], None]

# Generic types for extensibility
from typing import Generic, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class CacheEntry(Generic[T]):
    """Generic cache entry with metadata"""

    value: T
    timestamp: float
    ttl: int | None
    access_count: int


class Result(Generic[T]):
    """Generic result type for operations that may fail"""

    success: bool
    data: T | None
    error: str | None

    @classmethod
    def ok(cls, data: T) -> "Result[T]":
        return cls(success=True, data=data, error=None)

    @classmethod
    def error(cls, error: str) -> "Result[T]":
        return cls(success=False, data=None, error=error)


# Export commonly used types
__all__ = [
    "StoreDict",
    "RouteConstraints",
    "OptimizationOptions",
    "RouteMetadata",
    "AlgorithmMetrics",
    "AlgorithmType",
    "CacheType",
    "SecurityLevel",
    "OptimizationAlgorithm",
    "CacheBackend",
    "RouteRequest",
    "RouteResponse",
    "SecurityContext",
    "PerformanceMetrics",
    "StoreList",
    "RouteData",
    "MetricsData",
    "ConfigDict",
    "ErrorContext",
    "RouteOptimizer",
    "ValidationFunction",
    "CacheKeyGenerator",
    "ErrorHandler",
    "CacheEntry",
    "Result",
]
