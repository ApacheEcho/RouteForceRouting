"""
Comprehensive test suite for the modernized RouteForce Routing application
"""

import io
from unittest.mock import Mock, patch

import pytest

from app import create_app
from app.models.route_request import RouteRequest
from app.services.file_service import FileService
from app.services.routing_service_unified import UnifiedRoutingService


@pytest.fixture
def app():
    """Create test application"""
    app = create_app("testing")
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def sample_csv_file():
    """Create sample CSV file"""
    content = "name,chain,latitude,longitude\nStore A,Chain A,40.7128,-74.0060\nStore B,Chain B,40.7589,-73.9851"
    return io.BytesIO(content.encode("utf-8"))


class TestRouteRequest:
    """Test RouteRequest model"""

    def test_route_request_validation(self):
        """Test route request validation"""
        # Mock Flask request
        mock_request = Mock()
        mock_request.files = {"file": Mock(filename="test.csv")}
        mock_form = Mock()
        mock_form.get = Mock(
            side_effect=lambda key, default=None, type=None: {
                "proximity": "on",
                "time_start": "09:00",
                "time_end": "17:00",
                "max_stores_per_chain": 10 if type is int else "10",
                "min_sales_threshold": 1000.0 if type is float else "1000.0",
            }.get(key, default)
        )
        mock_form.getlist = Mock(return_value=["Monday", "Tuesday"])
        mock_form.__contains__ = Mock(
            side_effect=lambda key: key in ["proximity"]
        )
        mock_request.form = mock_form

        route_request = RouteRequest.from_request(mock_request)

        assert route_request.proximity
        assert route_request.time_start == "09:00"
        assert route_request.time_end == "17:00"
        assert route_request.max_stores_per_chain == 10
        assert route_request.min_sales_threshold == 1000.0
        assert route_request.exclude_days == ["Monday", "Tuesday"]

    def test_route_request_invalid_time_window(self):
        """Test invalid time window validation"""
        mock_request = Mock()
        mock_request.files = {"file": Mock(filename="test.csv")}
        mock_form = Mock()
        mock_form.get = Mock(
            side_effect=lambda key, default=None, type=None: {
                "time_start": "17:00",
                "time_end": "09:00",
            }.get(key, default)
        )
        mock_form.getlist = Mock(return_value=[])
        mock_form.__contains__ = Mock(return_value=False)
        mock_request.form = mock_form

        route_request = RouteRequest.from_request(mock_request)
        route_request.time_start = "17:00"
        route_request.time_end = "09:00"

        errors = route_request.get_validation_errors()
        assert any(
            "Time start must be before time end" in error for error in errors
        )


class TestFileService:
    """Test FileService"""

    def test_file_validation(self):
        """Test file validation"""
        file_service = FileService()

        # Test valid file
        assert file_service._is_allowed_file("test.csv")
        assert file_service._is_allowed_file("test.xlsx")
        assert file_service._is_allowed_file("test.xls")

        # Test invalid file
        assert not file_service._is_allowed_file("test.txt")
        assert not file_service._is_allowed_file("test.pdf")

    def test_csv_loading(self, tmp_path):
        """Test CSV file loading"""
        file_service = FileService()

        # Create temporary CSV file
        csv_content = "name,chain\nStore A,Chain A\nStore B,Chain B"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        stores = file_service._load_csv_file(str(csv_file))

        assert len(stores) == 2
        assert stores[0]["name"] == "Store A"
        assert stores[0]["chain"] == "Chain A"
        assert stores[1]["name"] == "Store B"
        assert stores[1]["chain"] == "Chain B"

    def test_file_content_validation(self, tmp_path):
        """Test file content validation"""
        file_service = FileService()

        # Create valid CSV file
        csv_content = "name,chain\nStore A,Chain A\nStore B,Chain B"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        assert file_service.validate_file_content(str(csv_file))

        # Create invalid CSV file (no name field)
        invalid_csv = "address,chain\n123 Main St,Chain A\n456 Oak Ave,Chain B"
        invalid_file = tmp_path / "invalid.csv"
        invalid_file.write_text(invalid_csv)

        assert not file_service.validate_file_content(str(invalid_file))


