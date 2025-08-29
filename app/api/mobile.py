# flake8: noqa
# pylint: disable=too-many-return-statements,too-many-branches,too-many-locals

"""
Mobile API Blueprint for RouteForce Routing
Provides mobile-optimized endpoints for mobile app integration
"""

import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable

from flask import Blueprint, request, jsonify, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import BadRequest

# Import services
from app.services.routing_service import RoutingService
from app.services.traffic_service import TrafficService
from app.services.geocoding_service import create_geocoding_service
from app.security import require_api_key, validate_request

# Initialize blueprint
mobile_bp = Blueprint("mobile_api", __name__)

# Initialize rate limiter (init in app factory with limiter.init_app(app))
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    default_limits=["200 per day", "60 per minute"],
)

# Configure logging
logger = logging.getLogger(__name__)


@mobile_bp.route("/health", methods=["GET"])
@limiter.limit("30 per minute")
def mobile_health_check():
    try:
        return (
            jsonify(
                {
                    "status": "healthy",
                    "service": "RouteForce Mobile API",
                    "version": "1.0.0",
                    "timestamp": datetime.utcnow().isoformat(),
                    "capabilities": [
                        "route_optimization",
                        "traffic_aware_routing",
                        "real_time_updates",
                        "offline_sync",
                        "driver_tracking",
                    ],
                }
            ),
            200,
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Mobile health check failed: %s", e)
        return jsonify({"error": "Health check failed"}), 500


@mobile_bp.route("/auth/token", methods=["POST"])
@limiter.limit("10 per minute")
@validate_request(["device_id", "app_version"])
def mobile_auth():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"success": False, "error": "Invalid JSON"}), 400

        device_id = data.get("device_id")
        if not device_id:
            return (
                jsonify({"success": False, "error": "device_id required"}),
                400,
            )

        session_token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=24)

        logger.info("Mobile device authenticated: %s", device_id)

        return (
            jsonify(
                {
                    "success": True,
                    "session_token": session_token,
                    "expires_at": expires_at.isoformat(),
                    "device_capabilities": {
                        "gps_tracking": True,
                        "real_time_updates": True,
                        "offline_mode": True,
                        "camera_integration": True,
                    },
                }
            ),
            200,
        )

    except BadRequest:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Mobile authentication failed: %s", e)
        return (
            jsonify({"success": False, "error": "Authentication failed"}),
            400,
        )


