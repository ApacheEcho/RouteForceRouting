"""
Performance Monitoring API Blueprint
Provides endpoints for real-time performance metrics and system health
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from typing import Dict, Any

from app.auth_decorators import admin_required, analytics_access_required, audit_log
from app.performance_monitor import get_performance_monitor

monitoring_bp = Blueprint("monitoring", __name__, url_prefix="/api/monitoring")


@monitoring_bp.route("/health", methods=["GET"])
def health_check():
    """Basic health check endpoint (no auth required)"""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "RouteForce Enhanced System",
            "version": "2.0",
        }
    )


@monitoring_bp.route("/metrics/current", methods=["GET"])
@analytics_access_required
@audit_log("view_current_metrics", "performance_metrics")
def get_current_metrics():
    """Get current performance metrics"""
    try:
        monitor = get_performance_monitor()
        metrics = monitor.get_current_metrics()

        return jsonify(
            {
                "success": True,
                "metrics": metrics,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        current_app.logger.error(f"Error retrieving current metrics: {str(e)}")
        return (
            jsonify({"success": False, "error": "Failed to retrieve current metrics"}),
            500,
        )


@monitoring_bp.route("/metrics/history/<metric_type>", methods=["GET"])
@analytics_access_required
@audit_log("view_metrics_history", "performance_metrics")
def get_metrics_history(metric_type: str):
    """Get historical metrics for a specific type"""
    try:
        hours = int(request.args.get("hours", 1))
        if hours > 24:
            hours = 24  # Limit to 24 hours

        monitor = get_performance_monitor()
        history = monitor.get_metrics_history(metric_type, hours)

        return jsonify(
            {
                "success": True,
                "metric_type": metric_type,
                "history": history,
                "hours": hours,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except ValueError:
        return jsonify({"success": False, "error": "Invalid hours parameter"}), 400
    except Exception as e:
        current_app.logger.error(f"Error retrieving metrics history: {str(e)}")
        return (
            jsonify({"success": False, "error": "Failed to retrieve metrics history"}),
            500,
        )


@monitoring_bp.route("/alerts", methods=["GET"])
@analytics_access_required
@audit_log("view_alerts", "system_alerts")
def get_alerts():
    """Get active system alerts"""
    try:
        severity = request.args.get("severity")  # optional filter

        monitor = get_performance_monitor()
        alerts = monitor.get_active_alerts(severity)

        return jsonify(
            {
                "success": True,
                "alerts": alerts,
                "count": len(alerts),
                "filtered_by": severity,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        current_app.logger.error(f"Error retrieving alerts: {str(e)}")
        return jsonify({"success": False, "error": "Failed to retrieve alerts"}), 500


@monitoring_bp.route("/alerts/<alert_id>/acknowledge", methods=["POST"])
@admin_required
@audit_log("acknowledge_alert", "system_alerts")
def acknowledge_alert(alert_id: str):
    """Acknowledge a system alert"""
    try:
        monitor = get_performance_monitor()
        success = monitor.acknowledge_alert(alert_id)

        if success:
            return jsonify(
                {
                    "success": True,
                    "message": f"Alert {alert_id} acknowledged",
                    "timestamp": datetime.now().isoformat(),
                }
            )
        else:
            return (
                jsonify({"success": False, "error": f"Alert {alert_id} not found"}),
                404,
            )

    except Exception as e:
        current_app.logger.error(f"Error acknowledging alert: {str(e)}")
        return jsonify({"success": False, "error": "Failed to acknowledge alert"}), 500


@monitoring_bp.route("/health/score", methods=["GET"])
@analytics_access_required
@audit_log("view_health_score", "system_health")
def get_health_score():
    """Get overall system health score"""
    try:
        monitor = get_performance_monitor()
        health_score = monitor.get_system_health_score()

        return jsonify(
            {
                "success": True,
                "health_score": health_score,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        current_app.logger.error(f"Error retrieving health score: {str(e)}")
        return (
            jsonify({"success": False, "error": "Failed to retrieve health score"}),
            500,
        )


@monitoring_bp.route("/summary", methods=["GET"])
@analytics_access_required
@audit_log("view_performance_summary", "performance_summary")
def get_performance_summary():
    """Get comprehensive performance summary"""
    try:
        monitor = get_performance_monitor()
        summary = monitor.get_performance_summary()

        return jsonify({"success": True, "summary": summary})

    except Exception as e:
        current_app.logger.error(f"Error retrieving performance summary: {str(e)}")
        return (
            jsonify(
                {"success": False, "error": "Failed to retrieve performance summary"}
            ),
            500,
        )


@monitoring_bp.route("/start", methods=["POST"])
@admin_required
@audit_log("start_monitoring", "system_control")
def start_monitoring():
    """Start performance monitoring"""
    try:
        monitor = get_performance_monitor()
        monitor.start_monitoring()

        return jsonify(
            {
                "success": True,
                "message": "Performance monitoring started",
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        current_app.logger.error(f"Error starting monitoring: {str(e)}")
        return jsonify({"success": False, "error": "Failed to start monitoring"}), 500


@monitoring_bp.route("/stop", methods=["POST"])
@admin_required
@audit_log("stop_monitoring", "system_control")
def stop_monitoring():
    """Stop performance monitoring"""
    try:
        monitor = get_performance_monitor()
        monitor.stop_monitoring()

        return jsonify(
            {
                "success": True,
                "message": "Performance monitoring stopped",
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        current_app.logger.error(f"Error stopping monitoring: {str(e)}")
        return jsonify({"success": False, "error": "Failed to stop monitoring"}), 500


@monitoring_bp.route("/thresholds", methods=["GET"])
@admin_required
@audit_log("view_thresholds", "system_configuration")
def get_monitoring_thresholds():
    """Get current monitoring thresholds"""
    try:
        monitor = get_performance_monitor()
        thresholds = monitor.thresholds

        return jsonify(
            {
                "success": True,
                "thresholds": thresholds,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        current_app.logger.error(f"Error retrieving thresholds: {str(e)}")
        return (
            jsonify({"success": False, "error": "Failed to retrieve thresholds"}),
            500,
        )


@monitoring_bp.route("/thresholds", methods=["PUT"])
@admin_required
@audit_log("update_thresholds", "system_configuration")
def update_monitoring_thresholds():
    """Update monitoring thresholds"""
    try:
        data = request.get_json()
        if not data:
            return (
                jsonify({"success": False, "error": "No threshold data provided"}),
                400,
            )

        monitor = get_performance_monitor()

        # Validate and update thresholds
        for metric_type, thresholds in data.items():
            if metric_type in monitor.thresholds:
                if "warning" in thresholds:
                    monitor.thresholds[metric_type]["warning"] = float(
                        thresholds["warning"]
                    )
                if "critical" in thresholds:
                    monitor.thresholds[metric_type]["critical"] = float(
                        thresholds["critical"]
                    )

        return jsonify(
            {
                "success": True,
                "message": "Thresholds updated successfully",
                "updated_thresholds": monitor.thresholds,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except (ValueError, TypeError) as e:
        return (
            jsonify({"success": False, "error": f"Invalid threshold values: {str(e)}"}),
            400,
        )
    except Exception as e:
        current_app.logger.error(f"Error updating thresholds: {str(e)}")
        return jsonify({"success": False, "error": "Failed to update thresholds"}), 500


@monitoring_bp.route("/system/info", methods=["GET"])
@analytics_access_required
@audit_log("view_system_info", "system_info")
def get_system_info():
    """Get basic system information"""
    try:
        import psutil
        import platform

        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "disk_total": psutil.disk_usage("/").total,
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "process_count": len(psutil.pids()),
        }

        return jsonify(
            {
                "success": True,
                "system_info": system_info,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        current_app.logger.error(f"Error retrieving system info: {str(e)}")
        return (
            jsonify(
                {"success": False, "error": "Failed to retrieve system information"}
            ),
            500,
        )
