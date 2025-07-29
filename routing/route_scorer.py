import logging
from typing import Any, Dict, List

from geopy.distance import geodesic


def score_route(route: List[Dict[str, Any]]) -> float:
    """
    Compute a deterministic score for a given route based on total distance and number of stops.
    Lower scores are better. Returns float('inf') for invalid input.
    Args:
        route: List of store dictionaries, each with 'latitude' and 'longitude'.
    Returns:
        Score (float): Lower is better. float('inf') if route is invalid.
    """
    logger = logging.getLogger(__name__)
    if not route or len(route) < 2:
        logger.warning("Route is empty or too short to score.")
        return float("inf")
    try:
        total_distance = sum(
            geodesic(
                (store["latitude"], store["longitude"]),
                (next_store["latitude"], next_store["longitude"]),
            ).km
            for store, next_store in zip(route[:-1], route[1:])
        )
        # Deterministic scoring: shorter distance and more stops is better
        score = total_distance + (100 / len(route))
        return score
    except Exception as e:
        logger.error(f"Failed to score route: {e}")
        return float("inf")


def rank_routes(routes: List[List[Dict[str, Any]]]) -> List[List[Dict[str, Any]]]:
    """
    Rank a list of routes from best to worst based on their score.
    Invalid or unscorable routes are ranked last.
    """
    return sorted(routes, key=score_route)
