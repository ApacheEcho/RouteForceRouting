"""
Helper functions to convert loose JSON dicts to routing_engine dataclasses.
Kept small and dependency-free for reuse by scripts.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from routing_engine import Store as StoreDC, Vehicle as VehicleDC, VehicleStatus


def _coord_from(d: Dict[str, Any]) -> Dict[str, float]:
    lat = d.get("lat")
    lng = d.get("lng", d.get("lon"))
    if lat is None:
        lat = d.get("latitude")
    if lng is None:
        lng = d.get("longitude")
    if lat is None or lng is None:
        raise ValueError("Missing latitude/longitude in store record")
    return {"lat": float(lat), "lng": float(lng)}


def store_dict_to_dataclass(d: Dict[str, Any]) -> StoreDC:
    """Map a generic dict to routing_engine.Store dataclass."""
    coordinates = _coord_from(d)
    store_id = str(d.get("store_id", d.get("id", d.get("name", "store"))))
    return StoreDC(
        store_id=store_id,
        name=str(d.get("name", store_id)),
        address=str(d.get("address", "Unknown")),
        coordinates=coordinates,
        delivery_window=str(d.get("delivery_window", "09:00-17:00")),
        priority=str(d.get("priority", "medium")),
        estimated_service_time=int(d.get("estimated_service_time", 15)),
        packages=int(d.get("packages", 1)),
        weight_kg=float(d.get("weight_kg", 1.0)),
        special_requirements=d.get("special_requirements"),
    )


def vehicle_dict_to_dataclass(d: Dict[str, Any]) -> VehicleDC:
    """Map a generic dict to routing_engine.Vehicle dataclass."""
    status_str = str(d.get("status", VehicleStatus.AVAILABLE.value))
    try:
        status = VehicleStatus(status_str)
    except Exception:
        status = VehicleStatus.AVAILABLE

    current_location: Optional[Dict[str, float]] = None
    if any(k in d for k in ("lat", "lng", "lon", "latitude", "longitude")):
        current_location = _coord_from(d)

    return VehicleDC(
        vehicle_id=str(d.get("vehicle_id", d.get("id", "vehicle"))),
        capacity_kg=float(d.get("capacity_kg", 500.0)),
        max_packages=int(d.get("max_packages", 100)),
        max_driving_hours=float(d.get("max_driving_hours", 8.0)),
        status=status,
        current_location=current_location,
        driver_id=(str(d["driver_id"]) if d.get("driver_id") is not None else None),
    )

