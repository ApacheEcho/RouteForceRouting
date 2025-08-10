import os

from app import create_app, socketio

app = create_app(os.getenv("FLASK_ENV", "production"))

# For Gunicorn, we just need to expose the app object
# The if __name__ block below is only for local development/testing

if __name__ == "__main__":
    # For local development/testing only
    # In production, use gunicorn instead of this
    env = os.getenv("FLASK_ENV", "development")
    
    if env == "production":
        print("⚠️  Production mode detected: Use gunicorn instead of running wsgi.py directly")
        import sys
        sys.exit(0)
    
    # Development server only
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=app.config.get("DEBUG", False),
        allow_unsafe_werkzeug=True  # For local development only
    )
