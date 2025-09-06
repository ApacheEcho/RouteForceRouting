# Gunicorn entrypoint for production
from app import create_app, socketio
import os

app = create_app(os.getenv("FLASK_ENV", "production"))

if __name__ == "__main__":
    # For local testing only; use Gunicorn in production
    # Default port: 5000 in dev, 8000 in production
    default_port = 8000 if os.getenv("FLASK_ENV", "production") == "production" else 5000
    socketio.run(app, host="0.0.0.0", port=int(os.getenv("PORT", default_port)), debug=False)
