"""
Metrics API Blueprint - Prometheus-compatible metrics endpoint
Provides /metrics endpoint for monitoring and observability
"""

import logging

from flask import Blueprint, Response, jsonify

from app.services.metrics_service import metrics_collector

logger = logging.getLogger(__name__)

metrics_bp = Blueprint("metrics", __name__)


@metrics_bp.route("/metrics", methods=["GET"])
def prometheus_metrics():
    """
    Prometheus-compatible metrics endpoint
    Returns metrics in Prometheus exposition format
    """
    try:
        metrics_text = metrics_collector.get_prometheus_metrics()
        return Response(
            metrics_text, mimetype="text/plain; version=0.0.4; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"Failed to export Prometheus metrics: {e}")
        return Response(
            "# Metrics export failed\n", mimetype="text/plain", status=500
        )


@metrics_bp.route("/metrics/summary", methods=["GET"])
def metrics_summary():
    """
    JSON metrics summary for dashboards and monitoring
    """
    try:
        summary = metrics_collector.get_metrics_summary()
        return jsonify(summary)
    except Exception as e:
        logger.error(f"Failed to get metrics summary: {e}")
        return jsonify({"error": "Failed to retrieve metrics summary"}), 500


@metrics_bp.route("/metrics/health", methods=["GET"])
def metrics_health():
    """
    Health check endpoint for metrics collection system
    """
    try:
        total_metrics = len(metrics_collector.metrics)
        services_count = len(metrics_collector.service_metrics)

        return jsonify(
            {
                "status": "healthy",
                "total_metrics": total_metrics,
                "services_monitored": services_count,
                "collection_active": True,
            }
        )
    except Exception as e:
        logger.error(f"Metrics health check failed: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


@metrics_bp.route("/metrics/clear", methods=["POST"])
def clear_metrics():
    """
    Clear all collected metrics (admin endpoint)
    """
    try:
        metrics_collector.clear_metrics()
        return jsonify({"message": "All metrics cleared successfully"})
    except Exception as e:
        logger.error(f"Failed to clear metrics: {e}")
        return jsonify({"error": "Failed to clear metrics"}), 500