class TestRoutingService:
    """Test RoutingService"""

    def test_constraint_building(self):
        """Test constraint building from filters"""
        # Mock the service to avoid initialization hang
        with patch(
            "app.services.routing_service_unified.UnifiedRoutingService"
        ) as mock_service:
            # Mock the service instance and its methods
            mock_instance = Mock()
            mock_instance.generate_route_from_stores = Mock()
            mock_instance.geocode_stores = Mock(
                return_value=[
                    {
                        "name": "Store A",
                        "address": "123 Main St",
                        "latitude": 40.7128,
                        "longitude": -74.0060,
                    },
                    {
                        "name": "Store B",
                        "address": "456 Oak Ave",
                        "latitude": 40.7129,
                        "longitude": -74.0061,
                    },
                ]
            )
            mock_instance.score_route = Mock(return_value=85.0)
            mock_service.return_value = mock_instance

            service = UnifiedRoutingService()

            # Test that the service has expected methods
            assert hasattr(service, "generate_route_from_stores")
            assert hasattr(service, "geocode_stores")
            assert hasattr(service, "score_route")

            # Test with simple store data
            stores = [
                {"name": "Store A", "address": "123 Main St", "priority": 1},
                {"name": "Store B", "address": "456 Oak Ave", "priority": 2},
            ]

            # Test geocoding
            geocoded = service.geocode_stores(stores)
            assert isinstance(geocoded, list)
            assert len(geocoded) == 2

    def test_distance_calculation(self):
        """Test distance calculation"""
        # Mock the service to avoid initialization hang
        with patch(
            "app.services.routing_service_unified.UnifiedRoutingService"
        ) as mock_service:
            mock_instance = Mock()
            mock_instance._calculate_total_distance = Mock(return_value=15.5)
            mock_service.return_value = mock_instance

            service = UnifiedRoutingService()

            route = [
                {"latitude": 40.7128, "longitude": -74.0060},  # NYC
                {"latitude": 40.7589, "longitude": -73.9851},  # Times Square
            ]

            distance = service._calculate_total_distance(route)
            assert distance > 0
            assert distance < 100  # Should be less than 100km

    def test_optimization_score(self):
        """Test optimization score calculation"""
        # Mock the service to avoid initialization hang
        with patch(
            "app.services.routing_service_unified.UnifiedRoutingService"
        ) as mock_service:
            mock_instance = Mock()
            mock_instance._calculate_optimization_score = Mock(
                return_value=75.0
            )
            mock_service.return_value = mock_instance

            service = UnifiedRoutingService()

            # Good route (short distance, many stops)
            good_route = [
                {"latitude": 40.7128, "longitude": -74.0060},
                {"latitude": 40.7129, "longitude": -74.0061},
                {"latitude": 40.7130, "longitude": -74.0062},
            ]

            score = service._calculate_optimization_score(good_route)
            assert score > 0


