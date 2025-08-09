"""
RouteForce Routing Application
Modern Flask application with enterprise-grade architecture and real-time features
"""

import os
from app import create_app, socketio

# Create application instance
app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    # Check if we're in production (Render sets this)
    is_production = os.getenv("RENDER") or os.getenv("FLASK_ENV") == "production"
    
    if is_production:
        # Production: Let Gunicorn handle the app
        # This should not be reached when using Gunicorn, but prevents Werkzeug errors
        print("Production mode: Use 'gunicorn app:app' to start the server")
    else:
        # Development server with WebSocket support
        socketio.run(
            app,
            host="0.0.0.0",
            port=int(os.getenv("PORT", 8000)),
            debug=app.config.get("DEBUG", False),
        )