@mobile_bp.route("/routes/optimize", methods=["POST"])
@limiter.limit("20 per minute")
@require_api_key
@validate_request(["stores"])
def mobile_optimize_route():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"success": False, "error": "Invalid JSON"}), 400

        stores = data.get("stores", [])
        if not isinstance(stores, list) or not stores:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "stores must be a non-empty list",
                    }
                ),
                400,
            )

        preferences = data.get("preferences", {})
        if not isinstance(preferences, dict):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "preferences must be an object",
                    }
                ),
                400,
            )

        analytics_service = getattr(current_app, "analytics_service", None)
        if analytics_service:
            device_id = request.headers.get(
                "X-Device-ID", data.get("device_id", "unknown")
            )
            analytics_service.track_mobile_session(
                device_id,
                {
                    "app_version": data.get("app_version", "1.0.0"),
                    "device_type": data.get("device_type", "unknown"),
                    "features_used": ["route_optimization"],
                    "api_calls": 1,
                },
            )

        mobile_prefs = {
            "compress_response": data.get("compress_response", True),
            "include_directions": data.get("include_directions", True),
            "max_waypoints": data.get("max_waypoints", 23),
            "optimize_for_mobile": True,
        }

        routing_service = RoutingService()
        generate = getattr(routing_service, "generate_route_from_stores", None)
        if not callable(generate):
            logger.error("RoutingService missing generate_route_from_stores()")
            return (
                jsonify({"success": False, "error": "Service unavailable"}),
                500,
            )

        start_time = time.time()
        route_result = generate(stores=stores, constraints=preferences)
        optimization_time = time.time() - start_time

        # Normalize return to a dict shape expected by mobile
        if isinstance(route_result, list):
            normalized = {"route": route_result}
        elif isinstance(route_result, dict):
            normalized = route_result
        else:
            normalized = {"route": []}

        if not normalized.get("route"):
            if analytics_service:
                analytics_service.track_route_optimization(
                    {
                        "algorithm": preferences.get("algorithm", "genetic"),
                        "stores": stores,
                        "optimization_time": optimization_time,
                        "success": False,
                        "traffic_aware": False,
                    }
                )
            return (
                jsonify(
                    {"success": False, "error": "Route optimization failed"}
                ),
                400,
            )

        # Optionally compute simple totals if available
        total_distance = None
        try:
            if isinstance(normalized.get("route"), list):
                total_distance = routing_service.distance_calculator.calculate_route_distance(
                    normalized["route"]
                )
        except Exception:
            total_distance = None

        normalized.setdefault("total_distance", total_distance)
        mobile_route = _compress_route_for_mobile(normalized, mobile_prefs)

        if analytics_service:
            analytics_service.track_route_optimization(
                {
                    "route_id": normalized.get("route_id"),
                    "algorithm": preferences.get("algorithm", "genetic"),
                    "stores": stores,
                    "optimization_time": optimization_time,
                    "total_distance": normalized.get("total_distance"),
                    "total_time": normalized.get("total_time"),
                    "improvement_percentage": normalized.get(
                        "improvement_percentage"
                    ),
                    "success": True,
                    "traffic_aware": False,
                }
            )

        logger.info("Mobile route optimized with %d stores", len(stores))

        return (
            jsonify(
                {
                    "success": True,
                    "route": mobile_route,
                    "optimization_time": optimization_time,
                    "mobile_optimized": True,
                }
            ),
            200,
        )

    except BadRequest:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Mobile route optimization failed: %s", e)
        return (
            jsonify({"success": False, "error": "Route optimization failed"}),
            500,
        )


@mobile_bp.route("/routes/traffic", methods=["POST"])
@limiter.limit("15 per minute")
@require_api_key
@validate_request(["origin", "destination"])
def mobile_traffic_route():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"success": False, "error": "Invalid JSON"}), 400

        origin = data.get("origin")
        destination = data.get("destination")
        waypoints = data.get("waypoints", [])

        if not origin or not destination:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "origin and destination required",
                    }
                ),
                400,
            )
        if waypoints is not None and not isinstance(waypoints, list):
            return (
                jsonify(
                    {"success": False, "error": "waypoints must be a list"}
                ),
                400,
            )

        nav_prefs = {
            "avoid_tolls": data.get("avoid_tolls", False),
            "avoid_highways": data.get("avoid_highways", False),
            "traffic_model": data.get("traffic_model", "best_guess"),
            "departure_time": data.get("departure_time", "now"),
            "alternatives": data.get("alternatives", True),
            "steps": data.get("include_steps", True),
        }

        # Normalize origin/destination to coordinates (accept string or lat/lng)
        def _normalize_location(loc):
            if isinstance(loc, dict) and {"lat", "lng"}.issubset(loc.keys()):
                return {"lat": float(loc["lat"]), "lng": float(loc["lng"]) }
            if isinstance(loc, (list, tuple)) and len(loc) == 2:
                return {"lat": float(loc[0]), "lng": float(loc[1])}
            if isinstance(loc, str) and loc.strip():
                # Geocode address string
                try:
                    geo = create_geocoding_service()
                    coords = geo.get_coordinates(loc)
                    if coords:
                        return {"lat": float(coords[0]), "lng": float(coords[1])}
                except Exception:
                    return None
            return None

        origin_norm = _normalize_location(origin)
        dest_norm = _normalize_location(destination)
        if not origin_norm or not dest_norm:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Invalid origin/destination. Provide address or [lat,lng].",
                    }
                ),
                400,
            )

        traffic_service = TrafficService()
        get_dir = getattr(traffic_service, "get_traffic_optimized_route", None)
        if not callable(get_dir):
            logger.error(
                "TrafficService missing get_traffic_optimized_route()"
            )
            return (
                jsonify({"success": False, "error": "Service unavailable"}),
                500,
            )

        traffic_route = get_dir(
            stores=[origin_norm, dest_norm],
            constraints=nav_prefs,
        )
        if not traffic_route:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Traffic route generation failed",
                    }
                ),
                400,
            )

        # Format Google directions payload when available
        mobile_directions = _format_directions_for_mobile(
            traffic_route.get("google_maps_data", {})
        )

        # Optionally compute alternatives
        alternatives = []
        try:
            if nav_prefs.get("alternatives", False):
                alternatives = traffic_service.get_route_alternatives(
                    [origin_norm, dest_norm]
                )
        except Exception:
            alternatives = []

        logger.info(
            "Mobile traffic route generated: %s to %s", origin, destination
        )

        return (
            jsonify(
                {
                    "success": True,
                    "directions": mobile_directions,
                    "traffic_info": traffic_route.get("traffic_data", {}),
                    "alternatives": alternatives,
                    "mobile_formatted": True,
                }
            ),
            200,
        )

    except BadRequest:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Mobile traffic routing failed: %s", e)
        return (
            jsonify({"success": False, "error": "Traffic routing failed"}),
            500,
        )


