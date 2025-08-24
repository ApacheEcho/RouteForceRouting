"""
RouteForce Routing Application
Modern Flask application with enterprise-grade architecture and real-time features
"""

import os
from app import create_app, socketio
from flask import send_file

# Create application instance
app = create_app(os.getenv("FLASK_ENV", "development"))

# Serve openapi.json at /openapi.json if it exists
def _openapi_json_route():
    if os.path.exists("openapi.json"):
        return send_file("openapi.json", mimetype="application/json")
    return ("OpenAPI spec not found", 404)
app.add_url_rule("/openapi.json", "openapi_json", _openapi_json_route)

if __name__ == "__main__":
    # Development server with WebSocket support
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),  # Use port 5000 to match Docker
        debug=app.config.get("DEBUG", False),
        allow_unsafe_werkzeug=True,  # Allow Werkzeug in Docker/dev
    )
