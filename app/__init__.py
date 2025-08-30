"""
RouteForce Routing Application Factory
"""

import logging
import time
import warnings
from datetime import datetime
import os
import uuid
import psutil
from flask import Flask, jsonify, request, abort, g
from flask_cors import CORS
from flask_socketio import SocketIO
from flasgger import Swagger
from werkzeug.middleware.proxy_fix import ProxyFix
from app.config import config
from app.models.database import db, migrate
from app.auth_system import init_jwt
from app.monitoring import setup_monitoring
from sqlalchemy import text
from app.websocket_handlers import init_websocket
from app.middleware.analytics import init_analytics_middleware
from app.services.analytics_service import AnalyticsService
from app.performance.beast_mode_integration import init_beast_mode
from app.services.auto_commit_service import start_auto_commit_service
from app.performance_monitor import get_performance_monitor
from app.advanced_dashboard_api import advanced_dashboard_bp
from app.analytics_api import analytics_bp as analytics_ai_bp
from app.api.analytics import analytics_bp
from app.routes.analytics import analytics_bp as analytics_routes_bp
from app.routes.user_activity import activity_bp as analytics_activity_bp
from app.api.mobile import mobile_bp
from app.api.traffic import traffic_bp
from app.api.voice import voice_bp
from app.auth_system import auth_bp
from app.monitoring_api import monitoring_bp
from app.routes.api import api_bp
from app.routes.dashboard import dashboard_bp
from app.routes.docs import docs_bp
from app.routes.enhanced_dashboard import enhanced_dashboard_bp
from app.routes.enterprise_dashboard import enterprise_bp
from app.routes.main_enhanced import main_bp
from app.routes.metrics import metrics_bp
from app.routes.scoring import scoring_bp
from app.routes.voice_dashboard import voice_dashboard_bp
from app.enterprise.organizations import organizations_bp
from app.enterprise.users import users_bp
from app.claude_api import claude_bp
from app.extensions import cache, limiter
from app.api.iot import iot_api
from app.routes.errors import errors_bp


# Initialize extensions
socketio = SocketIO(
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True,
    async_mode="threading",
)
swagger = Swagger()


