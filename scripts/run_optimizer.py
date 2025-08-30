#!/usr/bin/env python3
"""
Run RouteForce route optimization from JSON inputs.

Example:
  python scripts/run_optimizer.py \
    --stores data/samples/sf_20_stores.json \
    --vehicles data/samples/vehicles_small.json \
    --method two_opt --out routes.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure project root on sys.path when running from scripts/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from routing_engine import RouteOptimizer, OptimizationMethod
from routing.cli_adapter import store_dict_to_dataclass, vehicle_dict_to_dataclass

try:
    from app.utils.random_seed import seed_all_from_env
except Exception:
    def seed_all_from_env(default=None):  # type: ignore
        return None


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def route_to_dict(route) -> Dict[str, Any]:
    return {
        "route_id": route.route_id,
        "vehicle_id": route.vehicle_id,
        "driver_id": route.driver_id,
        "total_distance_km": route.total_distance_km,
        "estimated_duration_hours": route.estimated_duration_hours,
        "total_weight_kg": route.total_weight_kg,
        "total_packages": route.total_packages,
        "optimization_method": route.optimization_method,
        "created_at": route.created_at.isoformat(),
        "status": route.status,
        "stops": route.stops,
    }


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Run route optimization from JSON files")
    parser.add_argument("--stores", required=True, help="Path to stores JSON array")
    parser.add_argument("--vehicles", required=False, help="Path to vehicles JSON array")
    parser.add_argument(
        "--method",
        choices=[m.value for m in OptimizationMethod],
        default=OptimizationMethod.TWO_OPT.value,
        help="Optimization method",
    )
    parser.add_argument("--out", help="Write output JSON to this file (default stdout)")
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a concise summary (keeps JSON clean when printing to stdout)",
    )
    args = parser.parse_args(argv)

    seed_all_from_env()

    stores_raw = load_json(Path(args.stores))
    if not isinstance(stores_raw, list):
        print("--stores must be a JSON array", file=sys.stderr)
        return 2
    stores = [store_dict_to_dataclass(s) for s in stores_raw]

    if args.vehicles:
        vehicles_raw = load_json(Path(args.vehicles))
        if not isinstance(vehicles_raw, list):
            print("--vehicles must be a JSON array", file=sys.stderr)
            return 2
        vehicles = [vehicle_dict_to_dataclass(v) for v in vehicles_raw]
    else:
        # Default single vehicle at depot location
        vehicles = [vehicle_dict_to_dataclass({"vehicle_id": "V1"})]

    optimizer = RouteOptimizer()
    routes = optimizer.optimize_multi_vehicle_routes(
        stores, vehicles, OptimizationMethod(args.method)
    )

    result = {
        "method": args.method,
        "routes": [route_to_dict(r) for r in routes],
    }

    out_str = json.dumps(result, indent=2)
    if args.out:
        Path(args.out).write_text(out_str + "\n", encoding="utf-8")
    else:
        print(out_str)

    if args.summary:
        n_routes = len(routes)
        total_distance = round(sum(r.total_distance_km for r in routes), 2)
        total_stops = sum(len(r.stops) for r in routes)
        summary = f"Summary: method={args.method} routes={n_routes} total_distance_km={total_distance} total_stops={total_stops}"
        # If JSON was printed to stdout, write summary to stderr to avoid mixing
        if args.out:
            print(summary)
        else:
            print(summary, file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