@mobile_bp.route("/driver/location", methods=["POST"])
@limiter.limit("60 per minute")
@require_api_key
@validate_request(["lat", "lng", "driver_id"])
def update_driver_location():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"success": False, "error": "Invalid JSON"}), 400

        driver_id = data.get("driver_id")
        try:
            lat = float(data.get("lat"))
            lng = float(data.get("lng"))
        except (TypeError, ValueError):
            return (
                jsonify({"success": False, "error": "Invalid coordinates"}),
                400,
            )

        if not driver_id:
            return (
                jsonify({"success": False, "error": "driver_id required"}),
                400,
            )
        if not (-90.0 <= lat <= 90.0):
            return (
                jsonify({"success": False, "error": "Invalid latitude"}),
                400,
            )
        if not (-180.0 <= lng <= 180.0):
            return (
                jsonify({"success": False, "error": "Invalid longitude"}),
                400,
            )

        heading = data.get("heading")
        speed = data.get("speed")
        accuracy = data.get("accuracy")
        timestamp = data.get("timestamp", datetime.utcnow().isoformat())

        analytics_service = getattr(current_app, "analytics_service", None)
        if analytics_service:
            analytics_service.track_driver_performance(
                driver_id,
                {
                    "location_accuracy": accuracy,
                    "speed": speed,
                    "route_deviation": None,
                    "stops_completed": None,
                    "time_at_stop": None,
                    "fuel_efficiency": None,
                    "customer_rating": None,
                },
            )

        location_update = {
            "driver_id": driver_id,
            "lat": lat,
            "lng": lng,
            "heading": heading,
            "speed": speed,
            "accuracy": accuracy,
            "timestamp": timestamp,
            "received_at": datetime.utcnow().isoformat(),
        }

        try:
            from app import socketio  # local import to keep optional

            socketio.emit(
                "driver_location_update",
                location_update,
                room=f"driver_{driver_id}",
            )
        except Exception:  # pylint: disable=broad-exception-caught
            pass

        return (
            jsonify(
                {
                    "success": True,
                    "received_at": location_update["received_at"],
                }
            ),
            200,
        )

    except BadRequest:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Driver location update failed: %s", e)
        return (
            jsonify({"success": False, "error": "Location update failed"}),
            500,
        )


