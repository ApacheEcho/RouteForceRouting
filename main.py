"""
RouteForce Routing Application
Modern Flask application with enterprise-grade architecture and real-time features
"""

import os

from app import app as application
from app import create_app, socketio

# Create application instance
app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    # For Render deployment
    application.run(host="0.0.0.0", port=10000)

    # Uncomment the lines below for local development with WebSocket support
    # socketio.run(
    #     app,
    #     host="0.0.0.0",
    #     port=int(os.getenv("PORT", 8000)),
    #     debug=app.config.get("DEBUG", False),
    # )
