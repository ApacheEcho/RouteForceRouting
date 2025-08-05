"""
Route logging utilities for RouteForceRouting
"""

import logging
from datetime import datetime
from typing import Dict, Any, List


def log_route_score(route_data: Dict[str, Any], score: float) -> None:
    """
    Log route scoring information

    Args:
        route_data: Dictionary containing route information
        score: Calculated route score
    """
    logger = logging.getLogger(__name__)
    logger.info(
        f"Route scored: {score:.2f} for route with {len(route_data.get('stops', []))} stops"
    )


def log_route_generation(route_id: str, num_stops: int, duration: float) -> None:
    """
    Log route generation information

    Args:
        route_id: Unique identifier for the route
        num_stops: Number of stops in the route
        duration: Time taken to generate the route in seconds
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Route {route_id} generated with {num_stops} stops in {duration:.2f}s")


def log_route_error(route_id: str, error: str) -> None:
    """
    Log route generation errors

    Args:
        route_id: Unique identifier for the route
        error: Error message
    """
    logger = logging.getLogger(__name__)
    logger.error(f"Route {route_id} generation failed: {error}")
