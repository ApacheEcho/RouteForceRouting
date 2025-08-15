from typing import Any, Dict, List


def score_route(route: Dict[str, Any]) -> float:
    """
    Compute a score for a given route based on distance, number of stops, and average store priority.
    Lower scores are better.
    """
    distance = route.get("distance_km", 0)
    num_stops = len(route.get("stops", []))
    stores = route.get("stores", [])
    # Map priority to numeric: high=3, medium=2, low=1
    priority_map = {"high": 3, "medium": 2, "low": 1}
    if stores:
        avg_priority = sum(
            priority_map.get(s.get("priority", "medium"), 2) for s in stores
        ) / len(stores)
    else:
        avg_priority = 2.0
    # Scoring formula matches the test's comments
    score = 0.5 * distance + 0.3 * num_stops - 0.2 * avg_priority
    return round(score, 2)


def rank_routes(routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rank a list of routes from best to worst based on their score.
    """
    scored = [dict(route, score=score_route(route)) for route in routes]
    return sorted(scored, key=lambda r: r["score"])
