RouteForce Scripts

1) run_optimizer.py
- Purpose: Run the core optimizer from JSON files.
- Usage:
  - env: set RFR_SEED to make runs deterministic (optional)
  - example:
    - export RFR_SEED=123
    - python scripts/run_optimizer.py \
        --stores data/samples/cli_demo/stores_8_sf.json \
        --vehicles data/samples/cli_demo/vehicles_small.json \
        --method two_opt --out /tmp/routes_demo.json
- Inputs:
  - stores: JSON array with fields like id/name/address and either lat/lng or latitude/longitude.
  - vehicles: JSON array with vehicle_id/capacity_kg/max_packages/max_driving_hours; optional status and coordinates.
- Output: JSON with routes; prints to stdout unless --out is provided.

2) profile_routing.py
- Purpose: Generate synthetic stores and measure optimization performance.
- Usage:
  - export RFR_SEED=123  # optional
  - python scripts/profile_routing.py --stores 30 --vehicles 3 --method two_opt --json
- Notes:
  - Uses a Manhattan-like area for synthetic points.
  - Does not require any input files.

