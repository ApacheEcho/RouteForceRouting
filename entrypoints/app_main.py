"""
Deprecated dev entrypoint moved to avoid shadowing the `app/` package.

Use `run_app.py` for local dev and `wsgi:app` for Gunicorn.
"""

import os
from app import create_app, socketio  # type: ignore


def main() -> None:
    env = os.getenv("FLASK_ENV", "development")

    # Create application instance
    application = create_app(env)

    if env == "production":
        print("⚠️ Production mode: run via Gunicorn 'wsgi:app'")
        return

    # Development server with WebSocket support
    socketio.run(
        application,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        debug=(env == "development"),
        allow_unsafe_werkzeug=True,
    )


if __name__ == "__main__":
    main()