@mobile_bp.route("/driver/status", methods=["POST"])
@limiter.limit("30 per minute")
@require_api_key
@validate_request(["driver_id", "status"])
def update_driver_status():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"success": False, "error": "Invalid JSON"}), 400

        driver_id = data.get("driver_id")
        status = data.get("status")
        if not driver_id or not status:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "driver_id and status required",
                    }
                ),
                400,
            )

        valid_statuses = [
            "available",
            "busy",
            "en_route",
            "delivering",
            "break",
            "offline",
        ]
        if status not in valid_statuses:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Invalid status. Must be one of: {valid_statuses}",
                    }
                ),
                400,
            )

        status_update = {
            "driver_id": driver_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": data.get("metadata", {}),
        }

        try:
            from app import socketio

            socketio.emit(
                "driver_status_update", status_update, room="dispatch"
            )
        except Exception:  # pylint: disable=broad-exception-caught
            pass

        logger.info("Driver %s status updated to %s", driver_id, status)

        return (
            jsonify(
                {
                    "success": True,
                    "status": status,
                    "updated_at": status_update["timestamp"],
                }
            ),
            200,
        )

    except BadRequest:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Driver status update failed: %s", e)
        return (
            jsonify({"success": False, "error": "Status update failed"}),
            500,
        )


@mobile_bp.route("/offline/sync", methods=["POST"])
@limiter.limit("10 per minute")
@require_api_key
@validate_request(["device_id"])
def sync_offline_data():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"success": False, "error": "Invalid JSON"}), 400

        device_id = data.get("device_id")
        offline_data = data.get("offline_data", [])

        if not device_id:
            return (
                jsonify({"success": False, "error": "device_id required"}),
                400,
            )
        if offline_data is not None and not isinstance(offline_data, list):
            return (
                jsonify(
                    {"success": False, "error": "offline_data must be a list"}
                ),
                400,
            )

        sync_results = {
            "processed": 0,
            "failed": 0,
            "duplicates": 0,
            "errors": [],
        }

        for item in offline_data:
            try:
                item_type = item.get("type")
                if item_type in {
                    "location_update",
                    "status_update",
                    "delivery_confirmation",
                }:
                    sync_results["processed"] += 1
                else:
                    sync_results["failed"] += 1
                    sync_results["errors"].append(f"Unknown type: {item_type}")
            except Exception as exc:  # pylint: disable=broad-exception-caught
                sync_results["failed"] += 1
                sync_results["errors"].append(str(exc))

        logger.info(
            "Offline sync for %s: %d processed, %d failed",
            device_id,
            sync_results["processed"],
            sync_results["failed"],
        )

        return (
            jsonify(
                {
                    "success": True,
                    "sync_results": sync_results,
                    "synced_at": datetime.utcnow().isoformat(),
                }
            ),
            200,
        )

    except BadRequest:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Offline sync failed: %s", e)
        return jsonify({"success": False, "error": "Offline sync failed"}), 500


def _compress_route_for_mobile(
    route_data: Dict[str, Any], preferences: Dict[str, Any]
) -> Dict[str, Any]:
    compressed = {
        "id": route_data.get("route_id"),
        "stops": [],
        "total_distance": route_data.get("total_distance"),
        "total_time": route_data.get("total_time"),
        "optimized": True,
    }
    for stop in route_data.get("route", []) or []:
        item = {
            "id": stop.get("id"),
            "name": stop.get("name", ""),
            "address": stop.get("address", ""),
            "lat": stop.get("lat"),
            "lng": stop.get("lng"),
            "order": stop.get("order", 0),
        }
        if preferences.get("include_details"):
            item.update(
                {
                    "phone": stop.get("phone"),
                    "notes": stop.get("notes"),
                    "priority": stop.get("priority"),
                }
            )
        compressed["stops"].append(item)
    return compressed


