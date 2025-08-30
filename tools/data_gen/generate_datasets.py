#!/usr/bin/env python3
"""
Synthetic dataset generator for RouteForce Routing.

Generates realistic stores and vehicles JSON that match API/tests.
Writes only within data/samples/ and supports deterministic --seed.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple


# Preset city centers (lat, lng)
CITY_CENTERS: Dict[str, Tuple[float, float, str]] = {
    "sf": (37.7749, -122.4194, "San Francisco, CA"),
    "nyc": (40.7128, -74.0060, "New York, NY"),
    "la": (34.0522, -118.2437, "Los Angeles, CA"),
}


def _ensure_out_path_within_samples(out_path: str) -> str:
    """Resolve and ensure out_path is inside data/samples/ under the repo.

    Never writes outside target dirs per project policy.
    """
    abs_out = os.path.realpath(out_path)
    cwd = os.path.realpath(os.getcwd())
    samples_root = os.path.realpath(os.path.join(cwd, "data", "samples"))
    if not abs_out.startswith(samples_root + os.sep) and abs_out != samples_root:
        raise SystemExit(
            f"Refusing to write outside data/samples/: {out_path} (resolved to {abs_out})"
        )
    # Ensure parent dirs exist
    os.makedirs(os.path.dirname(abs_out), exist_ok=True)
    return abs_out


def _uniform_point_in_radius_km(center_lat: float, center_lng: float, radius_km: float) -> Tuple[float, float]:
    """Sample a point uniformly within a circle of radius_km around a center.

    Uses simple planar approximation: 1 deg lat ~ 111 km, 1 deg lng ~ 111 km * cos(lat).
    """
    # Uniform radius: sqrt(u) to avoid clustering at center
    u = random.random()
    r_km = radius_km * math.sqrt(u)
    theta = 2.0 * math.pi * random.random()

    # Convert km offsets to degrees
    km_per_deg_lat = 111.0
    km_per_deg_lng = 111.0 * math.cos(math.radians(center_lat))
    dlat = (r_km * math.sin(theta)) / km_per_deg_lat
    dlng = (r_km * math.cos(theta)) / max(1e-9, km_per_deg_lng)
    return center_lat + dlat, center_lng + dlng


def _rand_int(a: int, b: int) -> int:
    return int(random.randint(a, b))


def _rand_float(a: float, b: float, ndigits: int = 2) -> float:
    return round(random.uniform(a, b), ndigits)


def generate_stores(
    *,
    city: str | None,
    center_lat: float | None,
    center_lng: float | None,
    radius_km: float,
    count: int,
    priority_min: int,
    priority_max: int,
    service_time_min: int,
    service_time_max: int,
    packages_min: int,
    packages_max: int,
    per_package_weight_min: float,
    per_package_weight_max: float,
) -> List[Dict]:
    if center_lat is None or center_lng is None:
        if not city:
            raise SystemExit("Either --city or both --center-lat/--center-lng are required")
        if city not in CITY_CENTERS:
            raise SystemExit(f"Unknown city '{city}'. Choose from: {', '.join(CITY_CENTERS)}")
        clat, clng, city_name = CITY_CENTERS[city]
    else:
        clat, clng, city_name = center_lat, center_lng, (city or "Custom City")

    stores: List[Dict] = []
    city_prefix = (city or "custom").lower()
    for i in range(1, count + 1):
        lat, lng = _uniform_point_in_radius_km(clat, clng, radius_km)
        priority = _rand_int(priority_min, priority_max)
        packages = _rand_int(packages_min, packages_max)
        per_pkg = _rand_float(per_package_weight_min, per_package_weight_max, ndigits=2)
        total_weight = round(packages * per_pkg, 2)
        street_no = _rand_int(10, 9999)
        street = random.choice(
            [
                "Market St",
                "Main St",
                "Broadway",
                "Mission St",
                "Sunset Blvd",
                "Pine St",
                "Cedar Ave",
                "Maple Ave",
            ]
        )
        store = {
            "id": f"{city_prefix}_store_{i:03d}",
            "name": f"{city_name} Store {i}",
            "address": f"{street_no} {street}, {city_name}",
            "latitude": round(lat, 6),
            "longitude": round(lng, 6),
            "priority": priority,
            "estimated_service_time": _rand_int(service_time_min, service_time_max),
            "packages": packages,
            "weight_kg": total_weight,
        }
        stores.append(store)

    return stores


def generate_vehicles(*, count: int, city: str | None) -> List[Dict]:
    fleet_prefix = (city or "fleet").lower()
    vehicles: List[Dict] = []
    for i in range(1, count + 1):
        capacity = _rand_int(600, 1800)
        max_packages = _rand_int(60, 220)
        max_hours = _rand_int(8, 11)
        vehicle = {
            "vehicle_id": f"{fleet_prefix}_veh_{i:02d}",
            "capacity_kg": capacity,
            "max_packages": max_packages,
            "max_driving_hours": max_hours,
        }
        # include driver_id on some vehicles
        if random.random() < 0.7:
            vehicle["driver_id"] = f"driver_{i:03d}"
        vehicles.append(vehicle)
    return vehicles


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate synthetic stores/vehicles datasets")
    p.add_argument("--mode", choices=["stores", "vehicles"], default="stores", help="What to generate")
    p.add_argument("--city", choices=list(CITY_CENTERS.keys()), help="Preset city center")
    p.add_argument("--center-lat", type=float, help="Custom center latitude (overrides --city if set)")
    p.add_argument("--center-lng", type=float, help="Custom center longitude (overrides --city if set)")
    p.add_argument("--radius-km", type=float, default=25.0, help="Sampling radius around center in km (stores mode)")
    p.add_argument("--count", type=int, default=20, help="Number of stores to generate (stores mode)")
    p.add_argument("--vehicles-count", type=int, default=10, help="Number of vehicles (vehicles mode)")
    p.add_argument("--priority-min", type=int, default=1)
    p.add_argument("--priority-max", type=int, default=3)
    p.add_argument("--service-time-min", type=int, default=5)
    p.add_argument("--service-time-max", type=int, default=30)
    p.add_argument("--packages-min", type=int, default=1)
    p.add_argument("--packages-max", type=int, default=6)
    p.add_argument("--weight-kg-min", type=float, default=0.5, help="Per-package min weight")
    p.add_argument("--weight-kg-max", type=float, default=8.0, help="Per-package max weight")
    p.add_argument("--seed", type=int, help="Deterministic seed")
    p.add_argument("--out", required=True, help="Output JSON path under data/samples/")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.seed is not None:
        random.seed(args.seed)

    out_path = _ensure_out_path_within_samples(args.out)

    if args.mode == "stores":
        data = generate_stores(
            city=args.city,
            center_lat=args.center_lat,
            center_lng=args.center_lng,
            radius_km=args.radius_km,
            count=args.count,
            priority_min=args.priority_min,
            priority_max=args.priority_max,
            service_time_min=args.service_time_min,
            service_time_max=args.service_time_max,
            packages_min=args.packages_min,
            packages_max=args.packages_max,
            per_package_weight_min=args.weight_kg_min,
            per_package_weight_max=args.weight_kg_max,
        )
    else:
        data = generate_vehicles(count=args.vehicles_count, city=args.city)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Wrote {len(data)} items to {out_path}")


if __name__ == "__main__":
    main()

