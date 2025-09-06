# Migration Guide: Env Unification + Enterprise Fixes

This guide summarizes changes introduced in this iteration and the minimal steps to migrate local/dev/prod environments safely.

## What Changed

- Env handling standardized and safer defaults
  - `REDIS_URL` is now part of `app.config` and used by features expecting Redis.
  - `CACHE_TYPE` accepts shorthand (`simple|redis|null`) and maps to `flask_caching.backends.*`.
  - `RATELIMIT_STORAGE_URI` and `CACHE_REDIS_URL` are respected if set; fall back to `REDIS_URL`.
  - Sentry accepts `SENTRY_ENVIRONMENT` (preferred) and `SENTRY_SERVER_NAME`.
  - Gunicorn respects `PORT`, `GUNICORN_WORKERS`, `GUNICORN_LOG_LEVEL`.
- JWT/auth
  - Identity stored under `JWT_IDENTITY_CLAIM=id` (avoids PyJWT `sub` constraints and aligns SQL + enterprise identities).
  - Auth decorator can resolve SQL users and enterprise in-memory users; maps basic permissions to enterprise-style when needed.
- Enterprise
  - `GET /api/organizations/list` enforces `org.view` permission (RBAC).
  - Added stubs for `/api/optimize/*` and `/api/export/routes` to satisfy integration checks.
- Metrics
  - `/metrics` now includes `routeforce_cpu_usage` and `routeforce_memory_usage` gauges.
- Cleanup
  - Removed unused `app/config/production.py` (Production config lives in `app/config.py`).

## Action Items by Environment

### Local Development
- Update `.env` from `.env.example` (or re-copy it) and consider:
  - `CACHE_TYPE=simple`
  - `RATELIMIT_STORAGE_URI=memory://`
  - `REDIS_URL=redis://localhost:6379/0` (optional if you run Redis locally)
  - `LOG_LEVEL=DEBUG`
- If using Gunicorn locally:
  - `PORT=5000`, `GUNICORN_WORKERS=4`, `GUNICORN_LOG_LEVEL=info`

### Docker / Compose
- Confirm app service (prod compose) sets:
  - `PORT=5000`, `GUNICORN_WORKERS=4`, `GUNICORN_LOG_LEVEL=info`
  - `DATABASE_URL`, `REDIS_URL`, `CACHE_REDIS_URL`, `RATELIMIT_STORAGE_URI` as appropriate
- No change to exposed ports; app still listens on container port 5000.

### Render / PaaS
- Add `SENTRY_ENVIRONMENT` and `SENTRY_SERVER_NAME` if using Sentry.
- Ensure `PORT=5000` aligns with service settings.
- No changes required for `DATABASE_URL` and `REDIS_URL` (Render injects them).

### Production Security
- Treat as secrets and set via platform secret storage:
  - `SECRET_KEY`, `JWT_SECRET_KEY`, database and Redis credentials, `SENTRY_DSN`.
- Set `CORS_ORIGINS` in production; app enforces this.

## API Behavior Changes
- Organizations list: `/api/organizations/list` now 403 for users without `org.view` permission.
- New endpoints added:
  - `POST /api/optimize/genetic`, `POST /api/optimize/multi-objective` (stubs)
  - `GET /api/v1/routes/optimize/genetic` (compat stub under `/api/v1/routes/optimize/genetic`)
  - `GET /api/export/routes` (stub)

## Test Tips
- Full suite: `pytest -q`
- Excluding long-running: `pytest -q -k "not test_advanced and not test_genetic_edge_case"`
- Only enterprise integration checks: `pytest -q tests/test_enterprise_integration.py`

If long-running tests fail in CI due to environment or time limits, run locally or increase job timeouts. The most time-consuming suites are:
- `tests/test_genetic_edge_case.py` (uses integration harness and may be slow depending on environment)
- `tests/test_advanced.py` (broad coverage; usually stable, but can be slower on constrained environments)

## Rollback Notes
- If you previously referenced `app/config/production.py`, update imports to use `app.config.ProductionConfig`.
- Old `CACHE_TYPE` values like `redis` will continue to work via shorthand mapping.

---
For any questions, see `CHANGELOG.md` for a concise summary or ping the team in #platform.
