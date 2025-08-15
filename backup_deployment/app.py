"""
RouteForce Routing Application (Backup Deployment)
Standalone backup app for test and regression purposes.
"""

import os
from flask import Flask, request, jsonify
from flask_socketio import SocketIO

# Create application instance
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

@app.route("/")
def index():
    return "Backup Deployment App Running"

@app.route("/api/mobile/tracking/location", methods=["POST"])
def mobile_tracking_location():
    # Stub: Accepts location data from mobile client
    return jsonify({"status": "ok", "message": "Location received (stub)"}), 200

@app.route("/api/mobile/offline/download/<route_id>", methods=["GET"])
def mobile_offline_download(route_id):
    # Stub: Returns offline route data for given route_id
    return jsonify({"status": "ok", "route_id": route_id, "data": []}), 200

@app.route("/api/mobile/auth/login", methods=["POST"])
def mobile_auth_login():
    # Stub: Accepts login credentials and returns a fake token
    return jsonify({"status": "ok", "token": "stub-token"}), 200

if __name__ == "__main__":
    # Development server with WebSocket support
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        debug=True,
    )
