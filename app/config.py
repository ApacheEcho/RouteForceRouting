"""
Configuration management for RouteForce Routing
"""

import os
from typing import Any, Dict


class Config:
    """Base configuration class"""

    # Basic Flask configuration
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"

    # Database configuration
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or "sqlite:///routeforce.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # AUTO-PILOT: Enhanced database connection pooling configuration
    # Only apply pool settings for PostgreSQL/MySQL, not SQLite
    _db_uri = os.environ.get("DATABASE_URL") or "sqlite:///routeforce.db"
    if _db_uri.startswith("postgresql://") or _db_uri.startswith("mysql://"):
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_size": int(os.environ.get("DB_POOL_SIZE", "20")),
            "max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", "10")),
            "pool_timeout": int(os.environ.get("DB_POOL_TIMEOUT", "30")),
            "pool_recycle": int(os.environ.get("DB_POOL_RECYCLE", "3600")),  # 1 hour
            "pool_pre_ping": True,  # Validate connections before use
        }
    else:
        # SQLite configuration
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
        }

    # File upload configuration
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", "16777216"))  # 16MB
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")
    ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}

    # Cache configuration
    CACHE_TYPE = os.environ.get("CACHE_TYPE", "flask_caching.backends.simple")
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", "300"))

    # Rate limiting configuration
    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")
    RATE_LIMITS = os.environ.get("RATE_LIMITS", "200/day;50/hour")

    # Routing configuration
    MAX_ROUTE_OPTIMIZATION_TIME = int(
        os.environ.get("MAX_ROUTE_OPTIMIZATION_TIME", "300")
    )
    MAX_STORES_PER_ROUTE = int(os.environ.get("MAX_STORES_PER_ROUTE", "100"))

    # Logging configuration
    LOG_TO_STDOUT = os.environ.get("LOG_TO_STDOUT", "False").lower() == "true"
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_JSON = os.environ.get("LOG_JSON", "false").lower() == "true"
    REQUEST_ID_HEADER = os.environ.get("REQUEST_ID_HEADER", "X-Request-ID")
    JSONIFY_PRETTYPRINT_REGULAR = False

    # Google Maps API configuration
    GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
    GOOGLE_MAPS_API_QUOTA_LIMIT = int(
        os.environ.get("GOOGLE_MAPS_API_QUOTA_LIMIT", "1000")
    )
    GOOGLE_MAPS_CACHE_TTL = int(
        os.environ.get("GOOGLE_MAPS_CACHE_TTL", "3600")
    )  # 1 hour

    # Auto-commit service configuration
    AUTO_COMMIT_ENABLED = os.environ.get("AUTO_COMMIT_ENABLED", "true").lower() == "true"
    AUTO_COMMIT_INTERVAL_MINUTES = int(os.environ.get("AUTO_COMMIT_INTERVAL_MINUTES", "10"))
    AUTO_COMMIT_WIP_BRANCH = os.environ.get("AUTO_COMMIT_WIP_BRANCH", "auto-wip")

    @staticmethod
    def init_app(app) -> None:
        """Initialize app with configuration"""
        # Ensure upload directory exists
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    TESTING = False
    LOG_LEVEL = "DEBUG"
    CACHE_TYPE = "flask_caching.backends.simple"
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or "sqlite:///routeforce_dev.db"
    )
    SQLALCHEMY_ECHO = True
    SESSION_COOKIE_SAMESITE = "Lax"


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    TESTING = False
    LOG_LEVEL = "WARNING"

    # Production-specific settings
    CACHE_TYPE = "flask_caching.backends.redis"
    CACHE_REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
    RATELIMIT_STORAGE_URI = os.environ.get("REDIS_URL", "redis://localhost:6379")
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or "postgresql://localhost/routeforce_prod"
    )

    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    PREFERRED_URL_SCHEME = os.environ.get("PREFERRED_URL_SCHEME", "https")
    PROPAGATE_EXCEPTIONS = False

    @staticmethod
    def init_app(app) -> None:
        """Initialize production app"""
        Config.init_app(app)

        # Email errors to administrators
        import logging
        from logging.handlers import SMTPHandler

        if app.config.get("MAIL_SERVER"):
            mail_handler = SMTPHandler(
                mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
                fromaddr=app.config["MAIL_USERNAME"],
                toaddrs=app.config["ADMINS"],
                subject="RouteForce Routing Error",
                credentials=(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"]),
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    UPLOAD_FOLDER = "test_uploads"
    CACHE_TYPE = "flask_caching.backends.null"  # Disable cache for testing
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # In-memory database for testing


# Configuration dictionary
config: Dict[str, Any] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
