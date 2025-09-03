# Declarative Model and App Context Audit

This audit lists files that reference the repository's separate SQLAlchemy declarative model sets (defined under `app/database/models.py` and `backup_deployment/database/models.py`) and files that use Flask `current_app` or `db.session` in ways that may run outside an application context.

Summary:

- Root cause: The repo contains two separate ORM model/metadatas:
  - Flask-SQLAlchemy models under `app/models` (uses `db = SQLAlchemy()` and `db.Model`)
  - Declarative-style models under `app/database/models.py` and `backup_deployment/database/models.py` (uses `declarative_base()` and standalone classes like `RouteInsightDB`, `RoutePredictionDB`).

- Why it breaks: SQLAlchemy mappers and relationships require a single metadata/registry for related models. Mixing the two results in mapper errors like "Could not determine join condition between parent/child tables" during test runs and runtime.

Recommendations (per-file):

1) High-priority: Replace imports of declarative models with Flask-SQLAlchemy models (preferred)

Files that import or directly use declarative models:

- `backup_deployment/services/database_integration.py`
  - Uses: `from app.database.models import RouteInsightDB, RoutePredictionDB`
  - Uses db.session queries against `RouteInsightDB` and `RoutePredictionDB` and constructs instances.
  - Recommended action: Migrate code to use `app.models.insight.Insight` and `app.models.prediction.Prediction` (if a prediction model exists) or store predictions as Insights. Ensure imports come from `app.models`.

- `app/database/models.py` and `backup_deployment/database/models.py`
  - Use: define `Base = declarative_base()` and classes `RouteInsightDB`, `RoutePredictionDB`, relationships referencing `Route`.
  - Recommended action: Remove or deprecate these files. If they are required for an isolated legacy path, ensure they use a separate engine and are never imported alongside `app.models` in the same runtime.

2) Medium-priority: Modules that call `db.session` or `current_app` frequently (may require app context fixes)

Files that frequently use `db.session` or `current_app` (candidates for wrapping in `with app.app_context()` or refactor to run inside request/worker context):

- `backup_deployment/services/database_service.py`
- `backup_deployment/services/database_integration.py` (also uses declarative models)
- `backup_deployment/services/routing_service.py`
- `backup_deployment/websocket_manager.py`
- `backup_deployment/services/geocoding_cache.py`
- `backup_deployment/services/file_service.py`
- `backup_deployment/routes/*` and `backup_deployment/api/*` (many route modules reference `current_app`)
- `app/services/database_service.py`
- `app/services/database_integration.py`
- `app/services/geocoding_cache.py`

Recommended action for app/context issues:

- For background tasks or modules that run outside requests, ensure calls to `db.session` and `current_app` occur inside `with app.app_context():` or are refactored to accept a Flask app instance or `db` instance injected at startup.
- For long-lived modules that import `current_app` at import time, change to access `current_app` inside functions (not at import time).

3) Other occurrences & notes

- `app.py` already uses `with app.app_context()` in some places — use that pattern for startup tasks.
- Tests that open an app context use `with app.app_context():` in test helpers — ensure tests import the correct models.

Next steps (recommended order):

1. Replace references to `RouteInsightDB` and `RoutePredictionDB` in `backup_deployment/services/database_integration.py` with `Insight` and `Prediction` from `app.models` and run the analytics test batch.
2. Remove or isolate `app/database/models.py` and `backup_deployment/database/models.py`. If kept, ensure they are only imported in isolated scripts that create their own engine/metadata.
3. Wrap background/cron/demo scripts that call `db.session` inside `with app.app_context()`.
4. Re-run failing pytest groups and iterate until mapper errors and app-context errors are resolved.

Appendix: Grep hits (truncated)

See repository grep results for `declarative_base`, `RouteInsightDB`, `RoutePredictionDB`, `app.database` and `current_app` references. The top offenders are `backup_deployment/services/database_integration.py`, `app/database/models.py`, and `backup_deployment/database/models.py`.
