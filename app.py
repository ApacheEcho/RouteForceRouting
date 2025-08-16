"""
RouteForce Routing Application
Modern Flask application with enterprise-grade architecture and real-time features
"""

import os
from app import create_app, socketio

# Create application instance
app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    # Development server with WebSocket support
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),  # Use port 5000 to match Docker
        debug=app.config.get("DEBUG", False),
        allow_unsafe_werkzeug=True,  # Allow Werkzeug in Docker/dev
    )
