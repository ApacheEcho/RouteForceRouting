# Secrets Checklist

Use this checklist to configure all required secrets for deployment. Prefer Render deployment with a Deploy Hook; fall back to API key + service ID if needed. For VPS, configure local environment and CI variables as appropriate.

## Render (Recommended)
- Required (choose one path):
  - RENDER_DEPLOY_HOOK: Web Service → Settings → Deploy hooks → Create hook → copy URL
  - OR both of:
    - RENDER_API_KEY: From Render dashboard → Account → API Keys
    - RENDER_SERVICE_ID: Web Service URL contains `srv-xxxxxxxx` (also in Settings → General)
- Application secrets:
  - SECRET_KEY: Strong, random Flask secret key
  - JWT_SECRET_KEY: Strong, random JWT signing key
  - CORS_ORIGINS: Comma-separated list of allowed origins (e.g., https://app.routeforcepro.com)
  - SENTRY_DSN: Optional, for error tracking
  - METRICS_TOKEN: Optional token to protect /metrics endpoints (set header X-Metrics-Token)
  - HEALTHCHECK_URL: Optional full URL to poll after deploy (e.g., https://your-domain/health)
  - METRICS_URL: Optional full URL to poll after deploy (e.g., https://your-domain/metrics)

Recommended GitHub CLI setup:
```bash
gh secret set RENDER_DEPLOY_HOOK --body="https://api.render.com/deploy/srv-..."  # or set RENDER_API_KEY + RENDER_SERVICE_ID
gh secret set RENDER_API_KEY --body="<render-api-key>"
gh secret set RENDER_SERVICE_ID --body="srv-xxxxxxxxxxxxxxxx"
gh secret set SECRET_KEY --body="<random-64-128-hex>"
gh secret set JWT_SECRET_KEY --body="<random-64-128-hex>"
gh secret set CORS_ORIGINS --body="https://app.routeforcepro.com"
gh secret set SENTRY_DSN --body="https://<dsn>"  # optional
gh secret set METRICS_TOKEN --body="<random-token>"  # optional
gh secret set HEALTHCHECK_URL --body="https://your-domain/health"  # optional
gh secret set METRICS_URL --body="https://your-domain/metrics"  # optional
```

## VPS (NGINX + Gunicorn)
- On-server environment (.env.production):
  - SECRET_KEY
  - JWT_SECRET_KEY
  - DATABASE_URL (e.g., postgresql://user:pass@localhost:5432/routeforce_prod)
  - CORS_ORIGINS (must be set in production)
- Optional CI/CD (if you add SSH-based automation):
  - PROD_HOST, PROD_USER, SSH_PRIVATE_KEY

## Validation
- Run: `python3 scripts/preflight_deploy_check.py` → expect all ✅
- After deploy: `curl -fsS https://your-domain/health` → 200 + healthy response