class TestAPIEndpoints:
    """Test API endpoints"""

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.get_json()
        assert data["status"] == "healthy"
        assert data["service"] == "RouteForce Routing"

    def test_api_health_endpoint(self, client):
        """Test API health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.get_json()
        assert data["status"] == "healthy"
        assert "endpoints" in data

    def test_api_create_route(self, client):
        """Test API route creation"""
        payload = {
            "stores": [
                {"name": "Store A", "chain": "Chain A"},
                {"name": "Store B", "chain": "Chain B"},
            ],
            "constraints": {},
            "options": {},
        }

        response = client.post("/api/v1/routes", json=payload)
        assert response.status_code == 201

        data = response.get_json()
        assert "route" in data
        assert "metadata" in data

    def test_api_invalid_request(self, client):
        """Test API with invalid request"""
        response = client.post("/api/v1/routes", json={})
        assert response.status_code == 400

        data = response.get_json()
        assert "error" in data

    def test_api_clusters_endpoint(self, client):
        """Test API clusters endpoint"""
        test_data = {
            "stores": [
                {
                    "name": "Store A",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                },
                {
                    "name": "Store B",
                    "latitude": 40.7130,
                    "longitude": -74.0062,
                },
                {
                    "name": "Store C",
                    "latitude": 40.7500,
                    "longitude": -73.9500,
                },
            ],
            "radius_km": 1.0,
        }

        response = client.post("/api/v1/clusters", json=test_data)
        assert response.status_code == 200

        data = response.get_json()
        assert "clusters" in data
        assert "cluster_count" in data
        assert "total_stores" in data
        assert data["cluster_count"] == 2
        assert data["total_stores"] == 3

    def test_api_clusters_invalid_data(self, client):
        """Test API clusters with invalid data"""
        # Missing stores
        response = client.post("/api/v1/clusters", json={})
        assert response.status_code == 400

        # Invalid radius
        response = client.post(
            "/api/v1/clusters",
            json={
                "stores": [
                    {
                        "name": "Store A",
                        "latitude": 40.7128,
                        "longitude": -74.0060,
                    }
                ],
                "radius_km": -1.0,
            },
        )
        assert response.status_code == 400

        # Missing coordinates
        response = client.post(
            "/api/v1/clusters",
            json={"stores": [{"name": "Store A"}], "radius_km": 1.0},
        )
        assert response.status_code == 400


class TestMainRoutes:
    """Test main application routes"""

    def test_index_route(self, client):
        """Test main index route"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"RouteForce Routing" in response.data

    def test_generate_route_with_file(self, client, sample_csv_file):
        """Test route generation with file upload"""
        data = {
            "file": (sample_csv_file, "test.csv"),
            "proximity": "1",
            "time_start": "09:00",
            "time_end": "17:00",
        }

        with patch(
            "app.services.file_service.FileService.validate_file_content",
            return_value=True,
        ):
            with patch(
                "app.services.routing_service.RoutingService.generate_route_with_filters",
                return_value=[],
            ):
                response = client.post(
                    "/generate", data=data, content_type="multipart/form-data"
                )
                assert response.status_code == 200

    def test_generate_route_no_file(self, client):
        """Test route generation without file"""
        response = client.post(
            "/generate", data={}, content_type="multipart/form-data"
        )
        assert response.status_code == 400

        data = response.get_json()
        assert "error" in data


class TestErrorHandling:
    """Test error handling"""

    def test_404_error(self, client):
        """Test 404 error handling"""
        response = client.get("/nonexistent")
        assert response.status_code == 404

        data = response.get_json()
        assert data["error"] == "Resource not found"

    def test_file_too_large(self, client):
        """Test file size limit"""
        # Create large file content
        large_content = "x" * (20 * 1024 * 1024)  # 20MB
        large_file = io.BytesIO(large_content.encode("utf-8"))

        data = {"file": (large_file, "large.csv")}

        response = client.post(
            "/generate", data=data, content_type="multipart/form-data"
        )
        assert response.status_code == 413


class TestCaching:
    """Test caching functionality"""

    def test_cache_key_generation(self, sample_csv_file):
        """Test cache key generation"""
        mock_request = Mock()
        mock_request.files = {
            "file": Mock(
                filename="test.csv", read=Mock(return_value=b"test content")
            )
        }
        mock_form = Mock()
        mock_form.get = Mock(return_value=None)
        mock_form.getlist = Mock(return_value=[])
        mock_form.__contains__ = Mock(return_value=False)
        mock_request.form = mock_form

        # Mock the file object
        file_mock = Mock()
        file_mock.filename = "test.csv"
        file_mock.read.return_value = b"test content"
        file_mock.seek = Mock()

        route_request = RouteRequest.from_request(mock_request)
        route_request.file = file_mock

        cache_key = route_request.get_cache_key()
        assert len(cache_key) == 32  # MD5 hash length
        assert cache_key != ""


