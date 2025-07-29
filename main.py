"""
RouteForce Routing Application
Modern Flask application with enterprise-grade architecture and real-time features.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from routeforcepro.app import create_app

# Initialize Sentry for error tracking and performance monitoring
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN", "https://<your-key>@o<org-id>.ingest.sentry.io/<project-id>"),
    integrations=[FlaskIntegration()],
    traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.2")),
    environment=os.getenv("FLASK_ENV", "production"),
)

def main() -> "Flask":
    """
    Main entry point for the application.
    Returns a Flask application instance.
    """
    env = os.getenv("FLASK_ENV", "development")
    app = create_app(env)
    return app

# Application instance for WSGI servers (e.g. Gunicorn, uWSGI)
app = main()

if __name__ == "__main__":
    # Sentry test: raise an exception and send to Sentry if env var is set
    if os.getenv("SENTRY_TEST", "0") == "1":
        raise Exception("This is a Sentry test!")  # Sentry test exception

    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    app.run(debug=debug, host=host, port=port)