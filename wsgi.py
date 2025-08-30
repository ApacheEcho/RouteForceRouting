import os

# Load environment variables from local files if present
try:
    from dotenv import load_dotenv  # type: ignore
    # Base .env for local usage
    load_dotenv(dotenv_path=".env", override=False)
    # Production-specific overrides if running in production
    if os.getenv("FLASK_ENV", "production").lower() == "production":
        # Load .env.production if present (does not exist on Render by default)
        load_dotenv(dotenv_path=".env.production", override=True)
        # Also support a render-specific env file if used locally
        load_dotenv(dotenv_path=".env.render", override=False)
except Exception:
    # dotenv is optional; ignore if not installed or any error occurs
    pass

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
