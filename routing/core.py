"""
Legacy routing core - Modernized with clean service architecture
This module provides backward compatibility while using modern services internally
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

# Import modern services
from app.services.route_core import RouteConstraints, create_route_generator
from app.services.route_core import generate_route as modern_generate_route
from app.services.route_core import print_route_summary as modern_print_route_summary
from app.services.route_core import summarize_route as modern_summarize_route

logger = logging.getLogger(__name__)


def generate_route(
    stores: List[Dict],
    visit_date: Optional[datetime] = None,
    playbook: Optional[Dict] = None,
) -> List[Dict]:
    """
    Generate optimized route from stores list (legacy compatibility)

    Args:
        stores: List of store dictionaries
        visit_date: Optional visit date for time-based filtering
        playbook: Optional playbook constraints

    Returns:
        List of stores representing optimized route
    """
    return modern_generate_route(stores, visit_date, playbook)


def summarize_route(
    route: List[Dict],
    original_stores: List[Dict],
    playbook: Optional[Dict] = None,
    visit_date: Optional[datetime] = None,
) -> Dict:
    """
    Generate route summary with analysis (legacy compatibility)

    Args:
        route: Generated route
        original_stores: Original store list
        playbook: Optional playbook constraints
        visit_date: Optional visit date

    Returns:
        Route summary dictionary
    """
    return modern_summarize_route(route, original_stores, playbook, visit_date)


def print_route_summary(summary: Dict) -> None:
    """
    Print a route summary in a clean, readable format (legacy compatibility)

    Args:
        summary: Route summary dictionary
    """
    modern_print_route_summary(summary)


def apply_playbook_constraints(
    stores: List[Dict], playbook: Dict, visit_date: Optional[datetime] = None
) -> List[Dict]:
    """
    Apply playbook constraints to filter stores (legacy compatibility)

    Args:
        stores: List of store dictionaries
        playbook: Playbook constraints
        visit_date: Optional visit date

    Returns:
        Filtered list of stores
    """
    logger.warning(
        "apply_playbook_constraints is deprecated. Use RouteConstraints with ModernRouteGenerator instead."
    )

    # Convert playbook to constraints and use modern generator
    constraints = RouteConstraints()
    if visit_date:
        constraints.visit_date = visit_date

    # Convert playbook format to modern constraints
    time_windows = {}
    priority_weights = {}
    max_stores = None

    for chain, config in playbook.items():
        if "visit_hours" in config:
            time_windows[chain] = config["visit_hours"]
        if "priority" in config:
            priority_weights[chain] = config["priority"]
        if "max_route_stops" in config:
            max_stores = config["max_route_stops"]

    constraints.time_windows = time_windows if time_windows else None
    constraints.priority_weights = priority_weights if priority_weights else None
    constraints.max_stores = max_stores

    # Use modern route generator to apply constraints
    generator = create_route_generator("priority")
    route, _ = generator.generate_route(stores, constraints)
    return route


# Modern API recommendations
def get_modern_route_generator(algorithm: str = "nearest_neighbor"):
    """
    Get a modern route generator instance

    Args:
        algorithm: Algorithm to use ("priority", "nearest_neighbor")

    Returns:
        ModernRouteGenerator instance
    """
    return create_route_generator(algorithm)


def calculate_route_summary(route: List[Dict]) -> Dict:
    """
    Calculate route summary (legacy compatibility)

    Args:
        route: List of route stops

    Returns:
        Dictionary with route summary
    """
    return modern_summarize_route(route, route)
