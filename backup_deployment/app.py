"""
RouteForce Routing Application (Backup Deployment)
Standalone backup app for test and regression purposes.
"""

import os
from flask import Flask, request, jsonify, make_response
from flask_socketio import SocketIO
from functools import wraps
import datetime

# Create application instance
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return make_response(jsonify({"error": "Unauthorized"}), 401)
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def index():
    return "Backup Deployment App Running"

@app.route("/api/mobile/auth/login", methods=["POST"])
def mobile_auth_login():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400
    # Minimal validation
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Missing credentials"}), 400
    return jsonify({
        "success": True,
        "access_token": "test_token_123",
        "refresh_token": "refresh_token_abc",
        "expires_in": 3600,
        "driver_id": "driver_001"
    }), 200

@app.route("/api/mobile/auth/profile", methods=["GET"])
@require_auth
def mobile_auth_profile():
    return jsonify({
        "driver_id": "driver_001",
        "email": "test.driver@routeforce.com"
    }), 200

@app.route("/api/mobile/auth/refresh", methods=["POST"])
def mobile_auth_refresh():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400
    if not data or "refresh_token" not in data:
        return jsonify({"error": "Missing refresh_token"}), 400
    return jsonify({
        "success": True,
        "access_token": "test_token_456"
    }), 200

@app.route("/api/mobile/auth/logout", methods=["POST"])
@require_auth
def mobile_auth_logout():
    return jsonify({"success": True}), 200

@app.route("/api/mobile/routes/assigned", methods=["GET"])
@require_auth
def mobile_routes_assigned():
    return jsonify({
        "routes": [{"id": "route_123", "name": "Sample Route", "status": "assigned"}]
    }), 200

@app.route("/api/mobile/routes/<route_id>", methods=["GET"])
@require_auth
def mobile_route_detail(route_id):
    if route_id == "invalid_route_id":
        return jsonify({"error": "Route not found"}), 404
    return jsonify({
        "id": route_id,
        "stores": [],
        "status": "assigned"
    }), 200

@app.route("/api/mobile/routes/<route_id>/status", methods=["POST"])
@require_auth
def mobile_route_status(route_id):
    return jsonify({"success": True, "route_id": route_id}), 200

@app.route("/api/mobile/tracking/location", methods=["POST"])
@require_auth
def mobile_tracking_location():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400
    # Minimal validation
    if not data or not isinstance(data.get("lat"), (float, int)) or not isinstance(data.get("lng"), (float, int)):
        return jsonify({"error": "Invalid location data"}), 400
    if data.get("lat", 0) > 90 or data.get("lat", 0) < -90:
        return jsonify({"error": "Invalid latitude"}), 400
    if "timestamp" not in data or not isinstance(data["timestamp"], str):
        return jsonify({"error": "Invalid timestamp"}), 400
    return jsonify({"status": "ok", "message": "Location received (stub)"}), 200

@app.route("/api/mobile/tracking/status", methods=["GET"])
@require_auth
def mobile_tracking_status():
    return jsonify({
        "tracking_active": True,
        "last_update": datetime.datetime.now().isoformat()
    }), 200

@app.route("/api/mobile/optimize/feedback", methods=["POST"])
@require_auth
def mobile_optimize_feedback():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400
    # Minimal validation
    if not data or not data.get("route_id") or not (1 <= data.get("rating", 0) <= 5):
        return jsonify({"error": "Invalid feedback"}), 400
    return jsonify({"success": True}), 200

@app.route("/api/mobile/optimize/suggestions", methods=["GET"])
@require_auth
def mobile_optimize_suggestions():
    return jsonify({"suggestions": []}), 200

@app.route("/api/mobile/offline/download/<route_id>", methods=["GET"])
@require_auth
def mobile_offline_download(route_id):
    return jsonify({
        "route_data": {},
        "cache_timestamp": datetime.datetime.now().isoformat()
    }), 200

@app.route("/api/mobile/offline/sync", methods=["POST"])
@require_auth
def mobile_offline_sync():
    return jsonify({"success": True}), 200

@app.route("/api/mobile/performance/metrics", methods=["GET"])
@require_auth
def mobile_performance_metrics():
    return jsonify({
        "routes_completed": 5,
        "total_distance": 123.4,
        "performance_score": 98.7
    }), 200

@app.route("/api/mobile/health", methods=["GET"])
def mobile_health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "1.0.0"
    }), 200

if __name__ == "__main__":
    # Development server with WebSocket support
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        debug=True,
    )
