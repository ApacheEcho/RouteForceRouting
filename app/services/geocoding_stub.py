"""
Lightweight NoOp geocoder used in tests to avoid external network calls.
Provides create_geocoder() -> object with get_coordinates(address) -> (lat,lng)
"""
from typing import Tuple, Dict, Any, Union
import hashlib


class NoOpGeocoder:
    def get_coordinates(self, store: Union[Dict[str, Any], str]) -> Tuple[float, float]:
        """
        Return deterministic coordinates for a store dict or address string.
        If a dict contains explicit lat/lon keys, return them; otherwise derive
        deterministic fallback coordinates from an MD5 hash of the address.
        """
        # If store is a dict, prefer lat/lng fields
        if isinstance(store, dict):
            lat = store.get("lat") or store.get("latitude") or store.get("latitude")
            lng = store.get("lon") or store.get("lng") or store.get("longitude")
            if lat is not None and lng is not None:
                try:
                    return float(lat), float(lng)
                except Exception:
                    pass
            address = store.get("address") or store.get("name") or ""
        else:
            address = str(store or "")

        if not address:
            return 0.0, 0.0

        # Deterministic fallback: use md5 of address to generate coords
        h = hashlib.md5(address.encode("utf-8")).hexdigest()
        lat = (int(h[:8], 16) % 180) - 90
        lng = (int(h[8:16], 16) % 360) - 180
        return float(lat), float(lng)


def create_geocoder():
    return NoOpGeocoder()
