"""
RouteForce Routing Application
Modern Flask application with enterprise-grade architecture and real-time features
"""

import os
from app import create_app, socketio

# Create application instance
app = create_app(os.getenv("FLASK_ENV", "development"))

# Production-ready configuration
if os.getenv("FLASK_ENV") == "production":
    # Disable Werkzeug dev server warnings in production
    import werkzeug
    werkzeug.serving.is_running_from_reloader = lambda: False

if __name__ == "__main__":
    # For production, use gunicorn instead of this development server
    # For development/local testing only
    env = os.getenv("FLASK_ENV", "development")
    
    if env == "production":
        print("⚠️  Production mode detected: Use 'gunicorn app:app' instead of running directly")
        print("   For Render deployment, this is handled automatically by gunicorn_config.py")
    
    # Development server with WebSocket support
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        debug=(env == "development"),
        allow_unsafe_werkzeug=(env == "production")  # Allow production deployment
    )