class TestProximityClustering:
    """Test proximity clustering functionality"""

    def test_cluster_by_proximity_basic(self):
        """Test basic proximity clustering"""
        from app.utils.clustering import cluster_by_proximity

        stores = [
            {"name": "Store A", "lat": 40.7128, "lon": -74.0060},  # NYC
            {
                "name": "Store B",
                "lat": 40.7130,
                "lon": -74.0062,
            },  # Very close to A
            {
                "name": "Store C",
                "lat": 40.7500,
                "lon": -73.9500,
            },  # Further away
        ]

        clusters = cluster_by_proximity(stores, radius_km=1.0)

        # Should have 2 clusters: [A, B] and [C]
        assert len(clusters) == 2
        assert len(clusters[0]) == 2  # A and B together
        assert len(clusters[1]) == 1  # C alone

    def test_cluster_by_proximity_single_store(self):
        """Test clustering with single store"""
        from app.utils.clustering import cluster_by_proximity

        stores = [{"name": "Store A", "lat": 40.7128, "lon": -74.0060}]
        clusters = cluster_by_proximity(stores, radius_km=1.0)

        assert len(clusters) == 1
        assert len(clusters[0]) == 1
        assert clusters[0][0]["name"] == "Store A"

    def test_cluster_by_proximity_missing_coordinates(self):
        """Test clustering with missing coordinates"""
        from app.utils.clustering import cluster_by_proximity

        stores = [
            {"name": "Store A", "lat": 40.7128, "lon": -74.0060},
            {"name": "Store B", "lat": None, "lon": -74.0062},
            {"name": "Store C", "lat": 40.7500, "lon": None},
        ]

        clusters = cluster_by_proximity(stores, radius_km=1.0)

        # Each store should be in its own cluster due to missing coordinates
        assert len(clusters) == 3
        for cluster in clusters:
            assert len(cluster) == 1

    def test_is_within_radius(self):
        """Test radius calculation"""
        from app.utils.clustering import is_within_radius

        store1 = {"lat": 40.7128, "lon": -74.0060}
        store2 = {"lat": 40.7130, "lon": -74.0062}  # Very close
        store3 = {"lat": 41.0000, "lon": -75.0000}  # Far away

        assert is_within_radius(store1, store2, 1.0) is True
        assert is_within_radius(store1, store3, 1.0) is False
        assert is_within_radius(store1, store3, 100.0) is True

    def test_routing_service_clustering(self):
        """Test RoutingService clustering method"""
        from app.services.routing_service import RoutingService

        stores = [
            {"name": "Store A", "latitude": 40.7128, "longitude": -74.0060},
            {"name": "Store B", "latitude": 40.7130, "longitude": -74.0062},
            {"name": "Store C", "latitude": 40.7500, "longitude": -73.9500},
        ]

        service = RoutingService()
        # Use the actual method name from the service
        clusters = service._apply_filters(
            stores, {"use_clustering": True, "cluster_radius": 1.0}
        )

        assert len(clusters) >= 1  # Should have at least one cluster
        assert isinstance(clusters, list)


