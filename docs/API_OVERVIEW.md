# RouteForce Routing — API Overview

Base URL (local dev): `http://localhost:5002`

General behavior
- Content type: JSON required for POST/PUT/PATCH under `/api/*` (`Content-Type: application/json`).
- Error handling: JSON errors with `error`, `code`, `timestamp` (see Common Errors).
- Rate limiting: Applied via `flask-limiter`. Some endpoints stricter than others.
- Auth: A subset (e.g., Mobile, Analytics) expect `X-API-Key`. Many core v1 endpoints don’t require auth in development.

Primary endpoints

1) GET `/api/v1/health`
- Purpose: Lightweight API health and discovery.
- Request: No body.
- Response (200):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "endpoints": {
    "create_route": "/api/v1/routes",
    "get_routes": "/api/v1/routes",
    "get_route": "/api/v1/routes/<id>",
    "get_stores": "/api/v1/stores",
    "generate_route": "/api/v1/routes/generate",
    "optimize_genetic": "/api/v1/routes/optimize/genetic",
    "optimize_simulated_annealing": "/api/v1/routes/optimize/simulated_annealing",
    "get_algorithms": "/api/v1/routes/algorithms",
    "create_clusters": "/api/v1/clusters",
    "ml_predict": "/api/v1/ml/predict",
    "ml_recommend": "/api/v1/ml/recommend",
    "ml_train": "/api/v1/ml/train",
    "ml_model_info": "/api/v1/ml/model-info",
    "generate_route_ml": "/api/v1/routes/generate/ml"
  },
  "algorithms": {
    "available": ["default", "genetic", "simulated_annealing", "multi_objective"],
    "default": "default"
  }
}
```

2) POST `/api/v1/routes` — Create optimized route
- Body fields:
  - `stores` (required): array of stores. Minimum each item has `name`; include `address` or coordinates if available.
  - `constraints` (optional): `{ max_distance, max_time, vehicle_capacity, ... }`.
  - `options` (optional): `{ algorithm, traffic_aware, optimize_for, ... }` and algorithm-specific params (e.g., `ga_population_size`).
- Example request (see `examples/payloads/create_route.json`):
```json
{
  "stores": [
    { "name": "Store A", "address": "1600 Amphitheatre Pkwy, Mountain View, CA" },
    { "name": "Store B", "address": "1 Hacker Way, Menlo Park, CA" },
    { "name": "Store C", "address": "410 Terry Ave N, Seattle, WA" }
  ],
  "constraints": { "max_distance": 100.0 },
  "options": { "algorithm": "genetic", "ga_population_size": 50 }
}
```
- Example response (201):
```json
{
  "success": true,
  "data": {
    "route": [ { "name": "Store A" }, { "name": "Store B" }, { "name": "Store C" } ],
    "route_id": 123,
    "algorithm_used": "genetic"
  },
  "message": "Route created successfully",
  "metadata": {
    "total_stores": 3,
    "route_stores": 3,
    "processing_time": 0.12,
    "optimization_score": 0.0
  },
  "timestamp": "2025-01-01T12:00:00Z"
}
```
Notes
- Persists to DB when available. For SQLite, run `scripts/run_db_upgrade.sh` before using this endpoint.

3) POST `/api/v1/clusters` — Create proximity clusters
- Body fields:
  - `stores` (required): each with `latitude` and `longitude`.
  - `radius_km` (optional, default 2.0).
- Example request (see `examples/payloads/clusters.json`):
```json
{
  "stores": [
    { "id": "s1", "name": "A", "latitude": 37.7749, "longitude": -122.4194 },
    { "id": "s2", "name": "B", "latitude": 37.7849, "longitude": -122.4094 },
    { "id": "s3", "name": "C", "latitude": 37.7649, "longitude": -122.4294 }
  ],
  "radius_km": 2.0
}
```
- Example response (200):
```json
{
  "clusters": [ [ {"id":"s1"}, {"id":"s2"} ], [ {"id":"s3"} ] ],
  "cluster_count": 2,
  "total_stores": 3,
  "radius_km": 2.0
}
```

4) POST `/api/v1/ml/predict` — Predict performance (ML)
- Body fields:
  - `stores` (required): items with `id`, `name`, `lat`, `lon`, optional `priority`, `demand`.
  - `context` (optional): `{ weather_factor, traffic_factor, timestamp }`.
- Example request (see `examples/payloads/ml_predict.json`):
```json
{
  "stores": [
    { "id": "store_1", "name": "Downtown", "lat": 40.7128, "lon": -74.0060, "priority": 1, "demand": 150 },
    { "id": "store_2", "name": "Uptown",   "lat": 40.7580, "lon": -73.9855, "priority": 2, "demand": 200 }
  ],
  "context": { "weather_factor": 1.0, "traffic_factor": 1.1, "timestamp": "2025-01-01T10:30:00Z" }
}
```
- Example response (200): shape depends on model, e.g. `{ "success": true, ... }` with predicted metrics.

Related endpoints
- Traffic API: `POST /api/traffic/optimize` (see payload in `examples/payloads/traffic_optimize.json`).
- Mobile API: `GET /api/mobile/health`, `POST /api/mobile/routes/optimize` (requires `X-API-Key`).
- Analytics API: `GET /api/analytics/health`, plus analytics data endpoints (require `X-API-Key`).

Common errors
- 400: Validation failed (e.g., missing fields, invalid numbers).
- 401: Unauthorized (e.g., missing/invalid `X-API-Key` for protected endpoints).
- 415: Invalid content type — use `Content-Type: application/json` for JSON endpoints.
- 429: Rate limit exceeded — retry later.
- 500: Internal error.

