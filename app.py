"""
RouteForce Routing Application
Modern Flask application with enterprise-grade architecture and real-time features
"""

import os
from app import create_app, socketio
from flask import send_file
from flask import send_from_directory, request

# Create application instance
app = create_app(os.getenv("FLASK_ENV", "development"))

# Serve openapi.json at /openapi.json mirroring Flasgger JSON (fallback to file)
def _openapi_json_route():
    try:
        # Prefer the live Flasgger spec to avoid drift
        return app.view_functions["apispec_1"]()
    except Exception:
        root = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(root, "openapi.json")
        if os.path.exists(path):
            return send_file(path, mimetype="application/json")
        # Also check project root one level up if running from app subdir
        parent_path = os.path.join(os.path.dirname(root), "openapi.json")
        if os.path.exists(parent_path):
            return send_file(parent_path, mimetype="application/json")
        return ("OpenAPI spec not found", 404)
app.add_url_rule("/openapi.json", "openapi_json", _openapi_json_route)

# Serve static files from frontend/dist
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join('frontend', 'dist', 'static'), filename)

# SPA fallback: route all non-API, non-static requests to index.html
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path.startswith('api') or path.startswith('openapi.json') or path.startswith('static'):
        return ("Not Found", 404)
    return send_from_directory(os.path.join('frontend', 'dist'), 'index.html')

if __name__ == "__main__":
    # Development server with WebSocket support
    socketio.run(
        app,
        host="0.0.0.0",
        # Default port: 5000 in dev, 8000 in production
        port=int(os.getenv("PORT", 8000 if app.config.get("ENV", "development") == "production" else 5000)),
        debug=app.config.get("DEBUG", False),
        allow_unsafe_werkzeug=True,  # Allow Werkzeug in Docker/dev
    )
