import math

from app.services.route_scoring_service import RouteScorer
from app.services.routing_service_unified import create_unified_routing_service


def sample_stores():
    # Three nearby points in San Francisco
    return [
        {"name": "A", "lat": 37.7749, "lon": -122.4194, "priority": 8},
        {"name": "B", "lat": 37.7849, "lon": -122.4094, "priority": 5},
        {"name": "C", "lat": 37.7649, "lon": -122.4294, "priority": 3},
    ]


def test_calculate_comprehensive_score_single_component_distance():
    route = sample_stores()
    scorer = RouteScorer()

    # Distance-only weight should equal distance component * 100
    score = scorer.calculate_comprehensive_score(
        route, {"distance_weight": 1.0}
    )
    expected = scorer._calculate_distance_score(route) * 100.0

    assert isinstance(score, float)
    assert 0.0 <= score <= 100.0
    assert math.isclose(score, expected, rel_tol=1e-6, abs_tol=1e-6)


def test_unified_service_metrics_use_comprehensive_score():
    stores = sample_stores()
    service = create_unified_routing_service()

    # Generate route (no DB persistence because no user_id)
    route = service.generate_route_from_stores(stores, save_to_db=False)

    # Metrics should exist and optimization_score should come from scorer
    metrics = service.get_metrics()
    assert metrics is not None

    scorer = RouteScorer()
    weights = {
        "distance_weight": 0.6,
        "time_weight": 0.2,
        "priority_weight": 0.2,
    }
    expected = scorer.calculate_comprehensive_score(route, weights)

    assert 0.0 <= metrics.optimization_score <= 100.0
    assert math.isclose(
        metrics.optimization_score, expected, rel_tol=1e-6, abs_tol=1e-6
    )

