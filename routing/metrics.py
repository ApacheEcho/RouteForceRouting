from geopy.distance import geodesic


def score_route(route):
    """
    Score the route based on distance and number of stops.

    Args:
        route: List of store dictionaries.

    Returns:
        A score (float) representing the route quality.
    """
    if not route or len(route) < 2:
        return 0.0

    total_distance = sum(
        geodesic(
            (store["latitude"], store["longitude"]),
            (next_store["latitude"], next_store["longitude"]),
        ).km
        for store, next_store in zip(route[:-1], route[1:])
    )

    # Example scoring formula: shorter distance and more stops yield higher scores
    return max(0.0, 1000 / (total_distance + len(route)))