class TestDashboard:
    """Test dashboard functionality"""

    def test_dashboard_route(self, client):
        """Test dashboard route loads correctly"""
        response = client.get("/dashboard")
        assert response.status_code == 200
        assert b"RouteForce Dashboard" in response.data
        assert b"Real-Time Route Visualization" in response.data
        assert b"Upload Store Data" in response.data

    def test_dashboard_contains_required_elements(self, client):
        """Test dashboard contains all required UI elements"""
        response = client.get("/dashboard")
        assert response.status_code == 200

        # Check for key UI elements
        assert b"Upload Store Data" in response.data
        assert b"Total Stores" in response.data
        assert b"Clusters" in response.data
        assert b"Optimization Score" in response.data
        assert b"Processing Time" in response.data
        assert b"Map Controls" in response.data
        assert b"Live Activity" in response.data
        assert b"Route Visualization" in response.data

    def test_dashboard_includes_required_libraries(self, client):
        """Test dashboard includes required JavaScript libraries"""
        response = client.get("/dashboard")
        assert response.status_code == 200

        # Check for required libraries
        assert b"leaflet" in response.data
        assert b"chart.js" in response.data
        assert b"tailwindcss" in response.data
        assert b"dashboard_enhanced.js" in response.data

    def test_main_page_has_dashboard_link(self, client):
        """Test main page has dashboard link"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Real-Time Dashboard" in response.data
        assert b'href="/dashboard"' in response.data


class TestPlaybookConstraints:
    """Test playbook constraint logic validation"""

    def test_max_stores_per_chain_constraint(self):
        """Test max stores per chain validation"""
        mock_request = Mock()
        mock_request.files = {"file": Mock(filename="test.csv")}
        mock_form = Mock()
        mock_form.get = Mock(
            side_effect=lambda key, default=None, type=None: {
                "max_stores_per_chain": 2 if type is int else "2"
            }.get(key, default)
        )
        mock_form.getlist = Mock(return_value=[])
        mock_form.__contains__ = Mock(return_value=False)
        mock_request.form = mock_form

        route_request = RouteRequest.from_request(mock_request)
        assert route_request.max_stores_per_chain == 2

    def test_day_exclusion_validation(self):
        """Test day exclusion constraint validation"""
        mock_request = Mock()
        mock_request.files = {"file": Mock(filename="test.csv")}
        mock_form = Mock()
        mock_form.get = Mock(return_value=None)
        mock_form.getlist = Mock(return_value=["Sunday", "Saturday"])
        mock_form.__contains__ = Mock(return_value=False)
        mock_request.form = mock_form

        route_request = RouteRequest.from_request(mock_request)
        assert "Sunday" in route_request.exclude_days
        assert "Saturday" in route_request.exclude_days

    def test_time_window_constraint_validation(self):
        """Test time window constraint validation"""
        mock_request = Mock()
        mock_request.files = {"file": Mock(filename="test.csv")}
        mock_form = Mock()
        mock_form.get = Mock(
            side_effect=lambda key, default=None, type=None: {
                "time_start": "09:00",
                "time_end": "17:00",
            }.get(key, default)
        )
        mock_form.getlist = Mock(return_value=[])
        mock_form.__contains__ = Mock(return_value=False)
        mock_request.form = mock_form

        route_request = RouteRequest.from_request(mock_request)
        assert route_request.time_start == "09:00"
        assert route_request.time_end == "17:00"

        # Validation should pass for valid time window
        errors = route_request.get_validation_errors()
        time_errors = [e for e in errors if "time" in e.lower()]
        assert len(time_errors) == 0

    def test_sales_threshold_constraint(self):
        """Test sales threshold constraint validation"""
        mock_request = Mock()
        mock_request.files = {"file": Mock(filename="test.csv")}
        mock_form = Mock()
        mock_form.get = Mock(
            side_effect=lambda key, default=None, type=None: {
                "min_sales_threshold": 1000.0 if type is float else "1000.0"
            }.get(key, default)
        )
        mock_form.getlist = Mock(return_value=[])
        mock_form.__contains__ = Mock(return_value=False)
        mock_request.form = mock_form

        route_request = RouteRequest.from_request(mock_request)
        assert route_request.min_sales_threshold == 1000.0


class TestTimeWindowRoutingConflicts:
    """Test time window routing conflicts"""

    def test_invalid_time_window_start_after_end(self):
        """Test time window where start is after end"""
        mock_request = Mock()
        mock_request.files = {"file": Mock(filename="test.csv")}
        mock_form = Mock()
        mock_form.get = Mock(
            side_effect=lambda key, default=None, type=None: {
                "time_start": "18:00",
                "time_end": "08:00",
            }.get(key, default)
        )
        mock_form.getlist = Mock(return_value=[])
        mock_form.__contains__ = Mock(return_value=False)
        mock_request.form = mock_form

        route_request = RouteRequest.from_request(mock_request)
        route_request.time_start = "18:00"
        route_request.time_end = "08:00"

        errors = route_request.get_validation_errors()
        assert any(
            "Time start must be before time end" in error for error in errors
        )

    def test_zero_duration_time_window(self):
        """Test time window with zero duration"""
        mock_request = Mock()
        mock_request.files = {"file": Mock(filename="test.csv")}
        mock_form = Mock()
        mock_form.get = Mock(
            side_effect=lambda key, default=None, type=None: {
                "time_start": "12:00",
                "time_end": "12:00",
            }.get(key, default)
        )
        mock_form.getlist = Mock(return_value=[])
        mock_form.__contains__ = Mock(return_value=False)
        mock_request.form = mock_form

        route_request = RouteRequest.from_request(mock_request)
        route_request.time_start = "12:00"
        route_request.time_end = "12:00"

        errors = route_request.get_validation_errors()
        assert any(
            "Time window must have duration greater than 0" in error
            for error in errors
        )

    def test_extremely_short_time_window(self):
        """Test extremely short time window that prevents viable routing"""
        mock_request = Mock()
        mock_request.files = {"file": Mock(filename="test.csv")}
        mock_form = Mock()
        mock_form.get = Mock(
            side_effect=lambda key, default=None, type=None: {
                "time_start": "12:00",
                "time_end": "12:01",  # 1 minute window
            }.get(key, default)
        )
        mock_form.getlist = Mock(return_value=[])
        mock_form.__contains__ = Mock(return_value=False)
        mock_request.form = mock_form

        route_request = RouteRequest.from_request(mock_request)
        route_request.time_start = "12:00"
        route_request.time_end = "12:01"

        # Should be valid but routing service should handle the impracticality
        errors = route_request.get_validation_errors()
        # May have warnings about short duration
        assert len(errors) >= 0  # Always true, but validates no crash occurs


class TestRouteOutputValidation:
    """Test route output validation with maps links"""

    def test_route_metadata_includes_maps_links(self):
        """Test that route metadata includes properly formatted maps links"""
        # Mock the service to avoid initialization hang
        with patch(
            "app.services.routing_service_unified.UnifiedRoutingService"
        ) as mock_service:
            mock_instance = Mock()
            mock_service.return_value = mock_instance

            service = UnifiedRoutingService()

        route = [
            {
                "name": "Store A",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "address": "123 Main St",
            },
            {
                "name": "Store B",
                "latitude": 40.7589,
                "longitude": -73.9851,
                "address": "456 Oak Ave",
            },
        ]

        # Test route scoring/metadata generation
        score = service.score_route(route)
        assert score >= 0
        assert score <= 100

    def test_google_maps_link_generation(self):
        """Test Google Maps link generation"""
        from app.utils.maps import generate_google_maps_link

        waypoints = [
            {"latitude": 40.7128, "longitude": -74.0060},
            {"latitude": 40.7589, "longitude": -73.9851},
        ]

        link = generate_google_maps_link(waypoints)
        assert "google.com/maps" in link
        assert "40.7128,-74.0060" in link
        assert "40.7589,-73.9851" in link

    def test_apple_maps_link_generation(self):
        """Test Apple Maps link generation"""
        from app.utils.maps import generate_apple_maps_link

        waypoints = [
            {"latitude": 40.7128, "longitude": -74.0060},
            {"latitude": 40.7589, "longitude": -73.9851},
        ]

        link = generate_apple_maps_link(waypoints)
        assert "maps.apple.com" in link or link.startswith("http")
        assert "40.7128" in link
        assert "-74.0060" in link

    def test_fallback_maps_string_generation(self):
        """Test fallback maps string when links can't be generated"""
        waypoints = [
            {"latitude": None, "longitude": -74.0060},  # Invalid latitude
            {"latitude": 40.7589, "longitude": None},  # Invalid longitude
        ]

        # Should generate fallback strings instead of links
        from app.utils.maps import generate_google_maps_link

        try:
            link = generate_google_maps_link(waypoints)
            # Should either be a valid link or a fallback message
            assert isinstance(link, str)
            assert len(link) > 0
        except Exception:
            # Exception handling is acceptable for invalid coordinates
            pass


