"""
Sentry Configuration and Integration Module
Comprehensive error tracking, performance monitoring, and alerting for RouteForce Routing
"""

import logging
import os

import sentry_sdk
from flask import Flask, g, request
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration


class SentryConfig:
    """Sentry configuration and setup"""

    def __init__(self):
        self.dsn = os.environ.get("SENTRY_DSN")
        self.environment = os.environ.get("FLASK_ENV", "development")
        self.release = os.environ.get("SENTRY_RELEASE", "1.0.0")
        self.traces_sample_rate = float(
            os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1")
        )
        self.profiles_sample_rate = float(
            os.environ.get("SENTRY_PROFILES_SAMPLE_RATE", "0.1")
        )

    def is_enabled(self):
        """Check if Sentry is enabled"""
        return bool(self.dsn and self.dsn != "your-sentry-dsn-here")


def init_sentry(app: Flask = None):
    """Initialize Sentry with comprehensive monitoring"""
    config = SentryConfig()

    if not config.is_enabled():
        logging.info("Sentry integration disabled - no DSN provided")
        return False

    try:
        # Configure logging integration
        logging_integration = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR,  # Send records as events
        )

        # Initialize Sentry SDK
        sentry_sdk.init(
            dsn=config.dsn,
            environment=config.environment,
            release=config.release,
            traces_sample_rate=config.traces_sample_rate,
            profiles_sample_rate=config.profiles_sample_rate,
            # Integrations for comprehensive monitoring
            integrations=[
                FlaskIntegration(transaction_style="endpoint", record_sql_params=True),
                SqlalchemyIntegration(),
                RedisIntegration(),
                CeleryIntegration(),
                logging_integration,
            ],
            # Performance monitoring
            enable_tracing=True,
            # Error filtering and processing
            before_send=before_send_filter,
            before_send_transaction=before_send_transaction_filter,
            # Additional configuration
            attach_stacktrace=True,
            send_default_pii=False,  # Privacy protection
            max_breadcrumbs=50,
            # Custom tags
            tags={"component": "routeforce-routing", "service": "api"},
        )

        # Set up Flask-specific configurations
        if app:
            setup_flask_integration(app)

        logging.info(
            f"Sentry initialized successfully for environment: {config.environment}"
        )
        return True

    except Exception as e:
        logging.error(f"Failed to initialize Sentry: {e}")
        return False


def setup_flask_integration(app: Flask):
    """Set up Flask-specific Sentry integration"""

    @app.before_request
    def before_request():
        """Set up request context for Sentry"""
        # Set user context if available
        user_id = getattr(g, "user_id", None) or request.headers.get("X-User-ID")
        if user_id:
            sentry_sdk.set_user({"id": user_id})

        # Set custom tags for the request
        sentry_sdk.set_tag("route", request.endpoint)
        sentry_sdk.set_tag("method", request.method)

        # Add custom context
        sentry_sdk.set_context(
            "request",
            {
                "url": request.url,
                "method": request.method,
                "headers": dict(request.headers),
                "user_agent": request.user_agent.string if request.user_agent else None,
            },
        )

    @app.after_request
    def after_request(response):
        """Add response information to Sentry context"""
        sentry_sdk.set_tag("status_code", response.status_code)
        sentry_sdk.set_context(
            "response",
            {
                "status_code": response.status_code,
                "content_length": response.content_length,
            },
        )
        return response

    # Custom error handlers for better Sentry integration
    @app.errorhandler(404)
    def handle_404(e):
        sentry_sdk.capture_message("Page not found", level="warning")
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def handle_500(e):
        sentry_sdk.capture_exception(e)
        return {"error": "Internal server error"}, 500


def before_send_filter(event, hint):
    """Filter events before sending to Sentry"""

    # Skip certain types of errors
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]

        # Skip common non-critical errors
        if exc_type.__name__ in ["ConnectionError", "Timeout", "KeyboardInterrupt"]:
            return None

        # Skip 404 errors in production
        if hasattr(exc_value, "code") and exc_value.code == 404:
            if os.environ.get("FLASK_ENV") == "production":
                return None

    # Add custom fingerprinting for better issue grouping
    if event.get("exception"):
        fingerprint = []
        for exception in event["exception"]["values"]:
            if exception.get("stacktrace"):
                # Use the last frame for fingerprinting
                last_frame = exception["stacktrace"]["frames"][-1]
                fingerprint.append(f"{last_frame['filename']}:{last_frame['function']}")

        if fingerprint:
            event["fingerprint"] = fingerprint

    return event


def before_send_transaction_filter(event, hint):
    """Filter performance transactions before sending to Sentry"""

    # Skip health check and static asset requests
    transaction_name = event.get("transaction", "")
    if any(
        skip in transaction_name.lower() for skip in ["health", "static", "favicon"]
    ):
        return None

    # Only sample slow transactions
    duration = event.get("contexts", {}).get("trace", {}).get("duration", 0)
    if duration < 0.1:  # Skip transactions faster than 100ms
        return None

    return event


