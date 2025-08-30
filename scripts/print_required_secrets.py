#!/usr/bin/env python3
import os

for key in [
    "RENDER_DEPLOY_HOOK","RENDER_API_KEY","RENDER_SERVICE_ID",
    "SECRET_KEY","JWT_SECRET_KEY","CORS_ORIGINS","SENTRY_DSN",
    "METRICS_TOKEN","HEALTHCHECK_URL","METRICS_URL"
]:
    val = os.getenv(key)
    print(f"{'✅' if val else '❌'} {key}")

