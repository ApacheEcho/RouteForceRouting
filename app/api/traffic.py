"""
Traffic-aware routing API endpoints
Provides REST API for traffic optimization features
"""

from flask import Blueprint, request, jsonify, current_app
from app.services.routing_service import RoutingService
import logging
import time

# Create blueprint
traffic_bp = Blueprint("traffic", __name__, url_prefix="/api/traffic")
logger = logging.getLogger(__name__)


@traffic_bp.route("/optimize", methods=["POST"])
def optimize_route_with_traffic():
    """
    Generate traffic-optimized route
    ---
    tags:
      - Traffic
    summary: Optimize a route considering live traffic
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [stores]
          properties:
            stores:
              type: array
              items:
                $ref: '#/definitions/TrafficStop'
            constraints:
              type: object
            start_location:
              $ref: '#/definitions/TrafficStop'
    responses:
      200:
        description: Traffic-optimized route returned
        examples:
          application/json:
            success: true
            route: [ { name: Store A, lat: 40.71, lng: -74.0 }, { name: Store B, lat: 40.76, lng: -73.98 } ]
            traffic_data: { delay_minutes: 3 }
            metrics: { total_distance: 12.3, total_duration: 1800, traffic_delay: 180, processing_time: 0.12 }
            algorithm_used: traffic_optimized
      400:
        description: Bad request
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Server error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    try:
        data = request.get_json()

        if not data or "stores" not in data:
            return (
                jsonify(
                    {"success": False, "error": "Stores data is required"}
                ),
                400,
            )

        stores = data["stores"]
        constraints = data.get("constraints", {})
        start_location = data.get("start_location")

        if not stores:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "At least one store is required",
                    }
                ),
                400,
            )

        # Create routing service
        routing_service = RoutingService()

        # Generate traffic-optimized route
        result = routing_service.generate_traffic_optimized_route(
            stores, constraints, start_location
        )

        if result["success"]:
            return jsonify(
                {
                    "success": True,
                    "route": result["route"],
                    "traffic_data": result.get("traffic_data", {}),
                    "metrics": {
                        "total_distance": result.get("total_distance", 0),
                        "total_duration": result.get("total_duration", 0),
                        "traffic_delay": result.get("traffic_delay", 0),
                        "processing_time": routing_service.last_processing_time,
                    },
                    "algorithm_used": result.get(
                        "algorithm_used", "traffic_optimized"
                    ),
                }
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": result.get(
                            "error", "Traffic optimization failed"
                        ),
                        "fallback_route": result.get("route", []),
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error in traffic optimization API: {str(e)}")
        return (
            jsonify(
                {"success": False, "error": f"Internal server error: {str(e)}"}
            ),
            500,
        )


@traffic_bp.route("/alternatives", methods=["POST"])
def get_route_alternatives():
    """
    Get alternative routes with traffic analysis

    Expected JSON:
    {
        "stores": [{"lat": float, "lng": float, "name": str, ...}],
        "max_alternatives": int (optional, default 3)
    }
    """
    try:
        data = request.get_json()

        if not data or "stores" not in data:
            return (
                jsonify(
                    {"success": False, "error": "Stores data is required"}
                ),
                400,
            )

        stores = data["stores"]
        max_alternatives = data.get("max_alternatives", 3)

        if not stores:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "At least one store is required",
                    }
                ),
                400,
            )

        # Create routing service
        routing_service = RoutingService()

        # Get alternatives
        result = routing_service.get_traffic_alternatives(
            stores, max_alternatives
        )

        if result["success"]:
            return jsonify(
                {
                    "success": True,
                    "alternatives": result["alternatives"],
                    "best_alternative": result["best_alternative"],
                    "recommendation": result.get("recommendation", {}),
                    "processing_time": routing_service.last_processing_time,
                }
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": result.get(
                            "error", "Failed to generate alternatives"
                        ),
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error in traffic alternatives API: {str(e)}")
        return (
            jsonify(
                {"success": False, "error": f"Internal server error: {str(e)}"}
            ),
            500,
        )


@traffic_bp.route("/predict", methods=["POST"])
def predict_traffic():
    """
    Predict traffic conditions for future departure times
    ---
    tags:
      - Traffic
    summary: Predict traffic along a route for given future hours
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [stores]
          properties:
            stores:
              type: array
              items:
                $ref: '#/definitions/TrafficStop'
            future_hours:
              type: array
              items: { type: integer }
              default: [1, 2, 4, 8]
    responses:
      200:
        description: Traffic prediction available
        examples:
          application/json:
            success: true
            predictions: [ { hour: 1, delay_minutes: 2 }, { hour: 2, delay_minutes: 5 } ]
            best_time: { hour: 1 }
            recommendation: { depart_after_hours: 1 }
            processing_time: 0.06
      400:
        description: Bad request
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Server error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    try:
        data = request.get_json()

        if not data or "stores" not in data:
            return (
                jsonify(
                    {"success": False, "error": "Stores data is required"}
                ),
                400,
            )

        stores = data["stores"]
        future_hours = data.get("future_hours", [1, 2, 4, 8])

        if not stores:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "At least one store is required",
                    }
                ),
                400,
            )

        # Create routing service
        routing_service = RoutingService()

        # Get traffic predictions
        result = routing_service.predict_traffic_for_route(
            stores, future_hours
        )

        if result.get("success"):
            return jsonify(
                {
                    "success": True,
                    "predictions": result["predictions"],
                    "best_time": result.get("best_time"),
                    "recommendation": result.get("recommendation", {}),
                    "processing_time": routing_service.last_processing_time,
                }
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": result.get(
                            "error", "Traffic prediction failed"
                        ),
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error in traffic prediction API: {str(e)}")
        return (
            jsonify({"success": False, "error": "An internal error occurred. Please contact support."}),
            500,
        )


