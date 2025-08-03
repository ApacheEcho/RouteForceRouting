
# Copilot Instructions for RouteForceRouting

## Project Overview
- **RouteForceRouting** is an AI-powered routing and sales execution platform for Direct Store Delivery (DSD) teams.
- The system includes a Python backend (Flask API, route optimization, scoring) and multiple mobile clients (React Native, PWA).

## Architecture & Key Components
- **Backend Core**: Legacy routing logic is in `routing/` (e.g., `core.py`, `route_scorer.py`, `loader.py`, `utils.py`, `playbook_constraints.py`). These modules delegate to modern services for most operations.
- **Modern Service Layer**: All new business logic and integrations are in `app/services/` (notably `route_scoring_service.py`, `route_core.py`, `geocoding_service.py`).
- **API Layer**: REST endpoints are defined in `app/routes/` (notably `scoring.py` for route scoring APIs).
- **Mobile Apps**: Located in `mobile/` (see `README.md` for structure and shared code in `mobile/shared/`).

## Developer Workflows
- **Local Dev (Backend)**: Use Docker (`docker-compose up --build`) or run Python scripts directly. See `README.md` for setup.
- **Testing (API)**: Run `pytest -v app/routes/scoring.py` or use the VS Code task "Run scoring API tests (all endpoints)" for API endpoint validation.
- **Unit Testing (Core)**: Run `pytest` in `routing/test/` for core logic.
- **Data Loading**: Use `python -m routing.loader path/to/file.xlsx` to load and validate store data. Data must have `Store Name` and `Address` columns.
- **Environment**: All secrets (API keys, etc.) must be set in `.env` and never committed.

## Routing & Scoring Patterns
- **Route Generation**: `routing/core.py` (legacy) delegates to `app/services/route_core.py` (modern). Use the modern service for new features.
- **Scoring**: Unified, weighted scoring in `app/services/route_scoring_service.py`. Scoring presets and component breakdowns are available; see the `/api/route/score/weights` endpoint for options.
- **Playbook Constraints**: Business rules are enforced via `routing/playbook_constraints.py` and playbook logic in the scoring service.
- **Geocoding**: Persistent caching in `geocoding_cache.json` (see `routing/utils.py` and `app/services/geocoding_service.py`). The cache file is critical for performance—first run is slow, subsequent runs are fast.

## Project Conventions & Integration Points
- **Data Format**: Store data must have `Store Name` and `Address` columns.
- **Testing Mode**: By default, route generation is limited to 10 stores for safety.
- **Performance**: Geocoding is cached; avoid deleting `geocoding_cache.json` unless necessary.
- **Mobile API**: All mobile clients use `/api/mobile` endpoints with JWT authentication. The default base URL is `http://localhost:5001/api/mobile`.
- **Scoring Presets**: Use the `/api/route/score/weights` endpoint to discover available scoring strategies (e.g., `balanced`, `distance_focused`, `priority_focused`, `traffic_aware`, `playbook_strict`).

## Examples
- **Score a route via API**: POST to `/api/route/score` with `{ "route": [...], "preset": "balanced" }`.
- **Compare routes**: POST to `/api/route/score/compare` with `{ "routes": [[...], [...]], "preset": "distance_focused" }`.
- **Load stores**: `python -m routing.loader stores.xlsx`

## Key Files & Directories
- `README.md` — Main project setup and architecture
- `routing/` — Core routing logic and legacy compatibility
- `app/services/route_core.py` — Modern route generation logic
- `app/services/route_scoring_service.py` — Scoring logic and presets
- `app/routes/scoring.py` — Scoring API endpoints
- `mobile/` — Mobile app code and shared API client

## Troubleshooting & FAQ
- **Missing `.env`**: The backend will not start or will fail API calls if secrets are missing.
- **Data Format Errors**: Store files must have `Store Name` and `Address` columns. See `routing/loader.py` for validation logic.
- **Exceeded Test Limits**: By default, only 10 stores are processed in test mode. Adjust config for production.
- **Geocoding Slow?**: First run is slow; subsequent runs are fast due to `geocoding_cache.json`.
- **API Key Leaks**: Never commit secrets. Rotate keys if exposed.

---
**For new AI agents:**
- Always check for `.env` and never commit secrets.
- Follow the data format and use provided scripts/utilities for loading and testing.
- Reference the scoring presets and component breakdowns for any route evaluation logic.
- Use the provided Docker and test commands for local development.
- This project is pre-alpha: do not use real production secrets or data in development/testing.
