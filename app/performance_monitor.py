"""
Advanced Performance Monitoring for RouteForce Enhanced System
Provides real-time performance metrics, alerting, and optimization insights
"""

import logging
import threading
import time
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""

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


class PerformanceMonitor:
    """Advanced performance monitoring system"""

    def __init__(self, metrics_retention_hours: int = 24):
        self.metrics_retention_hours = metrics_retention_hours
        self.metrics_history: dict[str, deque] = {}
        self.active_alerts: list[SystemAlert] = []
        self.alert_id_counter = 0
        self.monitoring_active = False
        self.monitor_thread = None

        # Thresholds configuration
        self.thresholds = {
            "cpu_usage": {"warning": 70.0, "critical": 90.0},
            "memory_usage": {"warning": 80.0, "critical": 95.0},
            "disk_usage": {"warning": 85.0, "critical": 95.0},
            "api_response_time": {
                "warning": 1000.0,
                "critical": 5000.0,
            },  # milliseconds
            "database_connections": {"warning": 80.0, "critical": 95.0},
            "error_rate": {"warning": 5.0, "critical": 10.0},  # percentage
        }

        # Initialize metrics storage
        self._initialize_metrics_storage()

    def _initialize_metrics_storage(self):
        """Initialize metrics storage with deques for each metric type"""
        metric_types = [
            "cpu_usage",
            "memory_usage",
            "disk_usage",
            "network_io",
            "api_response_time",
            "database_connections",
            "error_rate",
            "active_routes",
            "analytics_requests",
            "prediction_accuracy",
        ]

        for metric_type in metric_types:
            self.metrics_history[metric_type] = deque(
                maxlen=self.metrics_retention_hours * 60
            )  # 1 metric per minute

    def start_monitoring(self):
        """Start the performance monitoring thread"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(
                target=self._monitoring_loop, daemon=True
            )
            self.monitor_thread.start()
            logger.info("Performance monitoring started")

    def stop_monitoring(self):
        """Stop the performance monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        logger.info("Performance monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                self._collect_system_metrics()

                # Collect application metrics
                self._collect_application_metrics()

                # Check thresholds and generate alerts
                self._check_thresholds()

                # Clean up old metrics
                self._cleanup_old_metrics()

                # Sleep for 60 seconds (1 minute interval)
                time.sleep(60)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(60)  # Continue monitoring even after errors

    def _collect_system_metrics(self):
        """Collect system-level performance metrics"""
        timestamp = datetime.now().isoformat()

        # CPU Usage
        cpu_usage = psutil.cpu_percent(interval=1)
        self._add_metric("cpu_usage", cpu_usage, "percent", timestamp)

        # Memory Usage
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        self._add_metric("memory_usage", memory_usage, "percent", timestamp)

        # Disk Usage
        disk = psutil.disk_usage("/")
        disk_usage = (disk.used / disk.total) * 100
        self._add_metric("disk_usage", disk_usage, "percent", timestamp)

        # Network I/O
        network = psutil.net_io_counters()
        network_io = network.bytes_sent + network.bytes_recv
        self._add_metric("network_io", network_io, "bytes", timestamp)

    def _collect_application_metrics(self):
        """Collect application-specific metrics"""
        timestamp = datetime.now().isoformat()

        # Simulate application metrics (in real implementation, these would come from app)
        # API Response Time (would be measured from actual requests)
        import random

        api_response_time = random.uniform(50, 300)  # Simulated response time in ms
        self._add_metric("api_response_time", api_response_time, "ms", timestamp)

        # Active Routes (would come from route tracking system)
        active_routes = random.randint(5, 15)
        self._add_metric("active_routes", active_routes, "count", timestamp)

        # Analytics Requests (would come from analytics engine)
        analytics_requests = random.randint(10, 50)
        self._add_metric("analytics_requests", analytics_requests, "count", timestamp)

        # Error Rate (would come from error tracking)
        error_rate = random.uniform(0.1, 2.0)
        self._add_metric("error_rate", error_rate, "percent", timestamp)

    def _add_metric(self, metric_type: str, value: float, unit: str, timestamp: str):
        """Add a metric to the history"""
        thresholds = self.thresholds.get(metric_type, {})

        metric = PerformanceMetric(
            timestamp=timestamp,
            metric_type=metric_type,
            value=value,
            unit=unit,
            threshold_warning=thresholds.get("warning"),
            threshold_critical=thresholds.get("critical"),
        )

        # Determine status
        if thresholds.get("critical") and value >= thresholds["critical"]:
            metric.status = "critical"
        elif thresholds.get("warning") and value >= thresholds["warning"]:
            metric.status = "warning"
        else:
            metric.status = "normal"

        # Add to history
        if metric_type in self.metrics_history:
            self.metrics_history[metric_type].append(metric)

        logger.debug(
            f"Metric collected: {metric_type}={value:.2f}{unit} ({metric.status})"
        )

    def _check_thresholds(self):
        """Check metrics against thresholds and generate alerts"""
        for metric_type, metrics in self.metrics_history.items():
            if not metrics:
                continue

            latest_metric = metrics[-1]

            # Check for threshold violations
            if latest_metric.status in ["warning", "critical"]:
                self._generate_alert(latest_metric)

    def _generate_alert(self, metric: PerformanceMetric):
        """Generate an alert for a threshold violation"""
        # Check if we already have an active alert for this metric
        existing_alert = None
        for alert in self.active_alerts:
            if (
                alert.component == "system"
                and alert.metric == metric.metric_type
                and not alert.acknowledged
            ):
                existing_alert = alert
                break

        if existing_alert:
            # Update existing alert
            existing_alert.current_value = metric.value
            existing_alert.timestamp = metric.timestamp
        else:
            # Create new alert
            self.alert_id_counter += 1
            alert = SystemAlert(
                alert_id=f"ALERT_{self.alert_id_counter:06d}",
                severity=metric.status,
                title=f"High {metric.metric_type.replace('_', ' ').title()}",
                description=f"{metric.metric_type.replace('_', ' ').title()} is {metric.value:.1f}{metric.unit}, "
                f"exceeding {metric.status} threshold of "
                f"{metric.threshold_critical if metric.status == 'critical' else metric.threshold_warning:.1f}{metric.unit}",
                timestamp=metric.timestamp,
                component="system",
                metric=metric.metric_type,
                current_value=metric.value,
                threshold=(
                    metric.threshold_critical
                    if metric.status == "critical"
                    else metric.threshold_warning
                ),
            )

            self.active_alerts.append(alert)
            logger.warning(f"Alert generated: {alert.title} - {alert.description}")

    def _cleanup_old_metrics(self):
        """Clean up metrics older than retention period"""
        cutoff_time = datetime.now() - timedelta(hours=self.metrics_retention_hours)
        cutoff_iso = cutoff_time.isoformat()

        for metric_type, metrics in self.metrics_history.items():
            # Remove old metrics (deque already handles max length, but we can be explicit)
            while metrics and metrics[0].timestamp < cutoff_iso:
                metrics.popleft()

    def get_current_metrics(self) -> dict[str, Any]:
        """Get current performance metrics"""
        current_metrics = {}

        for metric_type, metrics in self.metrics_history.items():
            if metrics:
                latest_metric = metrics[-1]
                current_metrics[metric_type] = {
                    "value": latest_metric.value,
                    "unit": latest_metric.unit,
                    "status": latest_metric.status,
                    "timestamp": latest_metric.timestamp,
                }

        return current_metrics

    def get_metrics_history(
        self, metric_type: str, hours: int = 1
    ) -> list[dict[str, Any]]:
        """Get historical metrics for a specific type"""
        if metric_type not in self.metrics_history:
            return []

        cutoff_time = datetime.now() - timedelta(hours=hours)
        cutoff_iso = cutoff_time.isoformat()

        metrics = self.metrics_history[metric_type]
        recent_metrics = [
            asdict(metric) for metric in metrics if metric.timestamp >= cutoff_iso
        ]

        return recent_metrics

    def get_active_alerts(self, severity: str | None = None) -> list[dict[str, Any]]:
        """Get active alerts, optionally filtered by severity"""
        alerts = self.active_alerts

        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]

        # Only return unacknowledged alerts
        active_alerts = [alert for alert in alerts if not alert.acknowledged]

        return [asdict(alert) for alert in active_alerts]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.active_alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                logger.info(f"Alert acknowledged: {alert_id}")
                return True

        return False

    def get_system_health_score(self) -> dict[str, Any]:
        """Calculate overall system health score"""
        current_metrics = self.get_current_metrics()

        if not current_metrics:
            return {
                "score": 100,
                "status": "unknown",
                "details": "No metrics available",
            }

        # Calculate health score based on metric statuses
        total_metrics = len(current_metrics)
        critical_count = sum(
            1 for m in current_metrics.values() if m["status"] == "critical"
        )
        warning_count = sum(
            1 for m in current_metrics.values() if m["status"] == "warning"
        )
        normal_count = total_metrics - critical_count - warning_count

        # Health score calculation
        score = (
            normal_count * 100 + warning_count * 60 + critical_count * 20
        ) / total_metrics

        # Determine overall status
        if critical_count > 0:
            status = "critical"
        elif warning_count > 0:
            status = "warning"
        else:
            status = "healthy"

        return {
            "score": round(score, 1),
            "status": status,
            "details": {
                "total_metrics": total_metrics,
                "normal": normal_count,
                "warning": warning_count,
                "critical": critical_count,
            },
        }

    def get_performance_summary(self) -> dict[str, Any]:
        """Get comprehensive performance summary"""
        return {
            "current_metrics": self.get_current_metrics(),
            "active_alerts": self.get_active_alerts(),
            "health_score": self.get_system_health_score(),
            "monitoring_status": "active" if self.monitoring_active else "inactive",
            "last_updated": datetime.now().isoformat(),
        }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    return performance_monitor
