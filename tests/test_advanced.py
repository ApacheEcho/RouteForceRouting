"""
Comprehensive test suite for the modernized RouteForce Routing application
"""
import pytest
import os
import tempfile
import io
from unittest.mock import Mock, patch, MagicMock

from app import create_app
from app.services.routing_service import RoutingService
from app.services.file_service import FileService
from app.models.route_request import RouteRequest

@pytest.fixture
def app():
    """Create test application"""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
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
    return io.BytesIO(content.encode('utf-8'))

class TestRouteRequest:
    """Test RouteRequest model"""
    
    def test_route_request_validation(self):
        """Test route request validation"""
        # Mock Flask request
        mock_request = Mock()
        mock_request.files = {'file': Mock(filename='test.csv')}
        mock_form = Mock()
        mock_form.get = Mock(side_effect=lambda key, default=None, type=None: {
            'proximity': 'on',
            'time_start': '09:00',
            'time_end': '17:00',
            'max_stores_per_chain': 10 if type == int else '10',
            'min_sales_threshold': 1000.0 if type == float else '1000.0'
        }.get(key, default))
        mock_form.getlist = Mock(return_value=['Monday', 'Tuesday'])
        mock_form.__contains__ = Mock(side_effect=lambda key: key in ['proximity'])
        mock_request.form = mock_form
        
        route_request = RouteRequest.from_request(mock_request)
        
        assert route_request.proximity == True
        assert route_request.time_start == '09:00'
        assert route_request.time_end == '17:00'
        assert route_request.max_stores_per_chain == 10
        assert route_request.min_sales_threshold == 1000.0
        assert route_request.exclude_days == ['Monday', 'Tuesday']
    
    def test_route_request_invalid_time_window(self):
        """Test invalid time window validation"""
        mock_request = Mock()
        mock_request.files = {'file': Mock(filename='test.csv')}
        mock_form = Mock()
        mock_form.get = Mock(side_effect=lambda key, default=None, type=None: {
            'time_start': '17:00',
            'time_end': '09:00'
        }.get(key, default))
        mock_form.getlist = Mock(return_value=[])
        mock_form.__contains__ = Mock(return_value=False)
        mock_request.form = mock_form
        
        route_request = RouteRequest.from_request(mock_request)
        route_request.time_start = '17:00'
        route_request.time_end = '09:00'
        
        errors = route_request.get_validation_errors()
        assert any('Time start must be before time end' in error for error in errors)

class TestFileService:
    """Test FileService"""
    
    def test_file_validation(self):
        """Test file validation"""
        file_service = FileService()
        
        # Test valid file
        assert file_service._is_allowed_file('test.csv') == True
        assert file_service._is_allowed_file('test.xlsx') == True
        assert file_service._is_allowed_file('test.xls') == True
        
        # Test invalid file
        assert file_service._is_allowed_file('test.txt') == False
        assert file_service._is_allowed_file('test.pdf') == False
    
    def test_csv_loading(self, tmp_path):
        """Test CSV file loading"""
        file_service = FileService()
        
        # Create temporary CSV file
        csv_content = "name,chain\nStore A,Chain A\nStore B,Chain B"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        
        stores = file_service._load_csv_file(str(csv_file))
        
        assert len(stores) == 2
        assert stores[0]['name'] == 'Store A'
        assert stores[0]['chain'] == 'Chain A'
        assert stores[1]['name'] == 'Store B'
        assert stores[1]['chain'] == 'Chain B'
    
    def test_file_content_validation(self, tmp_path):
        """Test file content validation"""
        file_service = FileService()
        
        # Create valid CSV file
        csv_content = "name,chain\nStore A,Chain A\nStore B,Chain B"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        
        assert file_service.validate_file_content(str(csv_file)) == True
        
        # Create invalid CSV file (no name field)
        invalid_csv = "address,chain\n123 Main St,Chain A\n456 Oak Ave,Chain B"
        invalid_file = tmp_path / "invalid.csv"
        invalid_file.write_text(invalid_csv)
        
        assert file_service.validate_file_content(str(invalid_file)) == False

