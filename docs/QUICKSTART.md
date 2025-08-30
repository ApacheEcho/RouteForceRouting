# RouteForce Routing — Quickstart

This guide gets the API running locally, configures environment variables, and verifies a working endpoint with curl.

## Prerequisites
- Python 3.10+ with `pip`
- macOS/Linux shell (or WSL on Windows)
- Optional: Redis/Postgres (not required for Quickstart — SQLite fallback is used)

## 1) Setup virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2) Configure environment
Start from the provided template and adjust a couple values for local dev.
```bash
cp .env.example .env
```

Recommended for Quickstart (uses SQLite without external services):
- Either comment out the `DATABASE_URL` line in `.env` or set it to SQLite, for example:
  - `DATABASE_URL=sqlite:///routeforce_dev.db`
- Leave Redis-related values as-is; the app falls back to in-memory cache locally.

Key variables from `.env.example` you may want to review:
- `FLASK_ENV=development`
- `SECRET_KEY`, `JWT_SECRET_KEY`
- `DATABASE_URL` (see note above)
- `RATE_LIMITS`, `CORS_ORIGINS`

## 3) Initialize database (optional but recommended)
If you plan to call endpoints that persist data (e.g., route creation), apply DB migrations first. With SQLite this creates the local DB file.
```bash
bash scripts/run_db_upgrade.sh
```

## 4) Run the app
The dev runner starts Flask+Socket.IO. Default port is `5002`.
```bash
python run_app.py
# or override the port
PORT=5002 python run_app.py
```

You should see a startup banner with the URL.

## 5) Verify health
Use the API health endpoint (does not require DB/Redis):
```bash
examples/curl/health.sh
# or
curl -s http://localhost:5002/api/v1/health | jq .
```
Expected: a JSON object with `status: "healthy"` and an `endpoints` map.

## 6) Explore the API docs
Swagger UI is available locally:
```
http://localhost:5002/api/docs
```

## Next steps
- Try POST examples using the scripts under `examples/curl/` (they reference bodies in `examples/payloads/`).
- If you didn’t run DB migrations, prefer GET endpoints (like health); POST route creation persists data and expects tables to exist.

