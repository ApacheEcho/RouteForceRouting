# Synthetic Data Generator

This tool generates realistic synthetic datasets for stores and vehicles that match RouteForce’s API/tests shape.

- Output directories: only writes under `data/samples/`.
- Deterministic runs with `--seed`.
- No external network or file reads.

## Install/Run

No extra deps beyond Python stdlib.

```bash
python tools/data_gen/generate_datasets.py --help
```

## Generate Stores

Generate 20 San Francisco stores (deterministic):
```bash
python tools/data_gen/generate_datasets.py \
  --city sf --count 20 --seed 123 \
  --out data/samples/sf_20_stores.json
```

Generate 50 NYC stores with custom radius and service-time range:
```bash
python tools/data_gen/generate_datasets.py \
  --city nyc --count 50 --radius-km 30 \
  --service-time-min 8 --service-time-max 25 \
  --out data/samples/nyc_50_stores.json
```

Use custom center instead of presets:
```bash
python tools/data_gen/generate_datasets.py \
  --center-lat 47.6062 --center-lng -122.3321 \
  --count 30 --seed 42 \
  --out data/samples/seattle_30_stores.json
```

Schema (stores):
- `id` (str), `name` (str), `address` (str),
- `latitude` (float), `longitude` (float),
- optional: `priority` (int), `estimated_service_time` (int, minutes),
- `packages` (int), `weight_kg` (float)

## Generate Vehicles

Generate 8 vehicles:
```bash
python tools/data_gen/generate_datasets.py \
  --mode vehicles --vehicles-count 8 --seed 7 \
  --out data/samples/vehicles_custom.json
```

Schema (vehicles):
- `vehicle_id` (str), `capacity_kg` (int), `max_packages` (int),
- `max_driving_hours` (int), optional `driver_id` (str)

## Notes
- The tool validates that `--out` resolves inside `data/samples/` and will refuse to write elsewhere.
- Coordinates are sampled uniformly within a circle of `--radius-km` around the chosen center.
- We use simple, readable synthetic addresses to avoid external geocoding.

