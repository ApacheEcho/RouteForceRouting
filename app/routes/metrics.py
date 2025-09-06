"""
Metrics API Blueprint - Prometheus-compatible metrics endpoint
Provides /metrics endpoint for monitoring and observability

Optional protection: set environment variable METRICS_TOKEN to require a matching
`X-Metrics-Token` header or `?token=` query parameter for access. If unset, endpoints
remain publicly accessible (default behavior).
"""

import logging
import os

from flask import Blueprint, Response, jsonify, request, abort
import psutil

from app.services.metrics_service import metrics_collector

logger = logging.getLogger(__name__)

metrics_bp = Blueprint("metrics", __name__)


@metrics_bp.before_request
def _protect_metrics():
    """Protect metrics with optional token if METRICS_TOKEN is set.

    Exempts the lightweight health probe at /metrics/health.
    """
    # Allow health probe without token
    if request.endpoint and request.endpoint.endswith("metrics_health"):
        return

    required = os.getenv("METRICS_TOKEN")
    if not required:
        return  # No protection configured

    provided = request.headers.get("X-Metrics-Token") or request.args.get("token")
    if provided != required:
        abort(401, description="Unauthorized: invalid or missing metrics token")


@metrics_bp.route("/metrics", methods=["GET"])
def prometheus_metrics():
    """
    Prometheus-compatible metrics endpoint
    Returns metrics in Prometheus exposition format
    """
    try:
        # Ensure basic system metrics are present
        try:
            metrics_collector.set_gauge(
                "routeforce_cpu_usage", psutil.cpu_percent(interval=None)
            )
            metrics_collector.set_gauge(
                "routeforce_memory_usage", psutil.virtual_memory().percent
            )
        except Exception:
            pass
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
