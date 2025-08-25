
import pytest
import requests
from integration_test import RouteForceSystemTest


@pytest.mark.timeout(30)
def test_genetic_algorithm_population_one():
    """Edge case: Genetic algorithm with population size 1 should not fail."""
    # Create test instance without calling parent constructor
    class TestRouteForceSystemTest(RouteForceSystemTest):
        def __init__(self):
            # Initialize attributes directly without calling super().__init__()
            self.backend_url = "http://localhost:5001"  # Use correct port
            self.frontend_url = "http://localhost:3000"
            self.test_results = []
            self.jwt_token = None
            # Now authenticate with the correct port
            self.login_and_store_token()
    
    tester = TestRouteForceSystemTest()
    test_data = {
        "stops": [
            {"id": "1", "lat": 37.7749, "lng": -122.4194, "name": "Stop 1"},
            {"id": "2", "lat": 37.7849, "lng": -122.4094, "name": "Stop 2"},
        ],
        "depot": {"lat": 37.7549, "lng": -122.4494, "name": "Depot"},
        "algorithm": "genetic",
        "population_size": 1,
    }
    headers = tester.get_auth_headers()
    resp = requests.post(
        f"{tester.backend_url}/api/optimize",
        json=test_data,
        headers=headers,
        timeout=15,
    )
    assert resp.status_code == 200, f"Expected 200 OK, got {resp.status_code}"
    data = resp.json()
    assert data.get("success"), f"API did not return success: {data}"