def create_app(config_name: str = "development", testing: bool = False) -> Flask:
    """
    Application factory pattern for creating Flask app instances

    Args:
        config_name: Configuration environment name
        testing: If True, use the 'testing' config

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)

    # Auto-detect pytest and prefer testing config to avoid external services
    if not testing and os.getenv("PYTEST_CURRENT_TEST"):
        testing = True
        config_name = "testing"

    # Load configuration
    if testing:
        app.config.from_object(config["testing"])
    else:
        app.config.from_object(config[config_name])

    # Configure logging early
    try:
        configure_logging(app)
    except Exception:
        # Logging setup should not break app initialization
        pass

    # Enforce HTTPS in production
    if app.config.get("PREFERRED_URL_SCHEME", "http") == "https":
        @app.before_request
        def enforce_https():
            if not request.is_secure and not app.config.get("DEBUG", False):
                return (
                    jsonify({
                        "error": "HTTPS is required. Please use https:// for all requests."
                    }),
                    403,
                )

    # Respect X-Forwarded-* headers from upstream proxy (Nginx/Render)
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1
    )

    # (Avoid reloading config here; already applied above)

    # Initialize database
    db.init_app(app)
    migrate.init_app(app, db)

    # Request ID correlation
    @app.before_request
    def _assign_request_id():
        g.request_id = request.headers.get(
            app.config.get("REQUEST_ID_HEADER", "X-Request-ID")
        ) or str(uuid.uuid4())

    @app.after_request
    def _add_request_id(resp):
        header_name = app.config.get("REQUEST_ID_HEADER", "X-Request-ID")
        resp.headers.setdefault(header_name, getattr(g, "request_id", ""))
        return resp

    # Minimal API request validation for JSON endpoints
    @app.before_request
    def _validate_request():
        # Only apply to API routes, but skip /api/mobile/auth/logout for
        # legacy/mobile compatibility
        if request.path.startswith("/api") and request.method in {
            "POST",
            "PUT",
            "PATCH",
        }:
            # Exempt endpoints that legitimately have no body
            exempt_paths = {
                "/api/mobile/auth/logout",
                "/api/v1/refresh",
                "/api/v1/logout",
            }
            if request.path in exempt_paths:
                return  # Allow any content-type or no body
            if not request.is_json:
                abort(415, description="Content-Type must be application/json")
            # Attempt to parse JSON early to return a clear error
            try:
                _ = request.get_json(silent=False)
            except Exception:
                abort(400, description="Invalid JSON payload")

    # Hardened CORS configuration: in production, require CORS_ORIGINS env var
    cors_env = os.getenv("CORS_ORIGINS", "")
    if app.config.get("ENV", "development") == "production":
        if not cors_env:
            raise RuntimeError("CORS_ORIGINS environment variable must be set in production!")
        cors_origins = [o.strip() for o in cors_env.split(",") if o.strip()]
    else:
        cors_origins = [
            o.strip()
            for o in (
                cors_env.split(",")
                if cors_env
                else [
                    "http://localhost:3000",
                    "https://app.routeforcepro.com",
                    "https://routeforcepro.netlify.app",
                ]
            )
            if o.strip()
        ]
    # Document: set CORS_ORIGINS env var to a comma-separated list of allowed origins
    CORS(
        app,
        origins=cors_origins,
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        max_age=86400,
    )
    cache.init_app(app)

    # Initialize API documentation with Swagger
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "RouteForce Routing API",
            "description": (
                "API documentation for RouteForce Routing application - "
                "A comprehensive route optimization platform for field "
                "execution teams"
            ),
            "version": "1.0.0",
            "contact": {
                "name": "RouteForce Support",
                "url": "https://github.com/ApacheEcho/RouteForceRouting",
            },
        },
        "host": "localhost:8000",
        "basePath": "/",
        "schemes": ["http", "https"],
        "tags": [
            {
                "name": "Analytics",
                "description": "Analytics and monitoring endpoints",
            },
            {"name": "Mobile", "description": "Mobile app specific endpoints"},
            {
                "name": "Routes",
                "description": "Route optimization and management",
            },
            {"name": "Traffic", "description": "Traffic data and routing"},
        ],
        "securityDefinitions": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
            }
        },
    }

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/api/swagger.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs",
    }

    Swagger(app, config=swagger_config, template=swagger_template)

    # Initialize JWT authentication
    init_jwt(app)

    # Initialize Sentry monitoring
    setup_monitoring(app)

    # Security headers
    @app.after_request
    def set_security_headers(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "no-referrer")
        resp.headers.setdefault("X-XSS-Protection", "0")
        # Enable HSTS only when serving over HTTPS
        if app.config.get("PREFERRED_URL_SCHEME", "http") == "https":
            resp.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )
        return resp

    # Register health check endpoint (for production monitoring)
    @app.route("/health")
    def health_check():
        """
        Health check endpoint for load balancers and monitoring systems
        """
        try:
            # Check database connectivity
            db_status = "healthy"
            try:
                db.session.execute(text("SELECT 1"))
                db.session.commit()
            except Exception as e:  # noqa: BLE001
                # DB connection errors can be many types
                # (SQLAlchemy, connection, etc.)
                db_status = f"unhealthy: {str(e)}"

            # Check cache connectivity
            cache_status = "healthy"
            try:
                cache.set("health_check", "ok", timeout=5)
                cache.get("health_check")
            except Exception as e:  # noqa: BLE001
                # Cache errors can be many types (redis, memcached, etc.)
                # Third-party cache libraries may raise many exception types
                cache_status = f"unhealthy: {str(e)}"

            # System metrics
            system_metrics = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage("/").percent,
            }

            status = (
                "healthy"
                if db_status == "healthy" and cache_status == "healthy"
                else "degraded"
            )

            return jsonify(
                {
                    "status": status,
                    "service": "RouteForce Routing",
                    "timestamp": datetime.utcnow().isoformat(),
                    "version": "1.0.0",
                    "services": {"database": db_status, "cache": cache_status},
                    "system": system_metrics,
                }
            ), (200 if status == "healthy" else 503)

        except Exception as e:  # noqa: BLE001
            # This is a last-resort catch for health endpoint
            return (
                jsonify(
                    {
                        "status": "unhealthy",
                        "timestamp": datetime.utcnow().isoformat(),
                        "error": str(e),
                    }
                ),
                503,
            )

    # Register metrics endpoint for Prometheus
    @app.route("/metrics")
    def metrics():
        """
        Prometheus metrics endpoint
        """
        try:
            # Basic system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Application metrics
            app_metrics = []
            app_metrics.append(
                "# HELP routeforce_cpu_usage CPU usage percentage"
            )
            app_metrics.append("# TYPE routeforce_cpu_usage gauge")
            app_metrics.append(f"routeforce_cpu_usage {cpu_percent}")

            app_metrics.append(
                "# HELP routeforce_memory_usage Memory usage percentage"
            )
            app_metrics.append("# TYPE routeforce_memory_usage gauge")
            app_metrics.append(f"routeforce_memory_usage {memory.percent}")

            app_metrics.append(
                "# HELP routeforce_disk_usage Disk usage percentage"
            )
            app_metrics.append("# TYPE routeforce_disk_usage gauge")
            app_metrics.append(f"routeforce_disk_usage {disk.percent}")

            app_metrics.append(
                "# HELP routeforce_uptime Application uptime in seconds"
            )
            app_metrics.append("# TYPE routeforce_uptime counter")
            app_metrics.append(
                f"routeforce_uptime {time.time() - psutil.boot_time()}"
            )

            return (
                "\n".join(app_metrics),
                200,
                {"Content-Type": "text/plain; charset=utf-8"},
            )

        except Exception as e:  # noqa: BLE001
            # Metrics endpoint must not crash the app
            return (
                f"# Error generating metrics: {str(e)}",
                503,
                {"Content-Type": "text/plain; charset=utf-8"},
            )

    # Initialize WebSocket support
    socketio.init_app(
        app,
        cors_allowed_origins=cors_origins,
        logger=True,
        engineio_logger=True,
        async_mode="threading",
    )

    # Initialize WebSocket handlers
    init_websocket(app, socketio)

    # Initialize analytics service and middleware
    analytics_service = AnalyticsService()
    init_analytics_middleware(app, analytics_service)

    # Store analytics service in app context for global access
    app.analytics_service = analytics_service

    # Configure limiter with storage URI
    if app.config.get("RATELIMIT_STORAGE_URI"):
        limiter.storage_uri = app.config["RATELIMIT_STORAGE_URI"]
    limiter.init_app(app)

    # Configure logging
    configure_logging(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Initialize Beast Mode Performance Optimizations
    # Get Redis client for optimizations
    redis_client = None
    try:
        import redis

        redis_url = app.config.get("REDIS_URL", "redis://localhost:6379/0")
        redis_client = redis.from_url(redis_url, decode_responses=False)
        redis_client.ping()  # Test connection
    except ImportError:
        logging.warning("Redis package not installed")
    except Exception as e:  # noqa: BLE001
        # Redis client can raise many exception types
        # (connection, config, etc.)
        logging.warning("Redis not available for optimizations: %s", e)

    # Initialize all Beast Mode optimizations (skip during tests)
    if not app.config.get("TESTING", False):
        beast_mode_results = init_beast_mode(app, socketio, redis_client)
        app.beast_mode_results = beast_mode_results
        logging.info(
            "🚀 Beast Mode Status: %s",
            beast_mode_results.get("beast_mode_status", "UNKNOWN"),
        )

    # Initialize legacy performance monitor as backup (skip during tests)
    if not app.config.get("TESTING", False):
        try:
            monitor = get_performance_monitor()
            monitor.start_monitoring()
            logging.info("Legacy performance monitoring started as backup")
        except Exception as e:  # noqa: BLE001
            # Performance monitor can fail for many reasons
            # (threading, config, etc.)
            logging.warning("Legacy performance monitor not available: %s", e)

    # Initialize auto-commit service for background code backup (skip during tests)
    if not app.config.get("TESTING", False) and app.config.get("AUTO_COMMIT_ENABLED", True):
        start_auto_commit_service()
        logging.info("Auto-commit background service started")

    return app


def configure_logging(app: Flask) -> None:
    """
    Configure application logging with optional JSON output and
    request correlation
    """
    # Suppress specific warnings for production readiness
    if not app.debug:
        warnings.filterwarnings("ignore", message="Flask-Caching.*deprecated")
        warnings.filterwarnings(
            "ignore", message="Using the in-memory storage.*not recommended"
        )

    log_level = getattr(
        logging,
        str(app.config.get("LOG_LEVEL", "INFO")).upper(),
        logging.INFO,
    )
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(log_level)

    handler = logging.StreamHandler()

    if app.config.get("LOG_JSON", False):
        try:
            from pythonjsonlogger import jsonlogger

            fmt = jsonlogger.JsonFormatter(
                fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
                rename_fields={"levelname": "level"},
            )
            handler.setFormatter(fmt)
        except ImportError:
            # JSON logger not installed
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s: %(message)s "
                    "[in %(pathname)s:%(lineno)d]"
                )
            )
        except Exception:
            # Fallback to plain format if json logger fails for any reason
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s: %(message)s "
                    "[in %(pathname)s:%(lineno)d]"
                )
            )
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s "
                "[in %(pathname)s:%(lineno)d]"
            )
        )

    root_logger.addHandler(handler)

    # Access log for requests
    @app.after_request
    def _access_log(resp):
        try:
            logging.getLogger("access").info(
                {
                    "method": request.method,
                    "path": request.path,
                    "status": resp.status_code,
                    "remote_addr": request.headers.get(
                        "X-Forwarded-For", request.remote_addr
                    ),
                    "request_id": getattr(g, "request_id", None),
                }
                if app.config.get("LOG_JSON", False)
                else (
                    "%s %s -> %s rid=%s"
                    % (
                        request.method,
                        request.path,
                        resp.status_code,
                        getattr(g, "request_id", None),
                    )
                )
            )
        except Exception:  # noqa: BLE001
            # Access log should never break the response
            pass
        return resp


def register_blueprints(app: Flask) -> None:
    """Register application blueprints"""
    app.register_blueprint(main_bp)
    # Register api_bp at root so /api/v1/* endpoints are accessible as /api/v1/*
    app.register_blueprint(api_bp)
    app.register_blueprint(scoring_bp, url_prefix="/api/route")
    app.register_blueprint(metrics_bp)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(enhanced_dashboard_bp)
    app.register_blueprint(enterprise_bp)
    app.register_blueprint(voice_dashboard_bp)  # Voice dashboard
    app.register_blueprint(traffic_bp, url_prefix="/api/traffic")
    app.register_blueprint(mobile_bp, url_prefix="/api/mobile")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    # Register additional analytics route blueprints (already include full paths)
    app.register_blueprint(analytics_routes_bp)
    app.register_blueprint(analytics_activity_bp)
    app.register_blueprint(analytics_ai_bp, url_prefix="/api/ai")
    app.register_blueprint(claude_bp)  # Claude Opus 4.1 AI endpoints
    app.register_blueprint(
        voice_bp, url_prefix="/api/voice"
    )  # Voice-to-code API
    app.register_blueprint(monitoring_bp)
    app.register_blueprint(
        advanced_dashboard_bp
    )  # Register advanced dashboard

    # Register enterprise blueprints
    app.register_blueprint(organizations_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(iot_api, url_prefix="/api/iot")  # Register IoT API


def register_error_handlers(app):
    """Register error handlers"""
    app.register_blueprint(errors_bp)
