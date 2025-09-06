# Changelog

All notable changes in this iteration (env unification + enterprise fixes).

## [Unreleased]

### Added
- New Optimization API stubs:
  - `POST /api/optimize/genetic` — validates input; returns stub response; 422 on XSS-like payloads.
  - `POST /api/optimize/multi-objective` — same behavior as above.
- New Export API stub:
  - `GET /api/export/routes` — simple JSON export placeholder.
- Metrics always include system gauges:
  - `routeforce_cpu_usage`, `routeforce_memory_usage`.

### Changed
- Unified env handling:
  - `REDIS_URL` available in `app.config`.
  - `CACHE_TYPE` shorthands (`simple|redis|null`) normalized to full backends.
  - `RATELIMIT_STORAGE_URI` and `CACHE_REDIS_URL` honored before fallback to `REDIS_URL`.
  - Sentry now supports `SENTRY_ENVIRONMENT` and `SENTRY_SERVER_NAME`.
  - Gunicorn respects `PORT`, `GUNICORN_WORKERS`, `GUNICORN_LOG_LEVEL`.
- RBAC: `/api/organizations/list` enforces `org.view` permission via enterprise user manager.
- Auth: JWT identity claim set to `id`; auth decorator falls back to enterprise user store when SQL user not found.
- Testing: When `TESTING=True`, database tables are created at app init to support shimmed requests.

### Removed
- Deleted unused `app/config/production.py` (production config lives in `app/config.py`).

### Documentation
- Updated `.env.*` templates and docs for the above env changes.
- README updated to reflect new endpoints and RBAC note.