class TestRoutingService:
    """Test RoutingService"""
    
    def test_constraint_building(self):
        """Test constraint building from filters"""
        service = RoutingService()
        
        filters = {
            'proximity': True,
            'time_start': '09:00',
            'time_end': '17:00',
            'priority_only': True,
            'exclude_days': ['Sunday', 'Monday'],
            'max_stores_per_chain': 10,
            'min_sales_threshold': 1000.0
        }
        
        constraints = service._build_routing_constraints(filters)
        
        assert constraints['max_route_stops'] == 10
        assert '*' in constraints
        assert constraints['*']['time_window']['start'] == '09:00'
        assert constraints['*']['time_window']['end'] == '17:00'
        assert constraints['*']['priority_only'] == True
        assert 'Tuesday' in constraints['*']['days_allowed']
        assert 'Sunday' not in constraints['*']['days_allowed']
    
    def test_distance_calculation(self):
        """Test distance calculation"""
        service = RoutingService()
        
        route = [
            {'latitude': 40.7128, 'longitude': -74.0060},  # NYC
            {'latitude': 40.7589, 'longitude': -73.9851},  # Times Square
        ]
        
        distance = service._calculate_total_distance(route)
        assert distance > 0
        assert distance < 100  # Should be less than 100km
    
    def test_optimization_score(self):
        """Test optimization score calculation"""
        service = RoutingService()
        
        # Good route (short distance, many stops)
        good_route = [
            {'latitude': 40.7128, 'longitude': -74.0060},
            {'latitude': 40.7129, 'longitude': -74.0061},
            {'latitude': 40.7130, 'longitude': -74.0062},
        ]
        
        score = service._calculate_optimization_score(good_route)
        assert score > 0

class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'RouteForce Routing'
    
    def test_api_health_endpoint(self, client):
        """Test API health check endpoint"""
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'endpoints' in data
    
    def test_api_create_route(self, client):
        """Test API route creation"""
        payload = {
            'stores': [
                {'name': 'Store A', 'chain': 'Chain A'},
                {'name': 'Store B', 'chain': 'Chain B'}
            ],
            'constraints': {},
            'options': {}
        }
        
        response = client.post('/api/v1/routes', json=payload)
        assert response.status_code == 201
        
        data = response.get_json()
        assert 'route' in data
        assert 'metadata' in data
    
    def test_api_invalid_request(self, client):
        """Test API with invalid request"""
        response = client.post('/api/v1/routes', json={})
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
    
    def test_api_clusters_endpoint(self, client):
        """Test API clusters endpoint"""
        test_data = {
            'stores': [
                {'name': 'Store A', 'latitude': 40.7128, 'longitude': -74.0060},
                {'name': 'Store B', 'latitude': 40.7130, 'longitude': -74.0062},
                {'name': 'Store C', 'latitude': 40.7500, 'longitude': -73.9500},
            ],
            'radius_km': 1.0
        }
        
        response = client.post('/api/v1/clusters', json=test_data)
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'clusters' in data
        assert 'cluster_count' in data
        assert 'total_stores' in data
        assert data['cluster_count'] == 2
        assert data['total_stores'] == 3
    
    def test_api_clusters_invalid_data(self, client):
        """Test API clusters with invalid data"""
        # Missing stores
        response = client.post('/api/v1/clusters', json={})
        assert response.status_code == 400
        
        # Invalid radius
        response = client.post('/api/v1/clusters', json={
            'stores': [{'name': 'Store A', 'latitude': 40.7128, 'longitude': -74.0060}],
            'radius_km': -1.0
        })
        assert response.status_code == 400
        
        # Missing coordinates
        response = client.post('/api/v1/clusters', json={
            'stores': [{'name': 'Store A'}],
            'radius_km': 1.0
        })
        assert response.status_code == 400

