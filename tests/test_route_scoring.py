import os
from datetime import datetime

from routing.playbook_constraints import enforce_playbook_constraints
from routing.route_logger import log_route_score
from routing.route_preflight import should_reject_route
from routing.route_scorer import score_route


def generate_routes():
    raw_routes = [
        {"distance": 12.5, "stops": 8, "issues": 0},
        {"distance": 45.2, "stops": 20, "issues": 2},
        {"distance": 70.1, "stops": 30, "issues": 5},
    ]

    scored_routes = []
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(
        log_dir, f"route_scores_{datetime.today().strftime('%Y-%m-%d')}.txt"
    )

    for route in raw_routes:
        score_result = score_route(route)
        if not enforce_playbook_constraints(route):
            continue
        if should_reject_route(score_result):
            continue
        route["score"] = score_result.score
        scored_routes.append(route)
        log_route_score(score_result, log_file)

    return scored_routes


def test_generate_routes():
    routes = generate_routes()
    assert isinstance(routes, list)
    for route in routes:
        assert "score" in route
        assert isinstance(route["score"], (int, float))


def test_generate_routes_output_range():
    routes = generate_routes()
    for i, route in enumerate(routes):
        assert (
            0 <= route["score"] <= 100
        ), f"[Route {i}] Score out of expected range: {route['score']}"
        print(
            f"[Route {i}] Validated score: {route['score']} (Distance: {route['distance']}, Stops: {route['stops']}, Issues: {route['issues']})"
        )


def test_generate_routes_issues_weight():
    routes = generate_routes()
    if routes:
        high_issue_route = {"distance": 10, "stops": 5, "issues": 99}
        score_result = score_route(high_issue_route)
        assert (
            score_result.score < 50
        ), f"Expected low score due to high issues, got {score_result.score}"
        print(
            f"Tested high-issue route (99 issues), received score: {score_result.score}"
        )


# Edge case: all parameters zero
def test_generate_routes_all_zero():
    zero_route = {"distance": 0, "stops": 0, "issues": 0}
    score_result = score_route(zero_route)
    assert (
        score_result.score >= 0
    ), f"Score should not be negative: {score_result.score}"
    print(f"Tested zeroed route, received score: {score_result.score}")


# Edge case: maxed parameters
def test_generate_routes_all_max():
    max_route = {"distance": 1000, "stops": 1000, "issues": 1000}
    score_result = score_route(max_route)
    assert (
        score_result.score <= 100
    ), f"Score should not exceed 100: {score_result.score}"
    assert (
        0 <= score_result.score <= 100
    ), f"Score out of bounds for max input: {score_result.score}"
    print(
        f"[Edge Max] Validated maxed route score: {score_result.score} for 1000 distance, 1000 stops, 1000 issues"
    )


# Edge case: missing key fields
def test_generate_routes_missing_fields():
    incomplete_route = {
        "distance": 25.0,
        "stops": 10,
    }  # 'issues' field is missing
    try:
        score_result = score_route(incomplete_route)
        assert hasattr(
            score_result, "score"
        ), "Score result should have a score attribute"
        print(f"Tested incomplete route, received score: {score_result.score}")
    except Exception as e:
        print(f"Handled missing field gracefully: {e}")
