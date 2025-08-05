from typing import Any, Dict, List


class RouteScoreResult:
    """Container for route scoring results."""
    
    def __init__(self, score: float, details: str = "", issues: int = 0):
        self.score = score
        self.details = details
        self.issues = issues


def score_route(route: Dict[str, Any]) -> RouteScoreResult:
    """
    Compute a score for a given route based on distance, stops, and issues.
    Higher scores are better (0-100 scale).
    """
    distance = route.get("distance", 0)
    stops = route.get("stops", 0)
    issues = route.get("issues", 0)
    
    # Start with base score of 100 and deduct for problems
    score = 100.0
    
    # Deduct for distance (longer routes get lower scores)
    if distance > 0:
        score -= min(distance * 0.5, 40)  # Cap distance penalty at 40 points
    
    # Deduct for too many stops
    if stops > 10:
        score -= (stops - 10) * 2
    
    # Heavy penalty for issues
    score -= issues * 5
    
    # Ensure score stays within bounds
    score = max(0, min(100, score))
    
    details = f"Distance: {distance}, Stops: {stops}, Issues: {issues}"
    
    return RouteScoreResult(score, details, issues)

def rank_routes(routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rank a list of routes from best to worst based on their score.
    """
    def get_score(route):
        score_result = score_route(route)
        return score_result.score
    
    return sorted(routes, key=get_score, reverse=True)  # Higher scores are better
