# API Schemas

This document summarizes the canonical JSON Schemas used by RouteForce and links to the source files.

- `schemas/store.schema.json` — Store objects or arrays of stores.
- `schemas/vehicle.schema.json` — Vehicle objects or arrays of vehicles.
- `schemas/route.schema.json` — Route results (full response) or arrays of stop objects.

## Store
- id: string or integer
- name: string (required)
- address: string (required)
- coordinates: either `lat` + `lng` or `latitude` + `longitude` (numbers)
- priority: one of `low|medium|high` or integer 1–3
- estimated_service_time: integer minutes ≥ 0
- packages: integer ≥ 0
- weight_kg: number ≥ 0

Schema: `schemas/store.schema.json`

## Vehicle
- vehicle_id: string (required)
- capacity_kg: integer ≥ 0 (required)
- max_packages: integer ≥ 0 (required)
- max_driving_hours: integer ≥ 0 (required)
- driver_id: string (optional)
- optional depot coordinates: either `lat` + `lng` or `latitude` + `longitude`

Schema: `schemas/vehicle.schema.json`

## Route Result / Stops
- stop:
  - id: string or integer (required)
  - name, address: strings (optional)
  - coordinates: either `lat`+`lng` or `latitude`+`longitude`
  - order: integer ≥ 0 (optional)
  - priority: `low|medium|high` or integer 1–3 (optional)
- result object:
  - route: array<stop> (required)
  - route_id: string or integer (optional)
  - algorithm_used: `default|genetic|simulated_annealing|multi_objective` (optional)
  - totals/metrics fields (optional): `total_distance_km`, `total_stops`, `processing_time`, `optimization_score`

Schema: `schemas/route.schema.json`

## Validation CLI
Use the lightweight CLI to validate JSON files against these schemas.

```bash
# Validate stores (array allowed)
python tools/schema_validate.py \
  --schema schemas/store.schema.json \
  --data data/samples/cli_demo/stores_12_sf_compact.json

# Validate vehicles (array allowed)
python tools/schema_validate.py \
  --schema schemas/vehicle.schema.json \
  --data data/samples/cli_demo/vehicles_sf_depot.json
```

The validator attempts to use `jsonschema` if present, otherwise falls back to an internal validator that supports the subset of features used in these schemas.