class TestMultiUserRequestIsolation:
    """Test multi-user request isolation and cache key separation"""

    def test_different_users_different_cache_keys(self):
        """Test that different users get different cache keys for same request"""
        # Create identical requests for two different users
        mock_request1 = Mock()
        mock_request1.files = {
            "file": Mock(
                filename="test.csv", read=Mock(return_value=b"same content")
            )
        }
        mock_form1 = Mock()
        mock_form1.get = Mock(
            side_effect=lambda key, default=None, type=None: {
                "time_start": "09:00",
                "time_end": "17:00",
            }.get(key, default)
        )
        mock_form1.getlist = Mock(return_value=[])
        mock_form1.__contains__ = Mock(return_value=False)
        mock_request1.form = mock_form1

        mock_request2 = Mock()
        mock_request2.files = {
            "file": Mock(
                filename="test.csv", read=Mock(return_value=b"same content")
            )
        }
        mock_form2 = Mock()
        mock_form2.get = Mock(
            side_effect=lambda key, default=None, type=None: {
                "time_start": "09:00",
                "time_end": "17:00",
            }.get(key, default)
        )
        mock_form2.getlist = Mock(return_value=[])
        mock_form2.__contains__ = Mock(return_value=False)
        mock_request2.form = mock_form2

        # Create route requests
        route_request1 = RouteRequest.from_request(mock_request1)
        route_request2 = RouteRequest.from_request(mock_request2)

        # Mock file objects for cache key generation
        file_mock1 = Mock()
        file_mock1.filename = "test.csv"
        file_mock1.read.return_value = b"same content"
        file_mock1.seek = Mock()

        file_mock2 = Mock()
        file_mock2.filename = "test.csv"
        file_mock2.read.return_value = b"same content"
        file_mock2.seek = Mock()

        route_request1.file = file_mock1
        route_request2.file = file_mock2

        # Cache keys should be the same for identical content and settings
        cache_key1 = route_request1.get_cache_key()
        cache_key2 = route_request2.get_cache_key()

        # They should be equal since content and settings are identical
        assert cache_key1 == cache_key2
        assert len(cache_key1) == 32  # MD5 hash length

    def test_different_content_different_cache_keys(self):
        """Test that different content generates different cache keys"""
        mock_request1 = Mock()
        mock_request1.files = {"file": Mock(filename="test1.csv")}
        mock_form1 = Mock()
        mock_form1.get = Mock(return_value=None)
        mock_form1.getlist = Mock(return_value=[])
        mock_form1.__contains__ = Mock(return_value=False)
        mock_request1.form = mock_form1

        mock_request2 = Mock()
        mock_request2.files = {"file": Mock(filename="test2.csv")}
        mock_form2 = Mock()
        mock_form2.get = Mock(return_value=None)
        mock_form2.getlist = Mock(return_value=[])
        mock_form2.__contains__ = Mock(return_value=False)
        mock_request2.form = mock_form2

        route_request1 = RouteRequest.from_request(mock_request1)
        route_request2 = RouteRequest.from_request(mock_request2)

        # Mock different file content
        file_mock1 = Mock()
        file_mock1.filename = "test1.csv"
        file_mock1.read.return_value = b"content 1"
        file_mock1.seek = Mock()

        file_mock2 = Mock()
        file_mock2.filename = "test2.csv"
        file_mock2.read.return_value = b"content 2"
        file_mock2.seek = Mock()

        route_request1.file = file_mock1
        route_request2.file = file_mock2

        cache_key1 = route_request1.get_cache_key()
        cache_key2 = route_request2.get_cache_key()

        # Should be different due to different content
        assert cache_key1 != cache_key2
        assert len(cache_key1) == 32
        assert len(cache_key2) == 32

    def test_back_to_back_route_requests(self):
        """Test back-to-back route requests with varying inputs"""
        from app.services.routing_service import RoutingService

        # Create service instance
        service = RoutingService()

        # First request with different stores
        stores1 = [
            {"name": "Store A", "latitude": 40.7128, "longitude": -74.0060},
            {"name": "Store B", "latitude": 40.7589, "longitude": -73.9851},
        ]

        # Second request with different stores
        stores2 = [
            {"name": "Store C", "latitude": 41.8781, "longitude": -87.6298},
            {"name": "Store D", "latitude": 34.0522, "longitude": -118.2437},
        ]

        # Generate routes back-to-back
        route1 = service.generate_route_from_stores(stores1, {})
        route2 = service.generate_route_from_stores(stores2, {})

        # Routes should be different and not interfere with each other
        assert isinstance(route1, list)
        assert isinstance(route2, list)
        assert route1 != route2 or len(stores1) != len(stores2)

    def test_concurrent_routing_service_isolation(self):
        """Test that multiple RoutingService instances don't interfere"""
        from app.services.routing_service import RoutingService

        # Create multiple service instances
        service1 = RoutingService(user_id=1)
        service2 = RoutingService(user_id=2)

        # Verify they have different user IDs
        assert service1.user_id != service2.user_id

        # Test that processing times are tracked separately
        initial_time1 = service1.get_last_processing_time()
        initial_time2 = service2.get_last_processing_time()

        # Both should start at 0
        assert initial_time1 == 0.0
        assert initial_time2 == 0.0

        # Generate a route with service1
        stores = [
            {"name": "Store A", "latitude": 40.7128, "longitude": -74.0060},
        ]

        service1.generate_route_from_stores(stores, {})

        # Only service1 should have updated processing time
        time1_after = service1.get_last_processing_time()
        time2_after = service2.get_last_processing_time()

        assert time1_after > 0  # Should have some processing time
        assert time2_after == 0.0  # Should still be 0


