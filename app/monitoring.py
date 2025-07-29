"""
Advanced monitoring and metrics collection
"""

import time
import logging
from functools import wraps
from typing import Dict, Any, Callable
from flask import request, g
import psutil
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collect and store application metrics"""

    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "requests_by_endpoint": defaultdict(int),
            "response_times": defaultdict(list),
            "errors_total": 0,
            "errors_by_type": defaultdict(int),
            "active_users": set(),
            "memory_usage": deque(maxlen=100),
            "cpu_usage": deque(maxlen=100),
            "route_generations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
        self.lock = threading.Lock()

        # Start background monitoring
        self._start_system_monitoring()

    def record_request(
        self, endpoint: str, response_time: float, status_code: int, user_ip: str
    ):
        """Record request metrics"""
        with self.lock:
            self.metrics["requests_total"] += 1
            self.metrics["requests_by_endpoint"][endpoint] += 1
            self.metrics["response_times"][endpoint].append(response_time)

            # Keep only last 1000 response times per endpoint
            if len(self.metrics["response_times"][endpoint]) > 1000:
                self.metrics["response_times"][endpoint] = self.metrics[
                    "response_times"
                ][endpoint][-1000:]

            self.metrics["active_users"].add(user_ip)

            if status_code >= 400:
                self.metrics["errors_total"] += 1
                self.metrics["errors_by_type"][f"{status_code}xx"] += 1

    def record_route_generation(self):
        """Record route generation event"""
        with self.lock:
            self.metrics["route_generations"] += 1

    def record_cache_hit(self):
        """Record cache hit"""
        with self.lock:
            self.metrics["cache_hits"] += 1

    def record_cache_miss(self):
        """Record cache miss"""
        with self.lock:
            self.metrics["cache_misses"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        with self.lock:
            # Calculate averages
            avg_response_times = {}
            for endpoint, times in self.metrics["response_times"].items():
                if times:
                    avg_response_times[endpoint] = sum(times) / len(times)

            # Calculate cache hit rate
            total_cache_requests = (
                self.metrics["cache_hits"] + self.metrics["cache_misses"]
            )
            cache_hit_rate = (
                (self.metrics["cache_hits"] / total_cache_requests * 100)
                if total_cache_requests > 0
                else 0
            )

            return {
                "requests_total": self.metrics["requests_total"],
                "requests_by_endpoint": dict(self.metrics["requests_by_endpoint"]),
                "average_response_times": avg_response_times,
                "errors_total": self.metrics["errors_total"],
                "errors_by_type": dict(self.metrics["errors_by_type"]),
                "active_users_count": len(self.metrics["active_users"]),
                "route_generations": self.metrics["route_generations"],
                "cache_hit_rate": round(cache_hit_rate, 2),
                "memory_usage_mb": list(self.metrics["memory_usage"])[
                    -10:
                ],  # Last 10 readings
                "cpu_usage_percent": list(self.metrics["cpu_usage"])[
                    -10:
                ],  # Last 10 readings
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _start_system_monitoring(self):
        """Start background system monitoring"""

        def monitor():
            while True:
                try:
                    # Get system metrics
                    memory_mb = psutil.virtual_memory().used / 1024 / 1024
                    cpu_percent = psutil.cpu_percent(interval=1)

                    with self.lock:
                        self.metrics["memory_usage"].append(memory_mb)
                        self.metrics["cpu_usage"].append(cpu_percent)

                    time.sleep(30)  # Update every 30 seconds

                except Exception as e:
                    logger.error(f"Error in system monitoring: {e}")
                    time.sleep(60)  # Wait longer on error

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()


# Global metrics collector
metrics_collector = MetricsCollector()


def monitor_performance(func: Callable) -> Callable:
    """Decorator to monitor function performance"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise
        finally:
            duration = time.time() - start_time
            logger.info(f"{func.__name__} executed in {duration:.3f}s")

    return wrapper


def setup_request_monitoring(app):
    """Setup request monitoring for Flask app"""

    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(g, "start_time"):
            duration = time.time() - g.start_time
            endpoint = request.endpoint or "unknown"
            user_ip = request.remote_addr or "unknown"

            metrics_collector.record_request(
                endpoint=endpoint,
                response_time=duration,
                status_code=response.status_code,
                user_ip=user_ip,
            )

            # Log slow requests
            if duration > 5.0:  # 5 seconds
                logger.warning(f"Slow request: {endpoint} took {duration:.3f}s")

        return response

    # Add metrics endpoint
    @app.route("/metrics")
    def metrics():
        """Prometheus-style metrics endpoint"""
        from flask import jsonify

        return jsonify(metrics_collector.get_metrics())


class StructuredLogger:
    """Structured logging for better observability"""

    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)

    def log_event(self, event_type: str, message: str, **kwargs):
        """Log structured event"""
        log_data = {
            "event_type": event_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs,
        }

        self.logger.info(f"EVENT: {log_data}")

    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log structured error"""
        log_data = {
            "event_type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.utcnow().isoformat(),
            "context": context or {},
        }

        self.logger.error(f"ERROR: {log_data}")

    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics"""
        log_data = {
            "event_type": "performance",
            "operation": operation,
            "duration_seconds": duration,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs,
        }

        self.logger.info(f"PERFORMANCE: {log_data}")


# Global structured logger
structured_logger = StructuredLogger(__name__)
