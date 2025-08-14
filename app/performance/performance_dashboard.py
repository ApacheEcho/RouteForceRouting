"""
Real-time Performance Dashboard - Beast Mode Monitoring
Comprehensive performance monitoring with real-time metrics and optimization
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import deque
import psutil
import logging

from flask import Blueprint, render_template, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """System-level performance metrics"""
    
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_gb: float = 0.0
    memory_total_gb: float = 0.0
    disk_percent: float = 0.0
    disk_used_gb: float = 0.0
    disk_total_gb: float = 0.0
    network_sent: int = 0
    network_recv: int = 0
    load_avg: List[float] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ApplicationMetrics:
    """Application-level performance metrics"""
    
    active_connections: int = 0
    total_requests: int = 0
    requests_per_second: float = 0.0
    avg_response_time: float = 0.0
    cache_hit_rate: float = 0.0
    database_connections: int = 0
    queue_size: int = 0
    error_rate: float = 0.0
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PerformanceAlert:
    """Performance alert definition"""
    
    alert_id: str
    severity: str  # info, warning, critical
    title: str
    description: str
    metric: str
    current_value: float
    threshold: float
    timestamp: float = field(default_factory=time.time)
    acknowledged: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MetricsCollector:
    """Collects and aggregates performance metrics"""
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.system_history = deque(maxlen=history_size)
        self.app_history = deque(maxlen=history_size)
        self.alerts = deque(maxlen=100)
        
        # Performance thresholds
        self.thresholds = {
            "cpu_critical": 90.0,
            "cpu_warning": 75.0,
            "memory_critical": 90.0,
            "memory_warning": 80.0,
            "disk_critical": 95.0,
            "disk_warning": 85.0,
            "response_time_critical": 3.0,
            "response_time_warning": 1.0,
            "error_rate_critical": 10.0,
            "error_rate_warning": 5.0,
        }
        
        # Metrics tracking
        self.last_network_counters = psutil.net_io_counters()
        self.last_network_time = time.time()
        
        # Application metrics (these would be updated by other components)
        self.app_metrics = ApplicationMetrics()
        
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system performance metrics"""
        try:
            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network = psutil.net_io_counters()
            current_time = time.time()
            time_delta = current_time - self.last_network_time
            
            network_sent = (network.bytes_sent - self.last_network_counters.bytes_sent) / time_delta
            network_recv = (network.bytes_recv - self.last_network_counters.bytes_recv) / time_delta
            
            self.last_network_counters = network
            self.last_network_time = current_time
            
            # Load average (Unix/Linux only)
            load_avg = []
            try:
                load_avg = list(psutil.getloadavg())
            except AttributeError:
                # Windows doesn't have load average
                load_avg = [cpu_percent / 100, 0, 0]
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_gb=memory.used / (1024**3),
                memory_total_gb=memory.total / (1024**3),
                disk_percent=disk.percent,
                disk_used_gb=disk.used / (1024**3),
                disk_total_gb=disk.total / (1024**3),
                network_sent=int(network_sent),
                network_recv=int(network_recv),
                load_avg=load_avg,
                timestamp=current_time
            )
            
            # Store in history
            self.system_history.append(metrics)
            
            # Check for alerts
            self._check_system_alerts(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics()
    
    def update_app_metrics(self, **kwargs) -> None:
        """Update application metrics"""
        for key, value in kwargs.items():
            if hasattr(self.app_metrics, key):
                setattr(self.app_metrics, key, value)
        
        self.app_metrics.timestamp = time.time()
        self.app_history.append(self.app_metrics)
        
        # Check for application alerts
        self._check_app_alerts(self.app_metrics)
    
    def _check_system_alerts(self, metrics: SystemMetrics) -> None:
        """Check for system performance alerts"""
        alerts_generated = []
        
        # CPU alerts
        if metrics.cpu_percent > self.thresholds["cpu_critical"]:
            alerts_generated.append(self._create_alert(
                "cpu_critical", "critical", "Critical CPU Usage",
                f"CPU usage is {metrics.cpu_percent:.1f}%",
                "cpu_percent", metrics.cpu_percent, self.thresholds["cpu_critical"]
            ))
        elif metrics.cpu_percent > self.thresholds["cpu_warning"]:
            alerts_generated.append(self._create_alert(
                "cpu_warning", "warning", "High CPU Usage",
                f"CPU usage is {metrics.cpu_percent:.1f}%",
                "cpu_percent", metrics.cpu_percent, self.thresholds["cpu_warning"]
            ))
        
        # Memory alerts
        if metrics.memory_percent > self.thresholds["memory_critical"]:
            alerts_generated.append(self._create_alert(
                "memory_critical", "critical", "Critical Memory Usage",
                f"Memory usage is {metrics.memory_percent:.1f}%",
                "memory_percent", metrics.memory_percent, self.thresholds["memory_critical"]
            ))
        elif metrics.memory_percent > self.thresholds["memory_warning"]:
            alerts_generated.append(self._create_alert(
                "memory_warning", "warning", "High Memory Usage",
                f"Memory usage is {metrics.memory_percent:.1f}%",
                "memory_percent", metrics.memory_percent, self.thresholds["memory_warning"]
            ))
        
        # Disk alerts
        if metrics.disk_percent > self.thresholds["disk_critical"]:
            alerts_generated.append(self._create_alert(
                "disk_critical", "critical", "Critical Disk Usage",
                f"Disk usage is {metrics.disk_percent:.1f}%",
                "disk_percent", metrics.disk_percent, self.thresholds["disk_critical"]
            ))
        elif metrics.disk_percent > self.thresholds["disk_warning"]:
            alerts_generated.append(self._create_alert(
                "disk_warning", "warning", "High Disk Usage",
                f"Disk usage is {metrics.disk_percent:.1f}%",
                "disk_percent", metrics.disk_percent, self.thresholds["disk_warning"]
            ))
        
        # Add alerts to queue
        for alert in alerts_generated:
            self.alerts.append(alert)
    
    def _check_app_alerts(self, metrics: ApplicationMetrics) -> None:
        """Check for application performance alerts"""
        alerts_generated = []
        
        # Response time alerts
        if metrics.avg_response_time > self.thresholds["response_time_critical"]:
            alerts_generated.append(self._create_alert(
                "response_critical", "critical", "Critical Response Time",
                f"Average response time is {metrics.avg_response_time:.3f}s",
                "avg_response_time", metrics.avg_response_time, 
                self.thresholds["response_time_critical"]
            ))
        elif metrics.avg_response_time > self.thresholds["response_time_warning"]:
            alerts_generated.append(self._create_alert(
                "response_warning", "warning", "High Response Time",
                f"Average response time is {metrics.avg_response_time:.3f}s",
                "avg_response_time", metrics.avg_response_time,
                self.thresholds["response_time_warning"]
            ))
        
        # Error rate alerts
        if metrics.error_rate > self.thresholds["error_rate_critical"]:
            alerts_generated.append(self._create_alert(
                "error_critical", "critical", "Critical Error Rate",
                f"Error rate is {metrics.error_rate:.1f}%",
                "error_rate", metrics.error_rate, self.thresholds["error_rate_critical"]
            ))
        elif metrics.error_rate > self.thresholds["error_rate_warning"]:
            alerts_generated.append(self._create_alert(
                "error_warning", "warning", "High Error Rate",
                f"Error rate is {metrics.error_rate:.1f}%",
                "error_rate", metrics.error_rate, self.thresholds["error_rate_warning"]
            ))
        
        # Add alerts to queue
        for alert in alerts_generated:
            self.alerts.append(alert)
    
    def _create_alert(
        self, alert_id: str, severity: str, title: str, description: str,
        metric: str, current_value: float, threshold: float
    ) -> PerformanceAlert:
        """Create a performance alert"""
        return PerformanceAlert(
            alert_id=f"{alert_id}_{int(time.time())}",
            severity=severity,
            title=title,
            description=description,
            metric=metric,
            current_value=current_value,
            threshold=threshold
        )
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        system_metrics = self.collect_system_metrics()
        
        return {
            "system": system_metrics.to_dict(),
            "application": self.app_metrics.to_dict(),
            "alerts": [alert.to_dict() for alert in list(self.alerts)[-10:]],  # Last 10 alerts
            "timestamp": time.time()
        }
    
    def get_historical_data(self, minutes: int = 60) -> Dict[str, Any]:
        """Get historical performance data"""
        cutoff_time = time.time() - (minutes * 60)
        
        # Filter recent data
        recent_system = [
            m.to_dict() for m in self.system_history 
            if m.timestamp > cutoff_time
        ]
        
        recent_app = [
            m.to_dict() for m in self.app_history 
            if m.timestamp > cutoff_time
        ]
        
        return {
            "system_history": recent_system,
            "application_history": recent_app,
            "time_range": f"{minutes} minutes",
            "data_points": {
                "system": len(recent_system),
                "application": len(recent_app)
            }
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary and health score"""
        if not self.system_history:
            return {"health_score": 0, "status": "no_data"}
        
        recent_system = self.system_history[-10:]  # Last 10 readings
        recent_app = list(self.app_history)[-10:] if self.app_history else []
        
        # Calculate averages
        avg_cpu = sum(m.cpu_percent for m in recent_system) / len(recent_system)
        avg_memory = sum(m.memory_percent for m in recent_system) / len(recent_system)
        avg_disk = sum(m.disk_percent for m in recent_system) / len(recent_system)
        
        avg_response_time = 0
        if recent_app:
            avg_response_time = sum(m.avg_response_time for m in recent_app) / len(recent_app)
        
        # Calculate health score (0-100)
        health_score = 100
        
        # System penalties
        if avg_cpu > 80:
            health_score -= 20
        elif avg_cpu > 60:
            health_score -= 10
        
        if avg_memory > 85:
            health_score -= 20
        elif avg_memory > 70:
            health_score -= 10
        
        if avg_disk > 90:
            health_score -= 30
        elif avg_disk > 80:
            health_score -= 15
        
        # Application penalties
        if avg_response_time > 2:
            health_score -= 15
        elif avg_response_time > 1:
            health_score -= 8
        
        # Alert penalties
        critical_alerts = sum(1 for alert in self.alerts if alert.severity == "critical")
        warning_alerts = sum(1 for alert in self.alerts if alert.severity == "warning")
        
        health_score -= critical_alerts * 10
        health_score -= warning_alerts * 5
        
        health_score = max(0, health_score)
        
        # Determine status
        if health_score >= 90:
            status = "excellent"
        elif health_score >= 75:
            status = "good"
        elif health_score >= 50:
            status = "warning"
        else:
            status = "critical"
        
        return {
            "health_score": health_score,
            "status": status,
            "averages": {
                "cpu_percent": avg_cpu,
                "memory_percent": avg_memory,
                "disk_percent": avg_disk,
                "response_time": avg_response_time,
            },
            "alert_counts": {
                "critical": critical_alerts,
                "warning": warning_alerts,
                "total": len(self.alerts)
            }
        }


class PerformanceDashboard:
    """Real-time performance dashboard with WebSocket updates"""
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.metrics_collector = MetricsCollector()
        self.update_interval = 5  # seconds
        self.active_clients = set()
        
        # Background thread for metrics collection
        self.monitoring_thread = None
        self.monitoring_active = False
        
        # Setup WebSocket handlers
        self._setup_socketio_handlers()
    
    def start_monitoring(self) -> None:
        """Start background monitoring thread"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("🚀 Performance monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=2)
        logger.info("⏹️ Performance monitoring stopped")
    
    def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect metrics
                metrics = self.metrics_collector.get_current_metrics()
                
                # Emit to connected clients
                if self.active_clients:
                    self.socketio.emit(
                        'performance_update',
                        metrics,
                        room='performance_dashboard'
                    )
                
                # Sleep until next update
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.update_interval)
    
    def _setup_socketio_handlers(self) -> None:
        """Setup WebSocket event handlers"""
        
        @self.socketio.on('join_performance_dashboard')
        def on_join():
            """Handle client joining performance dashboard"""
            join_room('performance_dashboard')
            self.active_clients.add(request.sid)
            
            # Send current metrics immediately
            current_metrics = self.metrics_collector.get_current_metrics()
            emit('performance_update', current_metrics)
            
            logger.debug(f"Client {request.sid} joined performance dashboard")
        
        @self.socketio.on('leave_performance_dashboard')
        def on_leave():
            """Handle client leaving performance dashboard"""
            leave_room('performance_dashboard')
            self.active_clients.discard(request.sid)
            logger.debug(f"Client {request.sid} left performance dashboard")
        
        @self.socketio.on('request_historical_data')
        def on_request_historical_data(data):
            """Handle request for historical data"""
            minutes = data.get('minutes', 60)
            historical_data = self.metrics_collector.get_historical_data(minutes)
            emit('historical_data', historical_data)
        
        @self.socketio.on('acknowledge_alert')
        def on_acknowledge_alert(data):
            """Handle alert acknowledgment"""
            alert_id = data.get('alert_id')
            
            # Find and acknowledge alert
            for alert in self.metrics_collector.alerts:
                if alert.alert_id == alert_id:
                    alert.acknowledged = True
                    break
            
            emit('alert_acknowledged', {'alert_id': alert_id})
    
    def update_app_metrics(self, **kwargs) -> None:
        """Update application metrics from external sources"""
        self.metrics_collector.update_app_metrics(**kwargs)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data for HTTP requests"""
        return {
            "current_metrics": self.metrics_collector.get_current_metrics(),
            "historical_data": self.metrics_collector.get_historical_data(60),
            "performance_summary": self.metrics_collector.get_performance_summary(),
            "active_clients": len(self.active_clients),
            "monitoring_active": self.monitoring_active,
        }


# Global performance dashboard instance
performance_dashboard = None


def init_performance_dashboard(socketio: SocketIO) -> PerformanceDashboard:
    """Initialize performance dashboard"""
    global performance_dashboard
    performance_dashboard = PerformanceDashboard(socketio)
    logger.info("🚀 Performance dashboard initialized")
    return performance_dashboard


def get_performance_dashboard() -> Optional[PerformanceDashboard]:
    """Get performance dashboard instance"""
    return performance_dashboard


# Blueprint for dashboard routes
dashboard_bp = Blueprint('performance_dashboard', __name__)


@dashboard_bp.route('/api/performance/current')
def get_current_performance():
    """Get current performance metrics"""
    if not performance_dashboard:
        return jsonify({"error": "Performance dashboard not initialized"}), 503
    
    return jsonify(performance_dashboard.metrics_collector.get_current_metrics())


@dashboard_bp.route('/api/performance/historical')
def get_historical_performance():
    """Get historical performance data"""
    if not performance_dashboard:
        return jsonify({"error": "Performance dashboard not initialized"}), 503
    
    minutes = request.args.get('minutes', 60, type=int)
    return jsonify(performance_dashboard.metrics_collector.get_historical_data(minutes))


@dashboard_bp.route('/api/performance/summary')
def get_performance_summary():
    """Get performance summary and health score"""
    if not performance_dashboard:
        return jsonify({"error": "Performance dashboard not initialized"}), 503
    
    return jsonify(performance_dashboard.metrics_collector.get_performance_summary())


@dashboard_bp.route('/api/performance/dashboard')
def get_dashboard_data():
    """Get complete dashboard data"""
    if not performance_dashboard:
        return jsonify({"error": "Performance dashboard not initialized"}), 503
    
    return jsonify(performance_dashboard.get_dashboard_data())


@dashboard_bp.route('/performance-dashboard')
def performance_dashboard_page():
    """Render performance dashboard page"""
    return render_template('performance_dashboard.html')
