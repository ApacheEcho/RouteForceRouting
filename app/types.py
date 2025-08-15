"""
Type Definitions for RouteForce Routing System - AUTO-PILOT ENHANCEMENT
Comprehensive type definitions for better code safety and IDE support
"""

from typing import TypedDict, List, Dict, Any, Optional, Union, Tuple, Protocol
from dataclasses import dataclass
from enum import Enum


# Core Data Types
class StoreDict(TypedDict):
    """Type definition for store data"""

    id: Union[int, str]
    name: str
    latitude: float
    longitude: float
    address: Optional[str]
    priority: Optional[int]
    demand: Optional[float]


class RouteConstraints(TypedDict, total=False):
    """Type definition for routing constraints"""

    max_distance: Optional[float]
    max_time: Optional[int]
    avoid_tolls: Optional[bool]
    avoid_highways: Optional[bool]
    start_time: Optional[str]
    end_time: Optional[str]


class OptimizationOptions(TypedDict, total=False):
    """Type definition for optimization options"""

    algorithm: str
    ga_population_size: Optional[int]
    ga_generations: Optional[int]
    ga_mutation_rate: Optional[float]
    ga_crossover_rate: Optional[float]
    sa_initial_temp: Optional[float]
    sa_cooling_rate: Optional[float]


class RouteMetadata(TypedDict):
    """Type definition for route metadata"""

    algorithm_used: str
    processing_time: float
    optimization_score: float
    route_stores: int
    total_distance: Optional[float]
    estimated_time: Optional[float]


class AlgorithmMetrics(TypedDict, total=False):
    """Type definition for algorithm-specific metrics"""

    algorithm: str
    generations: Optional[int]
    population_size: Optional[int]
    improvement_percent: Optional[float]
    initial_distance: Optional[float]
    final_distance: Optional[float]
    best_fitness: Optional[float]
    convergence_rate: Optional[float]


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
        self,
        stores: List[StoreDict],
        constraints: Optional[RouteConstraints] = None,
    ) -> Tuple[List[StoreDict], AlgorithmMetrics]:
        """Optimize route for given stores and constraints"""
        ...


class CacheBackend(Protocol):
    """Protocol for cache backends"""

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        ...

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        ...

    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        ...


# Data classes for complex types
@dataclass
class RouteRequest:
    """Data class for route generation requests"""

    stores: List[StoreDict]
    constraints: Optional[RouteConstraints] = None
    options: Optional[OptimizationOptions] = None
    user_id: Optional[int] = None
    session_id: Optional[str] = None


@dataclass
class RouteResponse:
    """Data class for route generation responses"""

    route: List[StoreDict]
    metadata: RouteMetadata
    algorithm_metrics: Optional[AlgorithmMetrics] = None
    success: bool = True
    error: Optional[str] = None


@dataclass
class SecurityContext:
    """Data class for security context"""

    user_id: Optional[int]
    ip_address: str
    user_agent: str
    api_key: Optional[str] = None
    security_level: SecurityLevel = SecurityLevel.MEDIUM


@dataclass
class PerformanceMetrics:
    """Data class for performance tracking"""

    cpu_usage: float
    memory_usage: float
    response_time: float
    request_count: int
    error_rate: float
    cache_hit_rate: Optional[float] = None


# Type aliases for complex types
StoreList = List[StoreDict]
RouteData = List[StoreDict]
MetricsData = Dict[str, Union[int, float, str, List[float]]]
ConfigDict = Dict[str, Any]
ErrorContext = Dict[str, Any]

# Function type annotations
from typing import Callable

RouteOptimizer = Callable[
    [StoreList, Optional[RouteConstraints]], Tuple[RouteData, AlgorithmMetrics]
]
ValidationFunction = Callable[[Any], Tuple[bool, str]]
CacheKeyGenerator = Callable[[str], str]
ErrorHandler = Callable[[Exception, ErrorContext], None]

# Generic types for extensibility
from typing import TypeVar, Generic

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class CacheEntry(Generic[T]):
    """Generic cache entry with metadata"""

    value: T
    timestamp: float
    ttl: Optional[int]
    access_count: int


class Result(Generic[T]):
    """Generic result type for operations that may fail"""

    success: bool
    data: Optional[T]
    error: Optional[str]

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
