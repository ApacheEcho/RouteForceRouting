# Secrets Checklist

Render (recommended)
- RENDER_DEPLOY_HOOK or (RENDER_API_KEY + RENDER_SERVICE_ID)
- SECRET_KEY, JWT_SECRET_KEY
- CORS_ORIGINS
- Optional: SENTRY_DSN, METRICS_TOKEN, HEALTHCHECK_URL, METRICS_URL

VPS
- .env.production: SECRET_KEY, JWT_SECRET_KEY, DATABASE_URL, CORS_ORIGINS, optional METRICS_TOKEN
- Optional CI: PROD_HOST, PROD_USER, SSH_PRIVATE_KEY

Validation
- python3 scripts/preflight_deploy_check.py
- ./scripts/smoke_post_deploy.sh https://your-domain [METRICS_TOKEN]
