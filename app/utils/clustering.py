"""
Proximity clustering utilities for route optimization
"""

import logging
from typing import Any, Dict, List

from geopy.distance import geodesic

logger = logging.getLogger(__name__)


def cluster_by_proximity(
    stores: List[Dict[str, Any]], radius_km: float = 2.0
) -> List[List[Dict[str, Any]]]:
    """
    Cluster stores by proximity using a greedy algorithm

    Args:
        stores: List of store dictionaries with lat/lon coordinates
        radius_km: Clustering radius in kilometers

    Returns:
        List of store clusters
    """
    if not stores:
        return []

    clusters = []
    unprocessed = stores.copy()

    while unprocessed:
        # Start new cluster with first unprocessed store
        seed_store = unprocessed.pop(0)
        cluster = [seed_store]

        # Find all stores within radius of the seed store
        i = 0
        while i < len(unprocessed):
            store = unprocessed[i]
            if is_within_radius(seed_store, store, radius_km):
                cluster.append(unprocessed.pop(i))
            else:
                i += 1

        clusters.append(cluster)

    logger.debug(
        f"Clustered {len(stores)} stores into {len(clusters)} clusters with radius {radius_km}km"
    )
    return clusters


def is_within_radius(
    store1: Dict[str, Any], store2: Dict[str, Any], radius_km: float
) -> bool:
    """
    Check if two stores are within specified radius

    Args:
        store1: First store dictionary
        store2: Second store dictionary
        radius_km: Radius in kilometers

    Returns:
        True if stores are within radius
    """
    # Get coordinates from either lat/lon or latitude/longitude fields
    lat1 = store1.get("lat") or store1.get("latitude")
    lon1 = store1.get("lon") or store1.get("longitude")
    lat2 = store2.get("lat") or store2.get("latitude")
    lon2 = store2.get("lon") or store2.get("longitude")

    # Return False if any coordinates are missing
    if not all([lat1, lon1, lat2, lon2]):
        return False

    try:
        # Convert to float in case they're strings
        lat1, lon1, lat2, lon2 = (
            float(lat1),
            float(lon1),
            float(lat2),
            float(lon2),
        )

        # Calculate distance using geodesic
        distance = geodesic((lat1, lon1), (lat2, lon2)).kilometers
        return distance <= radius_km

    except (ValueError, TypeError) as e:
        logger.warning(f"Error calculating distance between stores: {e}")
        return False


def get_cluster_center(cluster: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate the geographic center of a cluster

    Args:
        cluster: List of store dictionaries

    Returns:
        Dictionary with lat/lon of cluster center
    """
    if not cluster:
        return {"lat": 0.0, "lon": 0.0}

    valid_stores = []
    for store in cluster:
        lat = store.get("lat") or store.get("latitude")
        lon = store.get("lon") or store.get("longitude")
        if lat and lon:
            try:
                valid_stores.append({"lat": float(lat), "lon": float(lon)})
            except (ValueError, TypeError):
                continue

    if not valid_stores:
        return {"lat": 0.0, "lon": 0.0}

    # Calculate centroid
    avg_lat = sum(store["lat"] for store in valid_stores) / len(valid_stores)
    avg_lon = sum(store["lon"] for store in valid_stores) / len(valid_stores)

    return {"lat": avg_lat, "lon": avg_lon}


def optimize_cluster_order(
    clusters: List[List[Dict[str, Any]]],
) -> List[List[Dict[str, Any]]]:
    """
    Optimize the order of clusters for efficient routing

    Args:
        clusters: List of store clusters

    Returns:
        Reordered clusters for optimal routing
    """
    if len(clusters) <= 1:
        return clusters

    # Calculate cluster centers
    cluster_centers = [get_cluster_center(cluster) for cluster in clusters]

    # Simple nearest neighbor ordering starting from first cluster
    ordered_clusters = [clusters[0]]
    remaining_indices = list(range(1, len(clusters)))
    current_center = cluster_centers[0]

    while remaining_indices:
        # Find nearest cluster center
        min_distance = float("inf")
        nearest_idx = None

        for idx in remaining_indices:
            center = cluster_centers[idx]
            try:
                distance = geodesic(
                    (current_center["lat"], current_center["lon"]),
                    (center["lat"], center["lon"]),
                ).kilometers

                if distance < min_distance:
                    min_distance = distance
                    nearest_idx = idx
            except Exception:
                continue

        if nearest_idx is not None:
            ordered_clusters.append(clusters[nearest_idx])
            current_center = cluster_centers[nearest_idx]
            remaining_indices.remove(nearest_idx)
        else:
            # Fallback: add remaining clusters in original order
            for idx in remaining_indices:
                ordered_clusters.append(clusters[idx])
            break

    return ordered_clusters
