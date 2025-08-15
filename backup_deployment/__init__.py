"""
RouteForce Routing Application Factory
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
import logging
import warnings
import time
import psutil
from datetime import datetime

# Initialize extensions
cache = Cache()
limiter = Limiter(
    key_func=get_remote_address, default_limits=["200 per day", "50 per hour"]
)
socketio = SocketIO(
    cors_allowed_origins="*", logger=True, engineio_logger=True
)


def create_app(config_name: str = "development") -> Flask:
    """
    Application factory pattern for creating Flask app instances

    Args:
        config_name: Configuration environment name

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    from app.config import config

    app.config.from_object(config[config_name])

    # Initialize database
    from app.models.database import db, migrate

    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize extensions
    CORS(
        app,
        origins=[
            "http://localhost:3000",  # Local React development
            "https://app.routeforcepro.com",  # Production frontend
            "https://routeforcepro.netlify.app",  # Netlify deployment
        ],
    )
    cache.init_app(app)

    # Initialize JWT authentication
    from app.auth_system import init_jwt

    init_jwt(app)

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
                from sqlalchemy import text

                db.session.execute(text("SELECT 1"))
                db.session.commit()
            except Exception as e:
                db_status = f"unhealthy: {str(e)}"

            # Check cache connectivity
            cache_status = "healthy"
            try:
                cache.set("health_check", "ok", timeout=5)
                cache.get("health_check")
            except Exception as e:
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
                    "timestamp": datetime.utcnow().isoformat(),
                    "version": "1.0.0",
                    "services": {"database": db_status, "cache": cache_status},
                    "system": system_metrics,
                }
            ), (200 if status == "healthy" else 503)

        except Exception as e:
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

        except Exception as e:
            return (
                f"# Error generating metrics: {str(e)}",
                503,
                {"Content-Type": "text/plain; charset=utf-8"},
            )

    # Initialize WebSocket support
    socketio.init_app(
        app, cors_allowed_origins="*", logger=True, engineio_logger=True
    )

    # Initialize WebSocket handlers
    from app.websocket_handlers import init_websocket

    init_websocket(app, socketio)

    # Initialize analytics service and middleware
    from app.services.analytics_service import AnalyticsService
    from app.middleware.analytics import init_analytics_middleware

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

    # Initialize and start advanced performance monitoring
    from app.performance_monitor import get_performance_monitor

    # from app.performance.optimization_engine import PerformanceOptimizationEngine

    # Start legacy performance monitor
    monitor = get_performance_monitor()
    monitor.start_monitoring()
    logging.info("Performance monitoring started")

    # Initialize and start advanced optimization engine
    # optimization_engine = PerformanceOptimizationEngine()
    # optimization_engine.start_monitoring()
    # app.optimization_engine = optimization_engine
    # logging.info("Advanced performance optimization engine started")

    # Initialize optimized database connection pool
    from app.database.optimized_connection_pool import DatabaseConnectionPool

    db_pool = DatabaseConnectionPool(app.config.get("SQLALCHEMY_DATABASE_URI"))
    app.db_pool = db_pool
    logging.info("Optimized database connection pool initialized")

    return app


def configure_logging(app: Flask) -> None:
    """Configure application logging"""
    # Suppress specific warnings for production readiness
    if not app.debug:
        warnings.filterwarnings("ignore", message="Flask-Caching.*deprecated")
        warnings.filterwarnings(
            "ignore", message="Using the in-memory storage.*not recommended"
        )

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]",
        )
    else:
        logging.basicConfig(level=logging.DEBUG)


def register_blueprints(app: Flask) -> None:
    """Register application blueprints"""
    from app.routes.main_enhanced import main_bp  # Use enhanced main blueprint
    from app.routes.api import api_bp
    from app.auth_system import auth_bp  # Use JWT-based auth system
    from app.routes.dashboard import dashboard_bp
    from app.routes.enhanced_dashboard import enhanced_dashboard_bp
    from app.routes.enterprise_dashboard import enterprise_bp
    from app.api.traffic import traffic_bp
    from app.api.mobile import mobile_bp
    from app.api.analytics import analytics_bp
    from app.analytics_api import analytics_bp as analytics_ai_bp
    from app.monitoring_api import monitoring_bp
    from app.advanced_dashboard_api import advanced_dashboard_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(enhanced_dashboard_bp)
    app.register_blueprint(enterprise_bp)
    app.register_blueprint(traffic_bp, url_prefix="/api/traffic")
    app.register_blueprint(mobile_bp, url_prefix="/api/mobile")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(analytics_ai_bp, url_prefix="/api/ai")
    app.register_blueprint(monitoring_bp)
    app.register_blueprint(
        advanced_dashboard_bp
    )  # Register advanced dashboard

    # Register enterprise blueprints
    from app.enterprise.organizations import organizations_bp
    from app.enterprise.users import users_bp

    app.register_blueprint(organizations_bp)
    app.register_blueprint(users_bp)


def register_error_handlers(app: Flask) -> None:
    """Register application error handlers"""
    from app.routes.errors import errors_bp

    app.register_blueprint(errors_bp)