@traffic_bp.route("/segment", methods=["POST"])
def get_segment_traffic():
    """
    Get traffic data for a specific route segment

    Expected JSON:
    {
        "origin": {"lat": float, "lng": float},
        "destination": {"lat": float, "lng": float}
    }
    """
    try:
        data = request.get_json()

        if not data or "origin" not in data or "destination" not in data:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Origin and destination are required",
                    }
                ),
                400,
            )

        origin = data["origin"]
        destination = data["destination"]

        # Validate coordinates
        for location in [origin, destination]:
            if "lat" not in location or "lng" not in location:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Locations must have lat and lng coordinates",
                        }
                    ),
                    400,
                )

        # Create routing service
        routing_service = RoutingService()

        # Get segment traffic data
        traffic_data = routing_service.get_traffic_segment_data(
            origin, destination
        )

        if traffic_data:
            return jsonify({"success": True, "traffic_data": traffic_data})
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Could not retrieve traffic data for segment",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error in segment traffic API: {str(e)}")
        return (
            jsonify(
                {"success": False, "error": f"Internal server error: {str(e)}"}
            ),
            500,
        )


@traffic_bp.route("/status", methods=["GET"])
def get_traffic_service_status():
    """Get status of traffic service and Google Maps API
    ---
    tags:
      - Traffic
    summary: Get traffic subsystem status and cache stats
    responses:
      200:
        description: Service status returned
        examples:
          application/json:
            available: true
            api_key_configured: true
            cache_stats: { hits: 12, misses: 3 }
            config: { cache_duration: 3600, max_waypoints: 23, avoid_tolls: false, avoid_highways: false, avoid_ferries: false, traffic_model: best_guess }
      500:
        description: Server error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    try:
        routing_service = RoutingService()

        if not routing_service.traffic_service:
            return jsonify(
                {
                    "available": False,
                    "reason": "Traffic service not initialized",
                }
            )

        traffic_service = routing_service.traffic_service

        # Get cache statistics
        cache_stats = traffic_service.get_cache_stats()

        return jsonify(
            {
                "available": traffic_service.api_available,
                "api_key_configured": bool(traffic_service.api_key),
                "cache_stats": cache_stats,
                "config": {
                    "cache_duration": traffic_service.config.cache_duration,
                    "max_waypoints": traffic_service.config.max_waypoints,
                    "avoid_tolls": traffic_service.config.avoid_tolls,
                    "avoid_highways": traffic_service.config.avoid_highways,
                    "avoid_ferries": traffic_service.config.avoid_ferries,
                    "traffic_model": traffic_service.config.traffic_model,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error getting traffic service status: {str(e)}")
        return jsonify({"available": False, "error": "An internal error occurred. Please contact support."}), 500


@traffic_bp.route("/cache/clear", methods=["POST"])
def clear_traffic_cache():
    """Clear the traffic data cache"""
    try:
        routing_service = RoutingService()

        if not routing_service.traffic_service:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Traffic service not available",
                    }
                ),
                503,
            )

        routing_service.traffic_service.clear_cache()

        return jsonify(
            {"success": True, "message": "Traffic cache cleared successfully"}
        )

    except Exception as e:
        logger.error(f"Error clearing traffic cache: {str(e)}")
        return (
            jsonify({"success": False, "error": "An internal error occurred. Please contact support."}),
            500,
        )


@traffic_bp.errorhandler(400)
def bad_request(error):
    return (
        jsonify(
            {"success": False, "error": "Bad request", "message": str(error)}
        ),
        400,
    )


@traffic_bp.errorhandler(500)
def internal_error(error):
    return (
        jsonify(
            {
                "success": False,
                "error": "Internal server error",
                "message": str(error),
            }
        ),
        500,
    )
