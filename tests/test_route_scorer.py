import pytest

from routing.route_scorer import rank_routes, score_route


@pytest.fixture
def sample_routes():
    route1 = {
        "distance_km": 10,
        "stops": ["A", "B", "C"],
        "stores": [{"priority": "high"}, {"priority": "medium"}, {"priority": "low"}],
    }
    route2 = {
        "distance_km": 7,
        "stops": ["A", "B"],
        "stores": [{"priority": "medium"}, {"priority": "medium"}],
    }
    return [route1, route2]


def test_score_route(sample_routes):
    score1 = score_route(sample_routes[0])
    score2 = score_route(sample_routes[1])
    # Check that scores are floats
    assert isinstance(score1, float)
    assert isinstance(score2, float)
    # Check that the scores are different
    assert score1 != score2
    # Manually check expected values
    # route1: distance=10, stops=3, avg_priority=(3+2+1)/3=2.0
    # score = 0.5*10 + 0.3*3 - 0.2*2 = 5 + 0.9 - 0.4 = 5.5
    assert score1 == 5.5
    # route2: distance=7, stops=2, avg_priority=(2+2)/2=2.0
    # score = 0.5*7 + 0.3*2 - 0.2*2 = 3.5 + 0.6 - 0.4 = 3.7
    assert score2 == 3.7


def test_rank_routes(sample_routes):
    ranked = rank_routes(sample_routes)
    # Should be sorted from lowest (best) to highest (worst) score
    assert ranked[0]["score"] < ranked[1]["score"]
    # route2 should be first (lower score)
    assert ranked[0]["distance_km"] == 7
    assert ranked[1]["distance_km"] == 10
    # Scores should match those from test_score_route
    assert ranked[0]["score"] == 3.7
    assert ranked[1]["score"] == 5.5
