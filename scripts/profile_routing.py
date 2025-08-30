#!/usr/bin/env python3
"""
Lightweight profiling for core routing operations.

Generates synthetic stores/vehicles and times optimization methods.

Usage:
  python scripts/profile_routing.py --stores 30 --vehicles 3 --method two_opt
"""

from __future__ import annotations

import argparse
import json
import random
import time
from dataclasses import asdict
from typing import Any, Dict, List

from pathlib import Path
import sys

# Ensure project root on sys.path when running from scripts/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from routing_engine import RouteOptimizer, Store, Vehicle, VehicleStatus, OptimizationMethod

try:
    # Honor deterministic runs when RFR_SEED is set
    from app.utils.random_seed import seed_all_from_env
except Exception:
    def seed_all_from_env(default=None):  # type: ignore
        return None


def make_stores(n: int) -> List[Store]:
    # Around Manhattan
    base_lat, base_lng = 40.75, -73.98
    stores: List[Store] = []
    for i in range(n):
        lat = round(base_lat + random.uniform(-0.15, 0.15), 6)
        lng = round(base_lng + random.uniform(-0.15, 0.15), 6)
        stores.append(
            Store(
                store_id=f"S{i+1}",
                name=f"Store {i+1}",
                address=f"{100+i} 5th Ave",
                coordinates={"lat": lat, "lng": lng},
                delivery_window="09:00-17:00",
                priority=random.choice(["low", "medium", "high"]),
                estimated_service_time=random.choice([10, 15, 20]),
                packages=random.randint(1, 5),
                weight_kg=random.randint(5, 25),
            )
        )
    return stores


def make_vehicles(k: int) -> List[Vehicle]:
    vehicles: List[Vehicle] = []
    for i in range(k):
        vehicles.append(
            Vehicle(
                vehicle_id=f"V{i+1}",
                capacity_kg=500.0,
                max_packages=100,
                max_driving_hours=8.0,
                status=VehicleStatus.AVAILABLE,
                current_location=None,
                driver_id=f"D{i+1}",
            )
        )
    return vehicles


def main() -> int:
    parser = argparse.ArgumentParser(description="Profile routing optimization")
    parser.add_argument("--stores", type=int, default=20, help="# of stores to generate")
    parser.add_argument("--vehicles", type=int, default=2, help="# of vehicles")
    parser.add_argument(
        "--method",
        choices=[m.value for m in OptimizationMethod],
        default=OptimizationMethod.TWO_OPT.value,
        help="Optimization method",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON summary")
    args = parser.parse_args()

    seed_all_from_env()

    stores = make_stores(args.stores)
    vehicles = make_vehicles(args.vehicles)

    method = OptimizationMethod(args.method)
    optimizer = RouteOptimizer()

    start = time.time()
    routes = optimizer.optimize_multi_vehicle_routes(stores, vehicles, method)
    elapsed = time.time() - start

    summary: Dict[str, Any] = {
        "method": method.value,
        "stores": args.stores,
        "vehicles": args.vehicles,
        "routes": len(routes),
        "elapsed_sec": round(elapsed, 4),
        "total_distance_km": round(sum(r.total_distance_km for r in routes), 2),
    }

    if args.json:
        print(json.dumps(summary))
    else:
        print(f"Method: {summary['method']}")
        print(f"Stores: {summary['stores']}, Vehicles: {summary['vehicles']}")
        print(f"Routes: {summary['routes']}, Time: {summary['elapsed_sec']}s")
        print(f"Total distance: {summary['total_distance_km']} km")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
