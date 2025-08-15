"""
Maps link generation utilities
"""

import urllib.parse
from typing import Any, Dict, List


def generate_google_maps_link(waypoints: List[Dict[str, Any]]) -> str:
    """
    Generate Google Maps link for a list of waypoints

    Args:
        waypoints: List of waypoint dictionaries with latitude/longitude

    Returns:
        Google Maps URL string
    """
    if not waypoints:
        return "No waypoints provided"

    # Filter out invalid coordinates
    valid_waypoints = []
    for wp in waypoints:
        lat = wp.get("latitude")
        lon = wp.get("longitude")
        if lat is not None and lon is not None:
            try:
                float(lat)
                float(lon)
                valid_waypoints.append(wp)
            except (ValueError, TypeError):
                continue

    if not valid_waypoints:
        return "No valid coordinates found"

    if len(valid_waypoints) == 1:
        # Single destination
        lat, lon = (
            valid_waypoints[0]["latitude"],
            valid_waypoints[0]["longitude"],
        )
        return f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

    # Multiple waypoints - create directions URL
    origin = valid_waypoints[0]
    destination = valid_waypoints[-1]

    origin_str = f"{origin['latitude']},{origin['longitude']}"
    dest_str = f"{destination['latitude']},{destination['longitude']}"

    # Add intermediate waypoints if any
    if len(valid_waypoints) > 2:
        waypoint_strs = []
        for wp in valid_waypoints[1:-1]:
            waypoint_strs.append(f"{wp['latitude']},{wp['longitude']}")
        waypoints_param = "|".join(waypoint_strs)
        return f"https://www.google.com/maps/dir/?api=1&origin={origin_str}&destination={dest_str}&waypoints={waypoints_param}"
    else:
        return f"https://www.google.com/maps/dir/?api=1&origin={origin_str}&destination={dest_str}"


def generate_apple_maps_link(waypoints: List[Dict[str, Any]]) -> str:
    """
    Generate Apple Maps link for a list of waypoints

    Args:
        waypoints: List of waypoint dictionaries with latitude/longitude

    Returns:
        Apple Maps URL string
    """
    if not waypoints:
        return "No waypoints provided"

    # Filter out invalid coordinates
    valid_waypoints = []
    for wp in waypoints:
        lat = wp.get("latitude")
        lon = wp.get("longitude")
        if lat is not None and lon is not None:
            try:
                float(lat)
                float(lon)
                valid_waypoints.append(wp)
            except (ValueError, TypeError):
                continue

    if not valid_waypoints:
        return "No valid coordinates found"

    if len(valid_waypoints) == 1:
        # Single destination
        lat, lon = (
            valid_waypoints[0]["latitude"],
            valid_waypoints[0]["longitude"],
        )
        return f"http://maps.apple.com/?q={lat},{lon}"

    # Multiple waypoints - create directions URL
    origin = valid_waypoints[0]
    destination = valid_waypoints[-1]

    origin_str = f"{origin['latitude']},{origin['longitude']}"
    dest_str = f"{destination['latitude']},{destination['longitude']}"

    return f"http://maps.apple.com/?saddr={origin_str}&daddr={dest_str}"


def generate_fallback_directions_text(waypoints: List[Dict[str, Any]]) -> str:
    """
    Generate fallback text directions when maps links can't be created

    Args:
        waypoints: List of waypoint dictionaries

    Returns:
        Text description of the route
    """
    if not waypoints:
        return "No waypoints provided"

    directions = ["Route directions:"]
    for i, wp in enumerate(waypoints, 1):
        name = wp.get("name", f"Stop {i}")
        address = wp.get("address", "Address not available")
        lat = wp.get("latitude", "N/A")
        lon = wp.get("longitude", "N/A")

        directions.append(f"{i}. {name}")
        directions.append(f"   Address: {address}")
        directions.append(f"   Coordinates: {lat}, {lon}")

    return "\n".join(directions)
