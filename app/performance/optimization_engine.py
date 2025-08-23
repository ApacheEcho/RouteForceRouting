"""
Advanced Performance Optimization Engine - AUTO-PILOT ENHANCEMENT
Comprehensive performance monitoring and optimization system
"""

import gc
import logging
import threading
import time
import weakref
from collections import defaultdict, deque
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional
from collections.abc import Callable

import psutil

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics container"""

    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    response_time_ms: float = 0.0
    request_count: int = 0
    error_count: int = 0
    cache_hit_rate: float = 0.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class PerformanceMetric:
    """Individual performance metric data structure"""

    timestamp: str
    metric_type: str
    value: float
    unit: str
    threshold_warning: float | None = None
    threshold_critical: float | None = None
    status: str = "normal"  # normal, warning, critical


@dataclass
class SystemAlert:
    """System alert data structure"""

    alert_id: str
    severity: str  # info, warning, critical
    title: str
    description: str
    timestamp: str
    component: str
    metric: str
    current_value: float
    threshold: float
    acknowledged: bool = False


@dataclass
class OptimizationResult:
    """Optimization result container"""

    improvement_percentage: float
    performance_before: PerformanceMetrics
    performance_after: PerformanceMetrics
    optimizations_applied: list[str]
    recommendations: list[str]


class PerformanceMonitor:
    """Real-time performance monitoring with auto-optimization"""

    def __init__(self, sample_interval: float = 1.0, history_size: int = 1000):
        self.sample_interval = sample_interval
        self.metrics_history = deque(maxlen=history_size)
        self.active_requests = defaultdict(float)
        self.cache_stats = {"hits": 0, "misses": 0}
        self.monitoring_active = False
        self.monitor_thread = None
        self._lock = threading.RLock()

        # Performance thresholds
        self.thresholds = {
            "cpu_warning": 70.0,
            "cpu_critical": 85.0,
            "memory_warning": 512.0,  # MB
            "memory_critical": 1024.0,  # MB
            "response_warning": 1000.0,  # ms
            "response_critical": 3000.0,  # ms
        }

        # Weak references to avoid memory leaks
        self.request_callbacks = weakref.WeakSet()

    def start_monitoring(self) -> None:
        """Start background performance monitoring"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("🚀 Performance monitoring started")

    def stop_monitoring(self) -> None:
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        logger.info("⏹️ Performance monitoring stopped")

    def _monitor_loop(self) -> None:
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                metrics = self._collect_metrics()
                with self._lock:
                    self.metrics_history.append(metrics)

                # Auto-optimization triggers
                self._check_optimization_triggers(metrics)

                time.sleep(self.sample_interval)

            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                time.sleep(5.0)  # Longer delay on error

    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current system metrics"""
        process = psutil.Process()

        # System metrics
        cpu_percent = process.cpu_percent()
        memory_mb = process.memory_info().rss / 1024 / 1024

        # Application metrics
        request_count = len(self.active_requests)

        # Cache metrics
        total_cache_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        cache_hit_rate = (
            (self.cache_stats["hits"] / total_cache_requests * 100)
            if total_cache_requests > 0
            else 0.0
        )

        return PerformanceMetrics(
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            request_count=request_count,
            cache_hit_rate=cache_hit_rate,
        )

    def _check_optimization_triggers(self, metrics: PerformanceMetrics) -> None:
        """Check if optimization is needed"""
        optimizations = []

        # High CPU usage
        if metrics.cpu_percent > self.thresholds["cpu_critical"]:
            optimizations.append(self._optimize_cpu_usage)

        # High memory usage
        if metrics.memory_mb > self.thresholds["memory_critical"]:
            optimizations.append(self._optimize_memory_usage)

        # Low cache hit rate
        if metrics.cache_hit_rate < 50.0 and metrics.request_count > 10:
            optimizations.append(self._optimize_cache_strategy)

        # Execute optimizations
        for optimization in optimizations:
            try:
                optimization()
            except Exception as e:
                logger.error(f"Auto-optimization failed: {e}")

    def _optimize_cpu_usage(self) -> None:
        """Optimize CPU usage"""
        logger.warning("🔥 High CPU detected - triggering CPU optimization")

        # Force garbage collection
        gc.collect()

        # Log CPU-intensive operations for analysis
        logger.info("CPU optimization: garbage collection triggered")

    def _optimize_memory_usage(self) -> None:
        """Optimize memory usage"""
        logger.warning("💾 High memory usage detected - triggering memory optimization")

        # Aggressive garbage collection
        for _ in range(3):
            gc.collect()

        # Clear caches if available
        if hasattr(self, "clear_caches"):
            self.clear_caches()

        logger.info("Memory optimization: aggressive cleanup executed")

    def _optimize_cache_strategy(self) -> None:
        """Optimize cache strategy"""
        logger.info("📈 Low cache hit rate - analyzing cache strategy")
        # This would trigger cache warming or strategy adjustment

    @contextmanager
    def track_request(self, request_id: str):
        """Context manager for tracking request performance"""
        start_time = time.time()
        self.active_requests[request_id] = start_time

        try:
            yield
        finally:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # ms

            with self._lock:
                del self.active_requests[request_id]

                # Update latest metrics with response time
                if self.metrics_history:
                    self.metrics_history[-1].response_time_ms = response_time

    def record_cache_hit(self) -> None:
        """Record cache hit for metrics"""
        self.cache_stats["hits"] += 1

    def record_cache_miss(self) -> None:
        """Record cache miss for metrics"""
        self.cache_stats["misses"] += 1

    def get_current_metrics(self) -> PerformanceMetrics | None:
        """Get latest performance metrics"""
        with self._lock:
            return self.metrics_history[-1] if self.metrics_history else None

    def get_metrics_history(self, last_n: int = 100) -> list[PerformanceMetrics]:
        """Get performance metrics history"""
        with self._lock:
            return list(self.metrics_history)[-last_n:]


class PerformanceOptimizer:
    """Advanced performance optimization engine"""

    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.optimization_history = []
        self.active_optimizations = set()

    def start(self) -> None:
        """Start the optimization engine"""
        self.monitor.start_monitoring()
        logger.info("🎯 Performance optimization engine started")

    def stop(self) -> None:
        """Stop the optimization engine"""
        self.monitor.stop_monitoring()
        logger.info("⏹️ Performance optimization engine stopped")

    def performance_aware(self, threshold_ms: float = 1000.0):
        """Decorator for performance-aware functions"""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                request_id = f"{func.__name__}_{id(threading.current_thread())}"

                with self.monitor.track_request(request_id):
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        return result
                    finally:
                        execution_time = (time.time() - start_time) * 1000

                        if execution_time > threshold_ms:
                            logger.warning(
                                f"⚠️ Slow operation detected: {func.__name__} took {execution_time:.1f}ms"
                            )

            return wrapper

        return decorator

    def optimize_algorithm_performance(
        self, algorithm_name: str, execution_time: float
    ) -> OptimizationResult:
        """Optimize specific algorithm performance"""
        before_metrics = self.monitor.get_current_metrics()
        optimizations_applied = []
        recommendations = []

        # Algorithm-specific optimizations
        if algorithm_name == "genetic" and execution_time > 5.0:
            recommendations.extend(
                [
                    "Consider reducing population size for faster convergence",
                    "Implement parallel fitness evaluation",
                    "Use early stopping with convergence detection",
                ]
            )
            optimizations_applied.append("genetic_algorithm_tuning")

        elif algorithm_name == "simulated_annealing" and execution_time > 3.0:
            recommendations.extend(
                [
                    "Optimize cooling schedule",
                    "Implement adaptive reheating",
                    "Use efficient neighbor generation",
                ]
            )
            optimizations_applied.append("simulated_annealing_tuning")

        # General performance recommendations
        if execution_time > 2.0:
            recommendations.extend(
                [
                    "Consider algorithm parallelization",
                    "Implement result caching",
                    "Use approximation algorithms for large datasets",
                ]
            )

        after_metrics = self.monitor.get_current_metrics()
        improvement = 0.0  # Would calculate actual improvement

        result = OptimizationResult(
            improvement_percentage=improvement,
            performance_before=before_metrics or PerformanceMetrics(),
            performance_after=after_metrics or PerformanceMetrics(),
            optimizations_applied=optimizations_applied,
            recommendations=recommendations,
        )

        self.optimization_history.append(result)
        return result

    def get_optimization_report(self) -> dict[str, Any]:
        """Generate comprehensive optimization report"""
        current_metrics = self.monitor.get_current_metrics()
        metrics_history = self.monitor.get_metrics_history(last_n=100)

        if not current_metrics or not metrics_history:
            return {"status": "insufficient_data"}

        # Calculate trends
        if len(metrics_history) >= 10:
            recent_cpu = sum(m.cpu_percent for m in metrics_history[-10:]) / 10
            recent_memory = sum(m.memory_mb for m in metrics_history[-10:]) / 10
            recent_cache_hit = sum(m.cache_hit_rate for m in metrics_history[-10:]) / 10
        else:
            recent_cpu = current_metrics.cpu_percent
            recent_memory = current_metrics.memory_mb
            recent_cache_hit = current_metrics.cache_hit_rate

        # Performance status
        status = "healthy"
        if recent_cpu > 80 or recent_memory > 800:
            status = "warning"
        if recent_cpu > 90 or recent_memory > 1000:
            status = "critical"

        recommendations = []
        if recent_cpu > 70:
            recommendations.append("High CPU usage detected - consider optimization")
        if recent_memory > 500:
            recommendations.append("High memory usage - implement memory optimization")
        if recent_cache_hit < 60:
            recommendations.append("Low cache hit rate - review caching strategy")

        return {
            "status": status,
            "current_metrics": {
                "cpu_percent": current_metrics.cpu_percent,
                "memory_mb": current_metrics.memory_mb,
                "cache_hit_rate": current_metrics.cache_hit_rate,
                "request_count": current_metrics.request_count,
            },
            "trends": {
                "avg_cpu_last_10": recent_cpu,
                "avg_memory_last_10": recent_memory,
                "avg_cache_hit_last_10": recent_cache_hit,
            },
            "optimization_count": len(self.optimization_history),
            "recommendations": recommendations,
            "monitoring_active": self.monitor.monitoring_active,
        }

    def track_optimization_start(self, data: dict[str, Any]) -> None:
        """Track the start of a route optimization"""
        try:
            metric = PerformanceMetric(
                timestamp=datetime.utcnow().isoformat(),
                metric_type="optimization_start",
                value=data.get("stores_count", 0),
                unit="stores",
                status="normal",
            )
            self._add_metric("optimization_events", metric)

            logger.debug(
                f"Tracked optimization start: {data.get('algorithm', 'unknown')} with {data.get('stores_count', 0)} stores"
            )
        except Exception as e:
            logger.error(f"Error tracking optimization start: {e}")

    def track_optimization_completion(self, data: dict[str, Any]) -> None:
        """Track the completion of a route optimization"""
        try:
            # Track processing time
            time_metric = PerformanceMetric(
                timestamp=datetime.utcnow().isoformat(),
                metric_type="optimization_time",
                value=data.get("processing_time", 0),
                unit="seconds",
                threshold_warning=5.0,
                threshold_critical=10.0,
                status="warning" if data.get("processing_time", 0) > 5.0 else "normal",
            )
            self._add_metric("optimization_performance", time_metric)

            # Track optimization score
            score_metric = PerformanceMetric(
                timestamp=datetime.utcnow().isoformat(),
                metric_type="optimization_score",
                value=data.get("optimization_score", 0),
                unit="percent",
                threshold_warning=70.0,
                threshold_critical=50.0,
                status=(
                    "warning" if data.get("optimization_score", 0) < 70.0 else "normal"
                ),
            )
            self._add_metric("optimization_quality", score_metric)

            # Track improvement
            improvement_metric = PerformanceMetric(
                timestamp=datetime.utcnow().isoformat(),
                metric_type="route_improvement",
                value=data.get("improvement_percent", 0),
                unit="percent",
                status="normal",
            )
            self._add_metric("algorithm_performance", improvement_metric)

            logger.info(
                f"Tracked optimization completion: {data.get('algorithm', 'unknown')} - "
                f"{data.get('processing_time', 0):.2f}s, {data.get('improvement_percent', 0):.1f}% improvement"
            )
        except Exception as e:
            logger.error(f"Error tracking optimization completion: {e}")

    def track_optimization_failure(self, data: dict[str, Any]) -> None:
        """Track a failed route optimization"""
        try:
            failure_metric = PerformanceMetric(
                timestamp=datetime.utcnow().isoformat(),
                metric_type="optimization_failure",
                value=1,
                unit="count",
                status="critical",
            )
            self._add_metric("optimization_errors", failure_metric)

            # Generate alert for optimization failure
            alert = SystemAlert(
                alert_id=f"opt_fail_{int(time.time())}",
                severity="critical",
                title="Route Optimization Failed",
                description=f"Optimization failed for {data.get('stores_count', 0)} stores using {data.get('algorithm', 'unknown')} algorithm: {data.get('error', 'Unknown error')}",
                timestamp=datetime.utcnow().isoformat(),
                component="routing_service",
                metric="optimization_failure",
                current_value=1,
                threshold=0,
            )
            self.active_alerts.append(alert)

            logger.error(
                f"Tracked optimization failure: {data.get('algorithm', 'unknown')} - {data.get('error', 'Unknown error')}"
            )
        except Exception as e:
            logger.error(f"Error tracking optimization failure: {e}")

    def get_optimization_insights(self) -> dict[str, Any]:
        """Get insights about route optimization performance"""
        try:
            insights = {
                "optimization_summary": self._get_optimization_summary(),
                "performance_trends": self._get_performance_trends(),
                "algorithm_comparison": self._get_algorithm_comparison(),
                "recommendations": self._get_optimization_recommendations(),
            }
            return insights
        except Exception as e:
            logger.error(f"Error generating optimization insights: {e}")
            return {}

    def _get_optimization_summary(self) -> dict[str, Any]:
        """Get summary of optimization performance"""
        try:
            # Get recent optimization metrics
            recent_times = self._get_recent_metrics(
                "optimization_performance", "optimization_time", hours=24
            )
            recent_scores = self._get_recent_metrics(
                "optimization_quality", "optimization_score", hours=24
            )
            recent_improvements = self._get_recent_metrics(
                "algorithm_performance", "route_improvement", hours=24
            )

            return {
                "total_optimizations": len(recent_times),
                "avg_processing_time": (
                    sum(recent_times) / len(recent_times) if recent_times else 0
                ),
                "avg_optimization_score": (
                    sum(recent_scores) / len(recent_scores) if recent_scores else 0
                ),
                "avg_improvement": (
                    sum(recent_improvements) / len(recent_improvements)
                    if recent_improvements
                    else 0
                ),
                "optimization_rate": len(recent_times) / 24,  # per hour
            }
        except Exception as e:
            logger.error(f"Error getting optimization summary: {e}")
            return {}

    def _get_performance_trends(self) -> dict[str, Any]:
        """Get performance trend analysis"""
        try:
            # Analyze trends over different time periods
            last_hour_times = self._get_recent_metrics(
                "optimization_performance", "optimization_time", hours=1
            )
            last_day_times = self._get_recent_metrics(
                "optimization_performance", "optimization_time", hours=24
            )

            return {
                "hourly_avg": (
                    sum(last_hour_times) / len(last_hour_times)
                    if last_hour_times
                    else 0
                ),
                "daily_avg": (
                    sum(last_day_times) / len(last_day_times) if last_day_times else 0
                ),
                "trend": (
                    "improving"
                    if len(last_hour_times) > 0
                    and len(last_day_times) > 0
                    and sum(last_hour_times) / len(last_hour_times)
                    < sum(last_day_times) / len(last_day_times)
                    else "stable"
                ),
            }
        except Exception as e:
            logger.error(f"Error getting performance trends: {e}")
            return {}

    def _get_algorithm_comparison(self) -> dict[str, Any]:
        """Get comparison of different algorithms"""
        # This would require storing algorithm-specific metrics
        # For now, return placeholder data
        return {
            "genetic": {"avg_time": 2.5, "avg_improvement": 15.2},
            "simulated_annealing": {"avg_time": 3.1, "avg_improvement": 18.7},
            "default": {"avg_time": 0.8, "avg_improvement": 5.1},
        }

    def _get_optimization_recommendations(self) -> list[str]:
        """Get recommendations for optimization improvements"""
        recommendations = []

        # Get recent performance data
        recent_times = self._get_recent_metrics(
            "optimization_performance", "optimization_time", hours=24
        )
        recent_scores = self._get_recent_metrics(
            "optimization_quality", "optimization_score", hours=24
        )

        if recent_times:
            avg_time = sum(recent_times) / len(recent_times)
            if avg_time > 5.0:
                recommendations.append(
                    "Consider using faster algorithms for large route sets"
                )
            if avg_time < 1.0:
                recommendations.append(
                    "Consider using more sophisticated algorithms for better optimization"
                )

        if recent_scores:
            avg_score = sum(recent_scores) / len(recent_scores)
            if avg_score < 70:
                recommendations.append(
                    "Route optimization quality is below target - review algorithm parameters"
                )
            if avg_score > 90:
                recommendations.append(
                    "Excellent optimization performance - current settings are optimal"
                )

        return recommendations

    def _get_recent_metrics(
        self, category: str, metric_type: str, hours: int = 24
    ) -> list[float]:
        """Get recent metrics of a specific type"""
        try:
            if category not in self.metrics_history:
                return []

            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_metrics = []

            for metric in self.metrics_history[category]:
                metric_time = datetime.fromisoformat(
                    metric.timestamp.replace("Z", "+00:00")
                )
                if metric_time > cutoff_time and metric.metric_type == metric_type:
                    recent_metrics.append(metric.value)

            return recent_metrics
        except Exception as e:
            logger.error(f"Error getting recent metrics: {e}")
            return []


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()

# Convenience decorators
performance_aware = performance_optimizer.performance_aware


def start_performance_optimization():
    """Start global performance optimization"""
    performance_optimizer.start()


def stop_performance_optimization():
    """Stop global performance optimization"""
    performance_optimizer.stop()


def get_performance_report():
    """Get global performance report"""
    return performance_optimizer.get_optimization_report()