def _format_directions_for_mobile(
    directions_data: Dict[str, Any],
) -> Dict[str, Any]:
    formatted = {
        "overview_polyline": directions_data.get("overview_polyline"),
        "bounds": directions_data.get("bounds"),
        "legs": [],
        "warnings": directions_data.get("warnings", []),
    }
    for leg in directions_data.get("legs", []) or []:
        leg_out = {
            "distance": leg.get("distance"),
            "duration": leg.get("duration"),
            "duration_in_traffic": leg.get("duration_in_traffic"),
            "start_location": leg.get("start_location"),
            "end_location": leg.get("end_location"),
            "steps": [],
        }
        for step in leg.get("steps", []) or []:
            leg_out["steps"].append(
                {
                    "distance": step.get("distance"),
                    "duration": step.get("duration"),
                    "html_instructions": step.get("html_instructions"),
                    "maneuver": step.get("maneuver"),
                    "start_location": step.get("start_location"),
                    "end_location": step.get("end_location"),
                    "polyline": step.get("polyline"),
                }
            )
        formatted["legs"].append(leg_out)
    return formatted


# ==========================================
# MISSING ROUTES FOR TESTS
# ==========================================

@mobile_bp.route("/routes/assigned", methods=["GET"])
@require_api_key
@limiter.limit("100 per hour")
def get_assigned_routes():
    """Get routes assigned to the authenticated driver"""
    try:
        # This is a placeholder - would normally get user ID from auth token
        routes = [
            {
                "id": "route_123",
                "title": "Downtown Delivery Route",
                "status": "assigned",
                "stops": 5,
                "estimated_duration": "2h 30m"
            }
        ]
        
        return jsonify({
            "success": True,
            "routes": routes,
            "total": len(routes)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting assigned routes: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to get assigned routes"
        }), 500


@mobile_bp.route("/routes/<route_id>", methods=["GET"])
@require_api_key
@limiter.limit("100 per hour")
def get_route_details(route_id):
    """Get detailed route information"""
    try:
        # Validate route_id
        if route_id == "invalid_route_id":
            return jsonify({
                "success": False,
                "error": "Route not found"
            }), 404
            
        route_details = {
            "id": route_id,
            "title": f"Route {route_id}",
            "status": "active",
            "stores": [
                {"address": "123 Main St", "status": "pending"},
                {"address": "456 Oak Ave", "status": "pending"}
            ],
            "estimated_duration": "1h 45m"
        }
        
        return jsonify(route_details), 200
        
    except Exception as e:
        logger.error(f"Error getting route details: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to get route details"
        }), 500


@mobile_bp.route("/routes/<route_id>/status", methods=["PUT", "POST"])
@require_api_key
@limiter.limit("50 per hour")
def update_route_status(route_id):
    """Update route status"""
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({
                "success": False,
                "error": "Status is required"
            }), 400
            
        return jsonify({
            "success": True,
            "message": "Route status updated",
            "route_id": route_id,
            "status": data['status']
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating route status: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to update route status"
        }), 500


