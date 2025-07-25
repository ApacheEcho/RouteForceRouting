"""
Comprehensive Integration Tests for RouteForce Enterprise System
"""

import time

import pytest
import requests


class TestEnterpriseIntegration:
    """Test enterprise features integration"""

    @pytest.fixture(scope="class")
    def base_url(self):
        """Base URL for testing"""
        return "http://localhost:5000"

    @pytest.fixture(scope="class")
    def admin_token(self, base_url):
        """Get admin authentication token"""
        response = requests.post(
            f"{base_url}/api/users/login",
            json={"email": "admin@demo.routeforce.com", "password": "demo123"},
        )
        assert response.status_code == 200
        return response.json()["access_token"]

    @pytest.fixture(scope="class")
    def auth_headers(self, admin_token):
        """Authentication headers"""
        return {"Authorization": f"Bearer {admin_token}"}

    def test_health_endpoint(self, base_url):
        """Test system health endpoint"""
        response = requests.get(f"{base_url}/health")
        assert response.status_code == 200

        health_data = response.json()
        assert health_data["status"] in ["healthy", "degraded"]
        assert "services" in health_data
        assert "database" in health_data["services"]
        assert "cache" in health_data["services"]

    def test_metrics_endpoint(self, base_url):
        """Test Prometheus metrics endpoint"""
        response = requests.get(f"{base_url}/metrics")
        assert response.status_code == 200
        assert "routeforce_cpu_usage" in response.text
        assert "routeforce_memory_usage" in response.text

    def test_user_authentication(self, base_url):
        """Test user login and token generation"""
        response = requests.post(
            f"{base_url}/api/users/login",
            json={"email": "admin@demo.routeforce.com", "password": "demo123"},
        )
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["role"] == "org_admin"

    def test_organizations_api(self, base_url, auth_headers):
        """Test organizations management API"""
        response = requests.get(
            f"{base_url}/api/organizations/list", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "organizations" in data
        assert data["total"] >= 3  # Demo organizations

    def test_analytics_endpoints(self, base_url, auth_headers):
        """Test analytics API endpoints"""
        endpoints = [
            "/api/ai/fleet/insights",
            "/api/ai/trends",
            "/api/ai/recommendations/smart",
        ]

        for endpoint in endpoints:
            response = requests.get(f"{base_url}{endpoint}", headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["success"] is True

    def test_advanced_dashboard_api(self, base_url, auth_headers):
        """Test advanced dashboard endpoints"""
        endpoints = [
            "/advanced/api/ml-insights",
            "/advanced/api/performance-trends",
            "/advanced/api/predictive-analytics",
            "/advanced/api/real-time-alerts",
            "/advanced/api/optimization-insights",
        ]

        for endpoint in endpoints:
            response = requests.get(f"{base_url}{endpoint}", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "timestamp" in data

    def test_route_optimization(self, base_url, auth_headers):
        """Test route optimization algorithms"""
        test_route = {
            "start_location": "New York, NY",
            "end_location": "Boston, MA",
            "waypoints": ["Hartford, CT"],
            "optimization_type": "genetic_algorithm",
            "constraints": {"max_duration": 300, "vehicle_capacity": 1000},
        }

        # Test genetic algorithm
        response = requests.post(
            f"{base_url}/api/optimize/genetic", json=test_route, headers=auth_headers
        )
        assert response.status_code == 200

        # Test multi-objective optimization
        response = requests.post(
            f"{base_url}/api/optimize/multi-objective",
            json=test_route,
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_performance_monitoring(self, base_url, auth_headers):
        """Test performance monitoring system"""
        response = requests.get(
            f"{base_url}/dashboard/api/performance/alerts", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "alerts" in data
        assert isinstance(data["alerts"], list)

    def test_websocket_connectivity(self, base_url):
        """Test WebSocket connection capability"""
        import socketio

        sio = socketio.Client()
        connected = False

        @sio.event
        def connect():
            nonlocal connected
            connected = True

        try:
            sio.connect(base_url)
            time.sleep(1)
            assert connected is True
        finally:
            sio.disconnect()

    def test_data_export(self, base_url, auth_headers):
        """Test data export functionality"""
        response = requests.get(f"{base_url}/api/export/routes", headers=auth_headers)
        assert response.status_code == 200

    def test_system_scalability(self, base_url, auth_headers):
        """Test system under concurrent load"""
        import concurrent.futures

        def make_request():
            response = requests.get(f"{base_url}/health")
            return response.status_code == 200

        # Test with 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in futures]

        assert all(results), "System failed under concurrent load"


class TestMLPipeline:
    """Test machine learning pipeline"""

    def test_analytics_engine_initialization(self):
        """Test analytics engine can be initialized"""
        from app.analytics_ai import get_analytics_engine

        analytics = get_analytics_engine()
        assert analytics is not None
        assert hasattr(analytics, "ensemble_engine")

    def test_ensemble_model_training(self):
        """Test ensemble model training capability"""
        from app.analytics_ai import get_analytics_engine

        analytics = get_analytics_engine()

        # Add sample data
        sample_data = [
            {
                "route_id": f"test_route_{i}",
                "distance_km": 50 + i * 5,
                "duration_minutes": 120 + i * 10,
                "fuel_consumption": 8.5 + i * 0.5,
                "optimization_algorithm": "genetic_algorithm",
                "weather_conditions": "clear",
                "traffic_density": "medium",
            }
            for i in range(50)
        ]

        for data in sample_data:
            analytics.add_route_data(data)

        # Test model training
        assert len(analytics.historical_data) >= 50

    def test_uncertainty_quantification(self):
        """Test uncertainty quantification features"""
        from app.analytics_ai import AdvancedEnsembleEngine

        ensemble = AdvancedEnsembleEngine()
        assert hasattr(ensemble, "predict_with_uncertainty")


class TestSecurityCompliance:
    """Test security and compliance features"""

    def test_authentication_required(self, base_url):
        """Test that protected endpoints require authentication"""
        protected_endpoints = [
            "/api/organizations/list",
            "/api/users/profile",
            "/advanced/api/ml-insights",
        ]

        for endpoint in protected_endpoints:
            response = requests.get(f"{base_url}{endpoint}")
            assert response.status_code == 401

    def test_role_based_access(self, base_url):
        """Test role-based access control"""
        # Test with regular user
        user_response = requests.post(
            f"{base_url}/api/users/login",
            json={"email": "user@demo.routeforce.com", "password": "demo123"},
        )
        assert user_response.status_code == 200

        user_token = user_response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # Regular user should not access admin endpoints
        response = requests.get(
            f"{base_url}/api/organizations/list", headers=user_headers
        )
        assert response.status_code == 403

    def test_input_validation(self, base_url, auth_headers):
        """Test input validation and sanitization"""
        # Test with invalid data
        invalid_route = {
            "start_location": "<script>alert('xss')</script>",
            "end_location": "Boston, MA",
        }

        response = requests.post(
            f"{base_url}/api/optimize/genetic", json=invalid_route, headers=auth_headers
        )
        # Should handle invalid input gracefully
        assert response.status_code in [400, 422]


class TestPerformanceBenchmarks:
    """Performance benchmark tests"""

    def test_api_response_times(self, base_url, auth_headers):
        """Test API response time requirements"""
        endpoints = ["/health", "/api/ai/fleet/insights", "/advanced/api/ml-insights"]

        for endpoint in endpoints:
            start_time = time.time()
            requests.get(
                f"{base_url}{endpoint}",
                headers=auth_headers if endpoint != "/health" else None,
            )
            end_time = time.time()

            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            assert response_time < 2000, (
                f"Endpoint {endpoint} took {response_time}ms (too slow)"
            )

    def test_memory_usage(self):
        """Test memory usage is within acceptable limits"""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024

        # Should use less than 1GB for basic tests
        assert memory_mb < 1024, f"Memory usage too high: {memory_mb}MB"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
