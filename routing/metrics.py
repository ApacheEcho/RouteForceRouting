def score_route(route):
    """
    Score the route using the unified scoring logic from route_scorer.
    Args:
        route: List of store dictionaries.
    Returns:
        A score (float) representing the route quality.
    """
    import logging

    from routing.route_scorer import score_route as unified_score_route

    logger = logging.getLogger(__name__)
    try:
        return unified_score_route(route)
    except Exception as e:
        logger.error(f"metrics.score_route failed: {e}")
        return float("inf")