# Custom Sentry utilities for the application
class SentryHelper:
    """Helper class for custom Sentry operations"""

    @staticmethod
    def capture_route_optimization_error(algorithm_type, location_count, error):
        """Capture route optimization specific errors"""
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("algorithm", algorithm_type)
            scope.set_tag("location_count", location_count)
            scope.set_context(
                "optimization",
                {
                    "algorithm_type": algorithm_type,
                    "location_count": location_count,
                    "error_type": type(error).__name__,
                },
            )
            sentry_sdk.capture_exception(error)

    @staticmethod
    def capture_performance_metrics(
        algorithm_type, execution_time, memory_usage, location_count
    ):
        """Capture performance metrics for route optimization"""
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("algorithm", algorithm_type)
            scope.set_tag("performance_type", "optimization")

            sentry_sdk.set_context(
                "performance",
                {
                    "algorithm_type": algorithm_type,
                    "execution_time_ms": execution_time * 1000,
                    "memory_usage_mb": memory_usage,
                    "location_count": location_count,
                    "efficiency_score": (
                        location_count / execution_time if execution_time > 0 else 0
                    ),
                },
            )

            # Create custom metric
            sentry_sdk.capture_message(
                f"Route optimization completed: {algorithm_type}", level="info"
            )

    @staticmethod
    def capture_api_usage(endpoint, response_time, status_code, user_id=None):
        """Capture API usage metrics"""
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("api_endpoint", endpoint)
            scope.set_tag("api_status", status_code)

            if user_id:
                scope.set_user({"id": user_id})

            scope.set_context(
                "api_usage",
                {
                    "endpoint": endpoint,
                    "response_time_ms": response_time * 1000,
                    "status_code": status_code,
                    "timestamp": sentry_sdk.utils.utc_from_timestamp(
                        sentry_sdk.utils.now()
                    ).isoformat(),
                },
            )

            # Capture slow API calls as issues
            if response_time > 5.0:  # Slower than 5 seconds
                sentry_sdk.capture_message(
                    f"Slow API response: {endpoint} took {response_time:.2f}s",
                    level="warning",
                )

    @staticmethod
    def capture_database_error(operation, table, error, query=None):
        """Capture database-specific errors with context"""
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("db_operation", operation)
            scope.set_tag("db_table", table)

            context = {
                "operation": operation,
                "table": table,
                "error_type": type(error).__name__,
            }

            if query:
                context["query"] = query[:500]  # Limit query length

            scope.set_context("database", context)
            sentry_sdk.capture_exception(error)

    @staticmethod
    def start_transaction(name, op="http.server"):
        """Start a custom Sentry transaction"""
        return sentry_sdk.start_transaction(name=name, op=op)

    @staticmethod
    def add_breadcrumb(message, category="custom", level="info", data=None):
        """Add custom breadcrumb for debugging"""
        sentry_sdk.add_breadcrumb(
            message=message, category=category, level=level, data=data or {}
        )


# Decorator for monitoring function performance
def monitor_performance(algorithm_type=None):
    """Decorator to monitor function performance with Sentry"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            import tracemalloc

            # Start monitoring
            start_time = time.time()
            tracemalloc.start()

            try:
                with SentryHelper.start_transaction(
                    name=f"{func.__module__}.{func.__name__}", op="function.call"
                ):
                    result = func(*args, **kwargs)

                # Capture performance metrics
                end_time = time.time()
                execution_time = end_time - start_time
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()

                # Log performance if slow
                if execution_time > 1.0:  # Functions taking longer than 1 second
                    SentryHelper.capture_performance_metrics(
                        algorithm_type or func.__name__,
                        execution_time,
                        peak / 1024 / 1024,  # Convert to MB
                        len(args) + len(kwargs),
                    )

                return result

            except Exception as e:
                tracemalloc.stop()

                # Capture the error with context
                if algorithm_type:
                    SentryHelper.capture_route_optimization_error(
                        algorithm_type, len(args) + len(kwargs), e
                    )
                else:
                    sentry_sdk.capture_exception(e)

                raise

        return wrapper

    return decorator


# Context manager for Sentry scopes
class SentryContext:
    """Context manager for Sentry scope management"""

    def __init__(self, operation_name, **tags):
        self.operation_name = operation_name
        self.tags = tags
        self.scope = None
        self.transaction = None

    def __enter__(self):
        self.scope = sentry_sdk.push_scope()
        self.scope.__enter__()

        # Set tags
        for key, value in self.tags.items():
            self.scope.set_tag(key, value)

        # Start transaction
        self.transaction = sentry_sdk.start_transaction(
            name=self.operation_name, op="custom.operation"
        )
        self.transaction.__enter__()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.transaction:
            self.transaction.__exit__(exc_type, exc_val, exc_tb)

        if self.scope:
            self.scope.__exit__(exc_type, exc_val, exc_tb)

    def set_context(self, key, data):
        """Set context data in the current scope"""
        if self.scope:
            self.scope.set_context(key, data)

    def add_breadcrumb(self, message, **kwargs):
        """Add breadcrumb in the current scope"""
        sentry_sdk.add_breadcrumb(message=message, **kwargs)
