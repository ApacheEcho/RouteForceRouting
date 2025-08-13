"""
Celery application and Sentry integration for background workers.
Start worker with: celery -A app.celery_app worker --loglevel=info
"""
import os
from celery import Celery

# Create Celery instance
celery = Celery(
    "routeforce",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
)

# Base configuration
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=os.getenv("TZ", "UTC"),
    enable_utc=True,
)

# Auto-discover tasks from app.tasks if present
try:
    celery.autodiscover_tasks(["app.tasks"])  # nosec - module path only
except Exception:
    pass

# Initialize Sentry for worker if DSN is provided
try:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration

    dsn = os.getenv("SENTRY_DSN")
    if dsn:
        sentry_sdk.init(dsn=dsn, integrations=[CeleryIntegration()])
except Exception:
    # Sentry optional; ignore if not configured
    pass
