"""
Celery application factory and Sentry integration for background workers.
Start worker with: celery -A app.celery_app celery worker --loglevel=info
"""
import os
from celery import Celery

# Celery expects a module path in -A. Expose a variable named `celery`.
celery = Celery(
    "routeforce",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
)

# Basic Celery config (can be expanded)
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=os.getenv("TZ", "UTC"),
    enable_utc=True,
)

# Optional: Autodiscover tasks from app.tasks package if present
try:
    celery.autodiscover_tasks(["app.tasks"])  # nosec - package path only
except Exception:
    pass

# Initialize Sentry for worker if DSN provided
try:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration

    dsn = os.getenv("SENTRY_DSN")
    if dsn:
        sentry_sdk.init(dsn=dsn, integrations=[CeleryIntegration()])
except Exception:
    # Sentry is optional; ignore if not configured
    pass
