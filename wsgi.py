import os

from app import create_app, socketio

app = create_app(os.getenv("FLASK_ENV", "production"))

if __name__ == "__main__":
    # For local development/testing
    socketio.run(
        app,
        host="0.0.0.0",
        # Default port: 5000 in dev, 8000 in production
        port=int(os.getenv("PORT", 8000 if app.config.get("ENV", "development") == "production" else 5000)),
        debug=app.config.get("DEBUG", False),
    )
