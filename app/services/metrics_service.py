"""
Metrics Export Layer - Prometheus-compatible metrics collection and export
Provides logging hooks and metrics collection for routing, geocoding, and distance services
"""

import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Dict, List, Optional
from collections.abc import Callable

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Individual metric data point"""

    name: str
    value: float
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metric_type: str = "gauge"  # gauge, counter, histogram, summary


@dataclass
class ServiceMetrics:
    """Aggregated metrics for a service"""

    service_name: str
    total_requests: int = 0
    total_errors: int = 0
    avg_response_time: float = 0.0
    response_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    error_rate: float = 0.0
    last_activity: float = field(default_factory=time.time)


class MetricsCollector:
    """Central metrics collection system with Prometheus compatibility"""

    def __init__(self, max_metrics: int = 10000):
        self.metrics: dict[str, MetricPoint] = {}
        self.service_metrics: dict[str, ServiceMetrics] = {}
        self.request_durations: dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        self.counters: dict[str, float] = defaultdict(float)
        self.gauges: dict[str, float] = defaultdict(float)
        self.histograms: dict[str, list[float]] = defaultdict(list)
        self.max_metrics = max_metrics
        self._lock = Lock()

        logger.info("Metrics collector initialized")

    def increment_counter(
        self, name: str, value: float = 1.0, labels: dict[str, str] | None = None
    ):
        """Increment a counter metric"""
        with self._lock:
            metric_key = self._create_metric_key(name, labels or {})
            self.counters[metric_key] += value

            # Store as MetricPoint for Prometheus export
            self.metrics[metric_key] = MetricPoint(
                name=name,
                value=self.counters[metric_key],
                labels=labels or {},
                metric_type="counter",
            )

    def set_gauge(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ):
        """Set a gauge metric value"""
        with self._lock:
            metric_key = self._create_metric_key(name, labels or {})
            self.gauges[metric_key] = value

            self.metrics[metric_key] = MetricPoint(
                name=name, value=value, labels=labels or {}, metric_type="gauge"
            )

    def observe_histogram(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ):
        """Add observation to histogram metric"""
        with self._lock:
            metric_key = self._create_metric_key(name, labels or {})
            self.histograms[metric_key].append(value)

            # Keep only recent observations
            if len(self.histograms[metric_key]) > 1000:
                self.histograms[metric_key] = self.histograms[metric_key][-1000:]

            # Store current value as MetricPoint
            self.metrics[metric_key] = MetricPoint(
                name=name, value=value, labels=labels or {}, metric_type="histogram"
            )

    def record_service_request(
        self, service_name: str, duration: float, success: bool = True
    ):
        """Record a service request with timing and success status"""
        with self._lock:
            if service_name not in self.service_metrics:
                self.service_metrics[service_name] = ServiceMetrics(
                    service_name=service_name
                )

            metrics = self.service_metrics[service_name]
            metrics.total_requests += 1
            metrics.response_times.append(duration)
            metrics.last_activity = time.time()

            if not success:
                metrics.total_errors += 1

            # Update calculated metrics
            metrics.avg_response_time = sum(metrics.response_times) / len(
                metrics.response_times
            )
            metrics.error_rate = (
                metrics.total_errors / metrics.total_requests
                if metrics.total_requests > 0
                else 0.0
            )

            # Record as standard metrics
            self.increment_counter(
                f"{service_name}_requests_total",
                labels={"status": "success" if success else "error"},
            )
            self.observe_histogram(f"{service_name}_duration_seconds", duration)
            self.set_gauge(f"{service_name}_error_rate", metrics.error_rate)

    def get_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        with self._lock:
            lines = []

            # Group metrics by name
            metrics_by_name = defaultdict(list)
            for metric in self.metrics.values():
                metrics_by_name[metric.name].append(metric)

            for metric_name, metric_list in metrics_by_name.items():
                # Add HELP and TYPE comments
                lines.append(f"# HELP {metric_name} {metric_name}")
                lines.append(f"# TYPE {metric_name} {metric_list[0].metric_type}")

                for metric in metric_list:
                    labels_str = ""
                    if metric.labels:
                        label_pairs = [f'{k}="{v}"' for k, v in metric.labels.items()]
                        labels_str = "{" + ",".join(label_pairs) + "}"

                    lines.append(f"{metric_name}{labels_str} {metric.value}")

            return "\n".join(lines)

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get summarized metrics for monitoring dashboards"""
        with self._lock:
            summary = {
                "services": {},
                "total_metrics": len(self.metrics),
                "collection_time": time.time(),
            }

            for service_name, metrics in self.service_metrics.items():
                summary["services"][service_name] = {
                    "total_requests": metrics.total_requests,
                    "total_errors": metrics.total_errors,
                    "avg_response_time": round(metrics.avg_response_time, 3),
                    "error_rate": round(metrics.error_rate * 100, 2),
                    "last_activity": metrics.last_activity,
                }

            return summary

    def _create_metric_key(self, name: str, labels: dict[str, str]) -> str:
        """Create unique key for metric with labels"""
        if not labels:
            return name

        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}[{label_str}]"

    def clear_metrics(self):
        """Clear all collected metrics"""
        with self._lock:
            self.metrics.clear()
            self.service_metrics.clear()
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()
            logger.info("All metrics cleared")


# Global metrics collector instance
metrics_collector = MetricsCollector()


def metrics_decorator(service_name: str):
    """Decorator to automatically collect metrics for service methods"""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                metrics_collector.record_service_request(
                    service_name, duration, success
                )

        return wrapper

    return decorator


def track_route_generation(func: Callable) -> Callable:
    """Specific decorator for route generation metrics"""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)

            # Extract metrics from result if available
            if hasattr(result, "route") and hasattr(result, "total_distance"):
                metrics_collector.set_gauge(
                    "route_total_distance", result.total_distance
                )
                metrics_collector.set_gauge("route_store_count", len(result.route))

            return result
        finally:
            duration = time.time() - start_time
            metrics_collector.record_service_request("route_generation", duration)

    return wrapper


def track_geocoding(func: Callable) -> Callable:
    """Specific decorator for geocoding metrics"""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        cache_hit = False
        try:
            result = func(*args, **kwargs)

            # Check if result came from cache
            if hasattr(result, "from_cache"):
                cache_hit = result.from_cache

            return result
        finally:
            duration = time.time() - start_time
            metrics_collector.record_service_request("geocoding", duration)
            if cache_hit:
                metrics_collector.increment_counter("geocoding_cache_hits")
            else:
                metrics_collector.increment_counter("geocoding_api_calls")

    return wrapper


def track_distance_calculation(func: Callable) -> Callable:
    """Specific decorator for distance calculation metrics"""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)

            # Track distance if available in result
            if isinstance(result, (int, float)):
                metrics_collector.observe_histogram("distance_calculated", result)

            return result
        finally:
            duration = time.time() - start_time
            metrics_collector.record_service_request("distance_calculation", duration)

    return wrapper
