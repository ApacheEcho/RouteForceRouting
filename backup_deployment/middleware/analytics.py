"""
Analytics middleware for automatic tracking of API usage and performance
"""

import time
import logging
from flask import request, g
from typing import Optional
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)


class AnalyticsMiddleware:
    """
    Middleware to automatically track API usage and performance metrics
    """

    def __init__(self, analytics_service: AnalyticsService):
        self.analytics_service = analytics_service

    def before_request(self):
        """Track request start time"""
        g.start_time = time.time()
        g.analytics_data = {
            "endpoint": request.endpoint,
            "method": request.method,
            "user_agent": request.headers.get("User-Agent"),
            "ip_address": request.remote_addr,
            "path": request.path,
        }

    def after_request(self, response):
        """Track API usage after request completion"""
        try:
            if hasattr(g, "start_time") and hasattr(g, "analytics_data"):
                response_time = time.time() - g.start_time

                # Track API usage
                self.analytics_service.track_api_usage(
                    endpoint=g.analytics_data.get("endpoint")
                    or g.analytics_data.get("path"),
                    method=g.analytics_data["method"],
                    response_time=response_time,
                    status_code=response.status_code,
                    user_agent=g.analytics_data.get("user_agent"),
                )

                # Track system events for errors
                if response.status_code >= 400:
                    self.analytics_service.track_system_event(
                        event_type="api_error",
                        event_data={
                            "endpoint": g.analytics_data.get("endpoint"),
                            "status_code": response.status_code,
                            "method": g.analytics_data["method"],
                            "response_time": response_time,
                            "severity": (
                                "error"
                                if response.status_code >= 500
                                else "warning"
                            ),
                        },
                    )

                # Log slow requests
                if response_time > 2.0:  # 2 seconds threshold
                    logger.warning(
                        f"Slow API request: {g.analytics_data.get('endpoint')} took {response_time:.3f}s"
                    )
                    self.analytics_service.track_system_event(
                        event_type="slow_request",
                        event_data={
                            "endpoint": g.analytics_data.get("endpoint"),
                            "response_time": response_time,
                            "severity": "warning",
                        },
                    )

        except Exception as e:
            logger.error(f"Analytics middleware error: {e}")

        return response


def init_analytics_middleware(app, analytics_service: AnalyticsService):
    """Initialize analytics middleware with Flask app"""
    middleware = AnalyticsMiddleware(analytics_service)

    app.before_request(middleware.before_request)
    app.after_request(middleware.after_request)

    return middleware
