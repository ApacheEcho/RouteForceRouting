from .sentry_config import init_sentry
from flask import Flask

def create_app(env: str = "development") -> Flask:
    app = Flask(__name__)
    
    if env == "production":
        app.config.from_object("app.config.ProductionConfig")
    else:
        app.config.from_object("app.config.DevelopmentConfig")

    # Register sentry (optional)
    init_sentry()

    @app.route("/trigger-error")
    def trigger_error():
        1 / 0  # Raise an error to test Sentry

    # Add additional setup here if needed

    return app