class TestMainRoutes:
    """Test main application routes"""
    
    def test_index_route(self, client):
        """Test main index route"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'RouteForce Routing' in response.data
    
    def test_generate_route_with_file(self, client, sample_csv_file):
        """Test route generation with file upload"""
        data = {
            'file': (sample_csv_file, 'test.csv'),
            'proximity': '1',
            'time_start': '09:00',
            'time_end': '17:00'
        }
        
        with patch('app.services.file_service.FileService.validate_file_content', return_value=True):
            with patch('app.services.routing_service.RoutingService.generate_route_with_filters', return_value=[]):
                response = client.post('/generate', data=data, content_type='multipart/form-data')
                assert response.status_code == 200
    
    def test_generate_route_no_file(self, client):
        """Test route generation without file"""
        response = client.post('/generate', data={}, content_type='multipart/form-data')
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data

class TestErrorHandling:
    """Test error handling"""
    
    def test_404_error(self, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['error'] == 'Resource not found'
    
    def test_file_too_large(self, client):
        """Test file size limit"""
        # Create large file content
        large_content = "x" * (20 * 1024 * 1024)  # 20MB
        large_file = io.BytesIO(large_content.encode('utf-8'))
        
        data = {'file': (large_file, 'large.csv')}
        
        response = client.post('/generate', data=data, content_type='multipart/form-data')
        assert response.status_code == 413

class TestCaching:
    """Test caching functionality"""
    
    def test_cache_key_generation(self, sample_csv_file):
        """Test cache key generation"""
        mock_request = Mock()
        mock_request.files = {'file': Mock(filename='test.csv', read=Mock(return_value=b'test content'))}
        mock_form = Mock()
        mock_form.get = Mock(return_value=None)
        mock_form.getlist = Mock(return_value=[])
        mock_form.__contains__ = Mock(return_value=False)
        mock_request.form = mock_form
        
        # Mock the file object
        file_mock = Mock()
        file_mock.filename = 'test.csv'
        file_mock.read.return_value = b'test content'
        file_mock.seek = Mock()
        
        route_request = RouteRequest.from_request(mock_request)
        route_request.file = file_mock
        
        cache_key = route_request.get_cache_key()
        assert len(cache_key) == 32  # MD5 hash length
        assert cache_key != ''

class TestProximityClustering:
    """Test proximity clustering functionality"""
    
    def test_cluster_by_proximity_basic(self):
        """Test basic proximity clustering"""
        from app.services.routing_service import cluster_by_proximity
        
        stores = [
            {'name': 'Store A', 'lat': 40.7128, 'lon': -74.0060},  # NYC
            {'name': 'Store B', 'lat': 40.7130, 'lon': -74.0062},  # Very close to A
            {'name': 'Store C', 'lat': 40.7500, 'lon': -73.9500},  # Further away
        ]
        
        clusters = cluster_by_proximity(stores, radius_km=1.0)
        
        # Should have 2 clusters: [A, B] and [C]
        assert len(clusters) == 2
        assert len(clusters[0]) == 2  # A and B together
        assert len(clusters[1]) == 1  # C alone
    
    def test_cluster_by_proximity_single_store(self):
        """Test clustering with single store"""
        from app.services.routing_service import cluster_by_proximity
        
        stores = [{'name': 'Store A', 'lat': 40.7128, 'lon': -74.0060}]
        clusters = cluster_by_proximity(stores, radius_km=1.0)
        
        assert len(clusters) == 1
        assert len(clusters[0]) == 1
        assert clusters[0][0]['name'] == 'Store A'
    
    def test_cluster_by_proximity_missing_coordinates(self):
        """Test clustering with missing coordinates"""
        from app.services.routing_service import cluster_by_proximity
        
        stores = [
            {'name': 'Store A', 'lat': 40.7128, 'lon': -74.0060},
            {'name': 'Store B', 'lat': None, 'lon': -74.0062},
            {'name': 'Store C', 'lat': 40.7500, 'lon': None},
        ]
        
        clusters = cluster_by_proximity(stores, radius_km=1.0)
        
        # Each store should be in its own cluster due to missing coordinates
        assert len(clusters) == 3
        for cluster in clusters:
            assert len(cluster) == 1
    
    def test_is_within_radius(self):
        """Test radius calculation"""
        from app.services.routing_service import is_within_radius
        
        store1 = {'lat': 40.7128, 'lon': -74.0060}
        store2 = {'lat': 40.7130, 'lon': -74.0062}  # Very close
        store3 = {'lat': 41.0000, 'lon': -75.0000}  # Far away
        
        assert is_within_radius(store1, store2, 1.0) is True
        assert is_within_radius(store1, store3, 1.0) is False
        assert is_within_radius(store1, store3, 100.0) is True
    
    def test_routing_service_clustering(self):
        """Test RoutingService clustering method"""
        from app.services.routing_service import RoutingService
        
        stores = [
            {'name': 'Store A', 'latitude': 40.7128, 'longitude': -74.0060},
            {'name': 'Store B', 'latitude': 40.7130, 'longitude': -74.0062},
            {'name': 'Store C', 'latitude': 40.7500, 'longitude': -73.9500},
        ]
        
        service = RoutingService()
        clusters = service.cluster_stores_by_proximity(stores, radius_km=1.0)
        
        assert len(clusters) == 2
        assert len(clusters[0]) == 2
        assert len(clusters[1]) == 1

class TestDashboard:
    """Test dashboard functionality"""
    
    def test_dashboard_route(self, client):
        """Test dashboard route loads correctly"""
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'RouteForce Dashboard' in response.data
        assert b'Real-Time Route Visualization' in response.data
        assert b'Upload Store Data' in response.data
    
    def test_dashboard_contains_required_elements(self, client):
        """Test dashboard contains all required UI elements"""
        response = client.get('/dashboard')
        assert response.status_code == 200
        
        # Check for key UI elements
        assert b'Upload Store Data' in response.data
        assert b'Total Stores' in response.data
        assert b'Clusters' in response.data
        assert b'Optimization Score' in response.data
        assert b'Processing Time' in response.data
        assert b'Map Controls' in response.data
        assert b'Live Activity' in response.data
        assert b'Route Visualization' in response.data
    
    def test_dashboard_includes_required_libraries(self, client):
        """Test dashboard includes required JavaScript libraries"""
        response = client.get('/dashboard')
        assert response.status_code == 200
        
        # Check for required libraries
        assert b'leaflet' in response.data
        assert b'chart.js' in response.data
        assert b'tailwindcss' in response.data
        assert b'dashboard_enhanced.js' in response.data
    
    def test_main_page_has_dashboard_link(self, client):
        """Test main page has dashboard link"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Real-Time Dashboard' in response.data
        assert b'href="/dashboard"' in response.data

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
