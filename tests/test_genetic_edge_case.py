
import pytest
import requests
from integration_test import RouteForceSystemTest


@pytest.mark.timeout(30)
def test_genetic_algorithm_population_one():
    """Edge case: Genetic algorithm with population size 1 should not fail."""
    # Create test instance without calling parent constructor
    class TestRouteForceSystemTest(RouteForceSystemTest):
        def __init__(self):
            """Custom initialization to avoid parent constructor timing issues"""
            self.backend_url = "http://localhost:5000"
            self.login_and_store_token()
    
    tester = TestRouteForceSystemTest()
    test_data = {
        "stores": [
            {"id": "1", "lat": 37.7749, "lon": -122.4194, "name": "Stop 1"},
            {"id": "2", "lat": 37.7849, "lon": -122.4094, "name": "Stop 2"},
        ],
        "constraints": {},
        "genetic_config": {
            "population_size": 1,
            "generations": 50,  # Reduced for faster testing
            "mutation_rate": 0.02,
            "crossover_rate": 0.8,
            "elite_size": 1,
            "tournament_size": 1,
        }
    }
    headers = tester.get_auth_headers()
    resp = requests.post(
        f"{tester.backend_url}/api/v1/routes/optimize/genetic",
        json=test_data,
        headers=headers,
        timeout=15,
    )
    assert resp.status_code == 200, f"Expected 200 OK, got {resp.status_code}"
    data = resp.json()
    assert data.get("success"), f"API did not return success: {data}"
