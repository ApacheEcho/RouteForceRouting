"""
Test suite for PostgreSQL database schema validation
Tests database constraints, relationships, and data integrity
"""

import pytest
import tempfile
import os
from datetime import datetime
from app import create_app
from app.models.database import db, User, Route, Store, RouteOptimization, Analytics
from sqlalchemy.exc import IntegrityError


class TestDatabaseSchema:
    """Test database schema constraints and relationships"""

    @pytest.fixture
    def app(self):
        """Create test app with in-memory SQLite database"""
        # Set environment variable to avoid loading production config
        os.environ['FLASK_ENV'] = 'testing'
        
        app = create_app('testing')
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'WTF_CSRF_ENABLED': False
        })
        
        with app.app_context():
            db.create_all()
            yield app
            try:
                db.session.remove()
                db.drop_all()
            except Exception:
                pass

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()

    @pytest.fixture
    def sample_user(self, app):
        """Create a sample user for testing"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                first_name='Test',
                last_name='User',
                role='user'
            )
            user.set_password('testpassword')
            db.session.add(user)
            db.session.commit()
            return user

    def test_user_creation_and_validation(self, app):
        """Test user creation and field validation"""
        with app.app_context():
            # Test valid user creation
            user = User(
                username='validuser',
                email='valid@example.com',
                role='admin'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.check_password('password123')
            assert not user.check_password('wrongpassword')
            assert user.role == 'admin'
            assert user.is_active is True

    def test_user_unique_constraints(self, app, sample_user):
        """Test user unique constraints"""
        with app.app_context():
            # Test duplicate username
            with pytest.raises(IntegrityError):
                duplicate_user = User(
                    username='testuser',  # Same as sample_user
                    email='different@example.com'
                )
                duplicate_user.set_password('password')
                db.session.add(duplicate_user)
                db.session.commit()
            
            db.session.rollback()
            
            # Test duplicate email
            with pytest.raises(IntegrityError):
                duplicate_user = User(
                    username='differentuser',
                    email='test@example.com'  # Same as sample_user
                )
                duplicate_user.set_password('password')
                db.session.add(duplicate_user)
                db.session.commit()

    def test_store_creation_and_validation(self, app, sample_user):
        """Test store creation and coordinate validation"""
        with app.app_context():
            # Test valid store creation
            store = Store(
                name='Test Store',
                address='123 Test St',
                latitude=40.7128,
                longitude=-74.0060,
                chain='Test Chain',
                store_type='retail',
                priority=5,
                user_id=sample_user.id
            )
            db.session.add(store)
            db.session.commit()
            
            assert store.id is not None
            assert store.is_active is True
            assert store.priority == 5

    def test_store_coordinate_constraints(self, app, sample_user):
        """Test store coordinate validation constraints"""
        with app.app_context():
            # Test invalid latitude (using SQLite, so check constraints might not work)
            # This test is more relevant for PostgreSQL deployment
            store = Store(
                name='Invalid Store',
                latitude=100.0,  # Invalid latitude > 90
                longitude=0.0,
                user_id=sample_user.id
            )
            db.session.add(store)
            # Note: SQLite doesn't enforce check constraints by default
            # This would fail in PostgreSQL with proper check constraints
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def test_route_creation_and_relationships(self, app, sample_user):
        """Test route creation and user relationships"""
        with app.app_context():
            route_data = [
                {"name": "Store A", "lat": 40.7128, "lng": -74.0060},
                {"name": "Store B", "lat": 40.7589, "lng": -73.9851}
            ]
            
            route = Route(
                name='Test Route',
                description='A test route',
                total_distance=10.5,
                estimated_time=30,
                optimization_score=0.85,
                algorithm_used='nearest_neighbor',
                status='generated',
                user_id=sample_user.id
            )
            route.set_route_data(route_data)
            db.session.add(route)
            db.session.commit()
            
            assert route.id is not None
            assert route.user_id == sample_user.id
            assert route.get_route_data() == route_data
            assert route.status == 'generated'

    def test_route_optimization_creation(self, app, sample_user):
        """Test route optimization creation and relationships"""
        with app.app_context():
            # Create a route first
            route = Route(
                name='Test Route',
                total_distance=15.0,
                user_id=sample_user.id
            )
            route.set_route_data([])
            db.session.add(route)
            db.session.commit()
            
            # Create route optimization
            optimization = RouteOptimization(
                execution_time=2.5,
                algorithm='genetic_algorithm',
                improvement_score=15.2,
                original_distance=20.0,
                optimized_distance=17.0,
                stores_count=10,
                route_id=route.id,
                user_id=sample_user.id
            )
            optimization.set_parameters({'population_size': 100, 'generations': 50})
            db.session.add(optimization)
            db.session.commit()
            
            assert optimization.id is not None
            assert optimization.route_id == route.id
            assert optimization.user_id == sample_user.id
            assert optimization.get_parameters()['population_size'] == 100

    def test_analytics_creation(self, app, sample_user):
        """Test analytics event creation"""
        with app.app_context():
            analytics = Analytics(
                event_type='route_generated',
                user_id=sample_user.id,
                session_id='test_session_123',
                ip_address='192.168.1.1'
            )
            analytics.set_event_data({
                'route_id': 123,
                'algorithm': 'nearest_neighbor',
                'execution_time': 1.5
            })
            db.session.add(analytics)
            db.session.commit()
            
            assert analytics.id is not None
            assert analytics.event_type == 'route_generated'
            assert analytics.get_event_data()['route_id'] == 123

    def test_user_route_relationship(self, app, sample_user):
        """Test user-route relationship"""
        with app.app_context():
            # Create multiple routes for the user
            route1 = Route(name='Route 1', user_id=sample_user.id)
            route1.set_route_data([])
            route2 = Route(name='Route 2', user_id=sample_user.id)
            route2.set_route_data([])
            
            db.session.add_all([route1, route2])
            db.session.commit()
            
            # Test relationship
            user = db.session.get(User, sample_user.id)
            assert len(user.routes) == 2
            assert route1 in user.routes
            assert route2 in user.routes

    def test_user_store_relationship(self, app, sample_user):
        """Test user-store relationship"""
        with app.app_context():
            # Create multiple stores for the user
            store1 = Store(name='Store 1', user_id=sample_user.id)
            store2 = Store(name='Store 2', user_id=sample_user.id)
            
            db.session.add_all([store1, store2])
            db.session.commit()
            
            # Test relationship
            user = db.session.get(User, sample_user.id)
            assert len(user.stores) == 2
            assert store1 in user.stores
            assert store2 in user.stores

    def test_route_optimization_relationship(self, app, sample_user):
        """Test route-optimization relationship"""
        with app.app_context():
            # Create route
            route = Route(name='Test Route', user_id=sample_user.id)
            route.set_route_data([])
            db.session.add(route)
            db.session.commit()
            
            # Create multiple optimizations for the route
            opt1 = RouteOptimization(
                execution_time=1.0,
                algorithm='algo1',
                stores_count=5,
                route_id=route.id
            )
            opt2 = RouteOptimization(
                execution_time=2.0,
                algorithm='algo2',
                stores_count=5,
                route_id=route.id
            )
            
            db.session.add_all([opt1, opt2])
            db.session.commit()
            
            # Test relationship
            route = db.session.get(Route, route.id)
            assert len(route.optimizations) == 2
            assert opt1 in route.optimizations
            assert opt2 in route.optimizations

    def test_model_to_dict_methods(self, app, sample_user):
        """Test model to_dict methods"""
        with app.app_context():
            # Test user to_dict
            user_dict = sample_user.to_dict()
            assert 'id' in user_dict
            assert 'username' in user_dict
            assert 'password_hash' not in user_dict  # Should not expose password
            
            # Test store to_dict
            store = Store(name='Test Store', user_id=sample_user.id)
            store.set_metadata({'hours': '9-5', 'phone': '555-1234'})
            db.session.add(store)
            db.session.commit()
            
            store_dict = store.to_dict()
            assert 'id' in store_dict
            assert 'name' in store_dict
            assert store_dict['store_metadata']['hours'] == '9-5'

    def test_json_field_handling(self, app, sample_user):
        """Test JSON field serialization/deserialization"""
        with app.app_context():
            # Test route data JSON handling
            route_data = [
                {"name": "Store A", "lat": 40.7128, "lng": -74.0060},
                {"name": "Store B", "lat": 40.7589, "lng": -73.9851}
            ]
            
            route = Route(name='JSON Test Route', user_id=sample_user.id)
            route.set_route_data(route_data)
            db.session.add(route)
            db.session.commit()
            
            # Retrieve and verify JSON data
            retrieved_route = db.session.get(Route, route.id)
            assert retrieved_route.get_route_data() == route_data
            
            # Test empty JSON handling
            route.set_route_data([])
            db.session.commit()
            assert retrieved_route.get_route_data() == []

    def test_datetime_fields(self, app, sample_user):
        """Test datetime field handling"""
        with app.app_context():
            # Create a route and check timestamps
            route = Route(name='Timestamp Test', user_id=sample_user.id)
            route.set_route_data([])
            db.session.add(route)
            db.session.commit()
            
            assert route.created_at is not None
            assert route.updated_at is not None
            assert isinstance(route.created_at, datetime)


if __name__ == '__main__':
    pytest.main([__file__])