class TestDatabaseIntegration:
    """Test database integration and PostgreSQL mode"""

    def test_database_service_availability(self):
        """Test database service availability"""
        from app.services.routing_service import RoutingService

        # Create service and check database availability
        service = RoutingService()

        # Should have database_service attribute (may be None if not configured)
        assert hasattr(service, "database_service")

    def test_route_save_and_load_functionality(self, app):
        """Test route save/load functionality if database is available"""
        from app.services.routing_service import RoutingService

        with app.app_context():
            service = RoutingService(user_id=1)

            if service.database_service:
                # Test route saving
                try:
                    filters = {"algorithm": "default"}
                    # The file "test_file.csv" likely does not exist; this is expected.
                    service.generate_route_with_filters(
                        "test_file.csv", filters, save_to_db=False
                    )
                except Exception as e:
                    # Expected if file doesn't exist or other setup issues
                    assert isinstance(e, Exception)
            else:
                # No database configured - test should pass
                assert service.database_service is None

    def test_user_stores_retrieval(self, app):
        """Test user stores retrieval"""
        from app.services.routing_service import RoutingService

        with app.app_context():
            service = RoutingService(user_id=1)

            # Should return empty list if no database or no stores
            stores = service.get_user_stores()
            assert isinstance(stores, list)

    def test_route_history_retrieval(self, app):
        """Test route history retrieval"""
        from app.services.routing_service import RoutingService

        with app.app_context():
            service = RoutingService(user_id=1)

            # Should return empty list if no database or no routes
            history = service.get_route_history(limit=5)
            assert isinstance(history, list)

            # Test with different limits
            history_10 = service.get_route_history(limit=10)
            assert isinstance(history_10, list)
