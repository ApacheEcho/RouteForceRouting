from typing import Any, Dict, List


def score_route(route: List[Dict[str, Any]]) -> float:
    """
    Compute a score for a given route based on distance, time, and other factors.
    Lower scores are better.
    """
    score = 0.0
    for stop in route:
        score += stop.get("distance", 0) * 0.7
        score += stop.get("time", 0) * 0.3

    return score


def rank_routes(routes: List[List[Dict[str, Any]]]) -> List[List[Dict[str, Any]]]:
    """
    Rank a list of routes from best to worst based on their score.
    """
    return sorted(routes, key=score_route)
