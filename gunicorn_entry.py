# Gunicorn entrypoint for production
from app import create_app, socketio
import os

app = create_app(os.getenv("FLASK_ENV", "production"))

if __name__ == "__main__":
    # For local testing only; use Gunicorn in production
    socketio.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)
