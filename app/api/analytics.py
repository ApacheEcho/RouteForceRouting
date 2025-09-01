"""
Analytics API Blueprint for RouteForce Routing
Provides analytics endpoints for monitoring and business intelligence
"""

import logging
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request

from app.security import require_api_key
# Import services

# Initialize blueprint
analytics_bp = Blueprint("analytics_api", __name__)

# Use the app-wide rate limiter configured in app.__init__
from app import limiter as app_limiter

# Configure logging
logger = logging.getLogger(__name__)


def get_analytics_service():
    """Get analytics service from app context"""
    return getattr(current_app, "analytics_service", None)


@analytics_bp.route("/health", methods=["GET"])
@app_limiter.limit("30 per minute")
def analytics_health_check():
    """
    Analytics API health check endpoint
    ---
    tags:
      - Analytics
    summary: Health check for Analytics API
    description: Returns service status and capabilities for the analytics service
    responses:
      200:
        description: Service is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: "healthy"
            service:
              type: string
              example: "RouteForce Analytics API"
            version:
              type: string
              example: "1.0.0"
            timestamp:
              type: string
              format: date-time
            capabilities:
              type: array
              items:
                type: string
              example: ["mobile_analytics", "driver_performance", "route_optimization_analytics"]
      500:
        description: Health check failed
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Health check failed"
    """
    try:
        return (
            jsonify(
                {
                    "status": "healthy",
                    "service": "RouteForce Analytics API",
                    "version": "1.0.0",
                    "timestamp": datetime.utcnow().isoformat(),
                    "capabilities": [
                        "mobile_analytics",
                        "driver_performance",
                        "route_optimization_analytics",
                        "api_usage_analytics",
                        "system_health_monitoring",
                        "real_time_reporting",
                    ],
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Analytics health check failed: {e}")
        return jsonify({"error": "Health check failed"}), 500


@analytics_bp.route("/mobile", methods=["GET"])
@app_limiter.limit("20 per minute")
@require_api_key
def get_mobile_analytics():
    """
    Get mobile app usage analytics
    ---
    tags:
      - Analytics
    summary: Get mobile app usage analytics
    description: Retrieve analytics data for mobile app usage with specified timeframe
    security:
      - ApiKeyAuth: []
    parameters:
      - name: timeframe
        in: query
        type: string
        enum: ["1h", "24h", "7d", "30d"]
        default: "24h"
        description: Time period for analytics data
        required: false
    responses:
      200:
        description: Mobile analytics data retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              description: Mobile analytics data
            generated_at:
              type: string
              format: date-time
      400:
        description: Invalid timeframe parameter
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Invalid timeframe. Use: 1h, 24h, 7d, 30d"
      401:
        description: Unauthorized - invalid API key
      500:
        description: Failed to retrieve mobile analytics
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Failed to retrieve mobile analytics"
      503:
        description: Analytics service not available
    """
    try:
        timeframe = request.args.get("timeframe", "24h")

        if timeframe not in ["1h", "24h", "7d", "30d"]:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Invalid timeframe. Use: 1h, 24h, 7d, 30d",
                    }
                ),
                400,
            )

        analytics_service = get_analytics_service()
        if not analytics_service:
            return (
                jsonify({"success": False, "error": "Analytics service not available"}),
                503,
            )

        analytics_data = analytics_service.get_mobile_analytics(timeframe)

        return (
            jsonify(
                {
                    "success": True,
                    "data": analytics_data,
                    "generated_at": datetime.utcnow().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Mobile analytics request failed: {e}")
        return (
            jsonify({"success": False, "error": "Failed to retrieve mobile analytics"}),
            500,
        )


@analytics_bp.route("/drivers", methods=["GET"])
@app_limiter.limit("20 per minute")
@require_api_key
def get_driver_analytics():
    """
    Get driver performance analytics
    ---
    tags:
      - Analytics
    summary: Get driver performance analytics
    description: Retrieve analytics data for driver performance metrics
    security:
      - ApiKeyAuth: []
    parameters:
      - name: timeframe
        in: query
        type: string
        enum: ["1h", "24h", "7d", "30d"]
        default: "24h"
        description: Time period for analytics data
        required: false
    responses:
      200:
        description: Driver analytics data retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              description: Driver performance analytics data
            generated_at:
              type: string
              format: date-time
      400:
        description: Invalid timeframe parameter
      401:
        description: Unauthorized - invalid API key
      500:
        description: Failed to retrieve driver analytics
      503:
        description: Analytics service not available
    """
    try:
        timeframe = request.args.get("timeframe", "24h")

        if timeframe not in ["1h", "24h", "7d", "30d"]:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Invalid timeframe. Use: 1h, 24h, 7d, 30d",
                    }
                ),
                400,
            )

        analytics_service = get_analytics_service()
        if not analytics_service:
            return (
                jsonify({"success": False, "error": "Analytics service not available"}),
                503,
            )

        analytics_data = analytics_service.get_driver_analytics(timeframe)

        return (
            jsonify(
                {
                    "success": True,
                    "data": analytics_data,
                    "generated_at": datetime.utcnow().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Driver analytics request failed: {e}")
        return (
            jsonify({"success": False, "error": "Failed to retrieve driver analytics"}),
            500,
        )


@analytics_bp.route("/routes", methods=["GET"])
@app_limiter.limit("20 per minute")
@require_api_key
def get_route_analytics():
    """
    Get route optimization analytics
    Query params: timeframe (1h, 24h, 7d, 30d)
    """
    try:
        timeframe = request.args.get("timeframe", "24h")

        if timeframe not in ["1h", "24h", "7d", "30d"]:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Invalid timeframe. Use: 1h, 24h, 7d, 30d",
                    }
                ),
                400,
            )

        analytics_service = get_analytics_service()
        if not analytics_service:
            return (
                jsonify({"success": False, "error": "Analytics service not available"}),
                503,
            )

        analytics_data = analytics_service.get_route_analytics(timeframe)

        return (
            jsonify(
                {
                    "success": True,
                    "data": analytics_data,
                    "generated_at": datetime.utcnow().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Route analytics request failed: {e}")
        return (
            jsonify({"success": False, "error": "Failed to retrieve route analytics"}),
            500,
        )


@analytics_bp.route("/api-usage", methods=["GET"])
@app_limiter.limit("20 per minute")
@require_api_key
def get_api_analytics():
    """
    Get API usage and performance analytics
    Query params: timeframe (1h, 24h, 7d, 30d)
    """
    try:
        timeframe = request.args.get("timeframe", "24h")

        if timeframe not in ["1h", "24h", "7d", "30d"]:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Invalid timeframe. Use: 1h, 24h, 7d, 30d",
                    }
                ),
                400,
            )

        analytics_service = get_analytics_service()
        if not analytics_service:
            return (
                jsonify({"success": False, "error": "Analytics service not available"}),
                503,
            )

        analytics_data = analytics_service.get_api_analytics(timeframe)

        return (
            jsonify(
                {
                    "success": True,
                    "data": analytics_data,
                    "generated_at": datetime.utcnow().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"API analytics request failed: {e}")
        return (
            jsonify({"success": False, "error": "Failed to retrieve API analytics"}),
            500,
        )


@analytics_bp.route("/system-health", methods=["GET"])
@app_limiter.limit("30 per minute")
@require_api_key
def get_system_health():
    """
    Get overall system health metrics
    """
    try:
        analytics_service = get_analytics_service()
        if not analytics_service:
            return (
                jsonify({"success": False, "error": "Analytics service not available"}),
                503,
            )

        health_data = analytics_service.get_system_health()

        return (
            jsonify(
                {
                    "success": True,
                    "data": health_data,
                    "generated_at": datetime.utcnow().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"System health request failed: {e}")
        return (
            jsonify({"success": False, "error": "Failed to retrieve system health"}),
            500,
        )


@analytics_bp.route("/report", methods=["GET"])
@app_limiter.limit("10 per minute")
@require_api_key
def get_analytics_report():
    """
    Generate comprehensive analytics report
    Query params: timeframe (1h, 24h, 7d, 30d)
    """
    try:
        timeframe = request.args.get("timeframe", "24h")

        if timeframe not in ["1h", "24h", "7d", "30d"]:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Invalid timeframe. Use: 1h, 24h, 7d, 30d",
                    }
                ),
                400,
            )

        analytics_service = get_analytics_service()
        if not analytics_service:
            return (
                jsonify({"success": False, "error": "Analytics service not available"}),
                503,
            )

        report_data = analytics_service.generate_analytics_report(timeframe)

        return (
            jsonify(
                {
                    "success": True,
                    "data": report_data,
                    "generated_at": datetime.utcnow().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Analytics report request failed: {e}")
        return (
            jsonify({"success": False, "error": "Failed to generate analytics report"}),
            500,
        )


@analytics_bp.route("/track/session", methods=["POST"])
@app_limiter.limit("100 per minute")
@require_api_key
def track_mobile_session():
    """
    Track mobile app session for analytics
    ---
    tags:
      - Analytics
    summary: Track mobile app session
    description: Track mobile app session data for analytics purposes
    security:
      - ApiKeyAuth: []
    parameters:
      - name: session_data
        in: body
        required: true
        schema:
          type: object
          required:
            - device_id
          properties:
            device_id:
              type: string
              description: Unique device identifier
              example: "device_123456"
            app_version:
              type: string
              description: Application version
              example: "1.0.0"
            device_type:
              type: string
              description: Type of device
              example: "mobile"
            features_used:
              type: array
              items:
                type: string
              description: List of features used in session
              example: ["routing", "maps", "analytics"]
            api_calls:
              type: integer
              description: Number of API calls made
              example: 15
    responses:
      200:
        description: Session tracked successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Session tracked successfully"
      400:
        description: Bad request - device_id is required
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "device_id is required"
      401:
        description: Unauthorized - invalid API key
      500:
        description: Failed to track session
      503:
        description: Analytics service not available
    """
    try:
        data = request.get_json()

        if not data or "device_id" not in data:
            return jsonify({"success": False, "error": "device_id is required"}), 400

        analytics_service = get_analytics_service()
        if not analytics_service:
            return (
                jsonify({"success": False, "error": "Analytics service not available"}),
                503,
            )

        device_id = data["device_id"]
        session_data = {
            "app_version": data.get("app_version"),
            "device_type": data.get("device_type"),
            "features_used": data.get("features_used", []),
            "api_calls": data.get("api_calls", 0),
        }

        analytics_service.track_mobile_session(device_id, session_data)

        return (
            jsonify({"success": True, "message": "Session tracked successfully"}),
            200,
        )

    except Exception as e:
        logger.error(f"Session tracking failed: {e}")
        return jsonify({"success": False, "error": "Failed to track session"}), 500


@analytics_bp.route("/track/driver", methods=["POST"])
@app_limiter.limit("100 per minute")
@require_api_key
def track_driver_performance():
    """
    Track driver performance metrics
    """
    try:
        data = request.get_json()

        if not data or "driver_id" not in data:
            return jsonify({"success": False, "error": "driver_id is required"}), 400

        analytics_service = get_analytics_service()
        if not analytics_service:
            return (
                jsonify({"success": False, "error": "Analytics service not available"}),
                503,
            )

        driver_id = data["driver_id"]
        metrics = {
            "location_accuracy": data.get("location_accuracy"),
            "speed": data.get("speed"),
            "route_deviation": data.get("route_deviation"),
            "stops_completed": data.get("stops_completed"),
            "time_at_stop": data.get("time_at_stop"),
            "fuel_efficiency": data.get("fuel_efficiency"),
            "customer_rating": data.get("customer_rating"),
        }

        analytics_service.track_driver_performance(driver_id, metrics)

        return (
            jsonify(
                {"success": True, "message": "Driver performance tracked successfully"}
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Driver performance tracking failed: {e}")
        return (
            jsonify({"success": False, "error": "Failed to track driver performance"}),
            500,
        )


@analytics_bp.route("/track/route", methods=["POST"])
@app_limiter.limit("100 per minute")
@require_api_key
def track_route_optimization():
    """
    Track route optimization performance
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "Route data is required"}), 400

        analytics_service = get_analytics_service()
        if not analytics_service:
            return (
                jsonify({"success": False, "error": "Analytics service not available"}),
                503,
            )

        route_data = {
            "route_id": data.get("route_id"),
            "algorithm": data.get("algorithm"),
            "stores": data.get("stores", []),
            "optimization_time": data.get("optimization_time"),
            "total_distance": data.get("total_distance"),
            "total_time": data.get("total_time"),
            "improvement_percentage": data.get("improvement_percentage"),
            "success": data.get("success", False),
            "traffic_aware": data.get("traffic_aware", False),
        }

        analytics_service.track_route_optimization(route_data)

        return (
            jsonify(
                {"success": True, "message": "Route optimization tracked successfully"}
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Route optimization tracking failed: {e}")
        return (
            jsonify({"success": False, "error": "Failed to track route optimization"}),
            500,
        )


@analytics_bp.route("/track/event", methods=["POST"])
@app_limiter.limit("100 per minute")
@require_api_key
def track_system_event():
    """
    Track system events for monitoring
    """
    try:
        data = request.get_json()

        if not data or "event_type" not in data:
            return jsonify({"success": False, "error": "event_type is required"}), 400

        analytics_service = get_analytics_service()
        if not analytics_service:
            return (
                jsonify({"success": False, "error": "Analytics service not available"}),
                503,
            )

        event_type = data["event_type"]
        event_data = data.get("event_data", {})

        analytics_service.track_system_event(event_type, event_data)

        return (
            jsonify({"success": True, "message": "System event tracked successfully"}),
            200,
        )

    except Exception as e:
        logger.error(f"System event tracking failed: {e}")
        return jsonify({"success": False, "error": "Failed to track system event"}), 500


# Error handlers for analytics blueprint
@analytics_bp.errorhandler(400)
def analytics_bad_request(error):
    return (
        jsonify({"success": False, "error": "Bad request", "service": "analytics"}),
        400,
    )


@analytics_bp.errorhandler(401)
def analytics_unauthorized(error):
    return (
        jsonify({"success": False, "error": "Unauthorized", "service": "analytics"}),
        401,
    )


@analytics_bp.errorhandler(429)
def analytics_rate_limit(error):
    return (
        jsonify(
            {
                "success": False,
                "error": "Rate limit exceeded",
                "service": "analytics",
                "retry_after": "60 seconds",
            }
        ),
        429,
    )


@analytics_bp.errorhandler(500)
def analytics_server_error(error):
    return (
        jsonify({"success": False, "error": "Server error", "service": "analytics"}),
        500,
    )