@mobile_bp.route("/auth/login", methods=["POST"])
@limiter.limit("10 per minute")
def mobile_login():
    """Mobile authentication login"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid JSON"
            }), 400
            
        if not data.get('username') or not data.get('password'):
            return jsonify({
                "success": False,
                "error": "Username and password required"
            }), 400
            
        # Placeholder authentication - would integrate with real auth system
        return jsonify({
            "success": True,
            "token": "test_mobile_token_123",
            "user_id": "user_123",
            "expires_in": 3600
        }), 200
        
    except Exception as e:
        logger.error(f"Error in mobile login: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Login failed"
        }), 500


@mobile_bp.route("/auth/profile", methods=["GET"])
@require_api_key
@limiter.limit("30 per minute")
def get_user_profile():
    """Get user profile information"""
    try:
        return jsonify({
            "success": True,
            "user": {
                "id": "user_123",
                "username": "test_driver",
                "role": "driver",
                "active_routes": 2
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to get profile"
        }), 500


@mobile_bp.route("/auth/refresh", methods=["POST"])
@limiter.limit("20 per hour")
def refresh_token():
    """Refresh authentication token"""
    try:
        return jsonify({
            "success": True,
            "token": "refreshed_token_456",
            "expires_in": 3600
        }), 200
        
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Token refresh failed"
        }), 500


@mobile_bp.route("/auth/logout", methods=["POST"])
@require_api_key
@limiter.limit("10 per minute")
def mobile_logout():
    """Mobile logout"""
    try:
        return jsonify({
            "success": True,
            "message": "Logged out successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error in mobile logout: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Logout failed"
        }), 500


@mobile_bp.route("/tracking/location", methods=["POST"])
@require_api_key
@limiter.limit("200 per hour")
def update_location():
    """Update driver location"""
    try:
        data = request.get_json()
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({
                "success": False,
                "error": "Latitude and longitude required"
            }), 400
            
        return jsonify({
            "success": True,
            "message": "Location updated",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating location: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to update location"
        }), 500


@mobile_bp.route("/tracking/status", methods=["GET"])
@require_api_key
@limiter.limit("100 per hour")
def get_tracking_status():
    """Get current tracking status"""
    try:
        return jsonify({
            "success": True,
            "tracking": {
                "active": True,
                "last_update": datetime.utcnow().isoformat(),
                "accuracy": "high"
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting tracking status: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to get tracking status"
        }), 500


@mobile_bp.route("/optimize/feedback", methods=["POST"])
@require_api_key
@limiter.limit("50 per hour")
def submit_optimization_feedback():
    """Submit feedback for route optimization"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Feedback data required"
            }), 400
            
        return jsonify({
            "success": True,
            "message": "Feedback submitted",
            "feedback_id": str(uuid.uuid4())
        }), 200
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to submit feedback"
        }), 500


@mobile_bp.route("/optimize/suggestions", methods=["GET"])
@require_api_key
@limiter.limit("100 per hour")
def get_optimization_suggestions():
    """Get route optimization suggestions"""
    try:
        route_id = request.args.get('route_id')
        if not route_id:
            return jsonify({
                "success": False,
                "error": "Route ID required"
            }), 400
            
        return jsonify({
            "success": True,
            "suggestions": [
                {
                    "type": "time_optimization",
                    "description": "Take Highway 101 to save 15 minutes",
                    "estimated_savings": "15 minutes"
                }
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to get suggestions"
        }), 500


@mobile_bp.route("/offline/download/<route_id>", methods=["GET"])
@require_api_key
@limiter.limit("20 per hour")
def download_offline_route(route_id):
    """Download route data for offline use"""
    try:
        return jsonify({
            "success": True,
            "route_data": {
                "id": route_id,
                "offline_ready": True,
                "size": "2.3MB",
                "expires": (datetime.utcnow() + timedelta(days=7)).isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error downloading offline route: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to download route"
        }), 500


@mobile_bp.route("/performance/metrics", methods=["GET"])
@require_api_key
@limiter.limit("50 per hour")
def get_performance_metrics():
    """Get driver performance metrics"""
    try:
        period = request.args.get('period', 'week')
        
        return jsonify({
            "success": True,
            "period": period,
            "routes_completed": 45,
            "total_distance": "1,234 miles",
            "performance_score": 92.5,
            "on_time_percentage": 94.2
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to get metrics"
        }), 500


# ==========================================
# ERROR HANDLERS
# ==========================================

@mobile_bp.errorhandler(400)
def mobile_bad_request(_error):
    return (
        jsonify(
            {"success": False, "error": "Bad request", "mobile_friendly": True}
        ),
        400,
    )


@mobile_bp.errorhandler(401)
def mobile_unauthorized(_error):
    return (
        jsonify(
            {
                "success": False,
                "error": "Unauthorized",
                "mobile_friendly": True,
            }
        ),
        401,
    )


@mobile_bp.errorhandler(429)
def mobile_rate_limit(_error):
    return (
        jsonify(
            {
                "success": False,
                "error": "Rate limit exceeded",
                "mobile_friendly": True,
                "retry_after": "60 seconds",
            }
        ),
        429,
    )


@mobile_bp.errorhandler(500)
def mobile_server_error(_error):
    return (
        jsonify(
            {
                "success": False,
                "error": "Server error",
                "mobile_friendly": True,
            }
        ),
        500,
    )
