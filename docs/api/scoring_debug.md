# Scoring Debug API Documentation

## Endpoint

### POST /api/route/score?debug=true
- Accepts: JSON payload (see below)
- Query param: `debug=true` to enable debug output

#### Example Payload
```json
{
  "route": [
    {"name": "Store A", "lat": 40.7128, "lon": -74.0060, "priority": 8},
    {"name": "Store B", "lat": 40.7589, "lon": -73.9851, "priority": 6},
    {"name": "Store C", "lat": 40.7505, "lon": -73.9934, "priority": 9}
  ],
  "preset": "balanced"
}
```

#### Example Response
```json
{
  "success": true,
  "score": { ... },
  "debug": {
    "total_score": 87.5,
    "components": { ... },
    "formula": "..."
  }
}
```

### Notes
- `debug` key only present if `debug=true`
- Role restrictions apply (JWT required)
