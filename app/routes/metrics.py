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
import time

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
        metrics_text = metrics_collector.get_prometheus_metrics()

        # If the collector has no metrics yet, expose a small compatibility
        # Prometheus payload so legacy checks (and tests) that expect
        # `routeforce_cpu_usage` / `routeforce_memory_usage` continue to work.
        if not metrics_text or not metrics_text.strip():
            try:
                cpu_percent = psutil.cpu_percent(interval=0.5)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage("/")

                app_metrics = []
                app_metrics.append("# HELP routeforce_cpu_usage CPU usage percentage")
                app_metrics.append("# TYPE routeforce_cpu_usage gauge")
                app_metrics.append(f"routeforce_cpu_usage {cpu_percent}")

                app_metrics.append("# HELP routeforce_memory_usage Memory usage percentage")
                app_metrics.append("# TYPE routeforce_memory_usage gauge")
                app_metrics.append(f"routeforce_memory_usage {memory.percent}")

                app_metrics.append("# HELP routeforce_disk_usage Disk usage percentage")
                app_metrics.append("# TYPE routeforce_disk_usage gauge")
                app_metrics.append(f"routeforce_disk_usage {disk.percent}")

                app_metrics.append("# HELP routeforce_uptime Application uptime in seconds")
                app_metrics.append("# TYPE routeforce_uptime counter")
                app_metrics.append(f"routeforce_uptime {time.time() - psutil.boot_time()}")

                metrics_text = "\n".join(app_metrics)
            except Exception:
                # Fallback to an explicit empty metrics payload if system metrics fail
                metrics_text = "# Metrics temporarily unavailable\n"

        try:
            logger.debug("Prometheus metrics payload generated; length=%d", len(metrics_text))
            logger.debug("metrics preview: %s", repr(metrics_text[:200]))
        except Exception:
            pass

        # Return bytes and set Content-Length explicitly to ensure WSGI includes body
        body_bytes = metrics_text.encode("utf-8")
        resp = Response(body_bytes, mimetype="text/plain; version=0.0.4; charset=utf-8")
        try:
            resp.headers["Content-Length"] = str(len(body_bytes))
        except Exception:
            pass
        return resp
    except Exception as e:
        logger.error(f"Failed to export Prometheus metrics: {e}")
        return Response("# Metrics export failed\n", mimetype="text/plain", status=500)


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
