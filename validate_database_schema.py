"""
Simple database schema validation script
Tests basic functionality without complex pytest setup
"""

import os
import sys
import tempfile
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_schema():
    """Test database schema creation and basic functionality"""
    try:
        # Set testing environment
        os.environ['FLASK_ENV'] = 'testing'
        
        # Import after setting environment
        from app import create_app
        from app.models.database import db, User, Route, Store, RouteOptimization, Analytics
        
        # Create test app with SQLite
        app = create_app()
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///test_schema.db',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False
        })
        
        with app.app_context():
            print("🔧 Creating database tables...")
            db.create_all()
            
            print("✅ Testing User model...")
            # Test user creation
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
            
            assert user.id is not None
            assert user.check_password('testpassword')
            print(f"   User created with ID: {user.id}")
            
            print("✅ Testing Store model...")
            # Test store creation
            store = Store(
                name='Test Store',
                address='123 Test St',
                latitude=40.7128,
                longitude=-74.0060,
                chain='Test Chain',
                store_type='retail',
                priority=5,
                user_id=user.id
            )
            store.set_metadata({'hours': '9-5', 'phone': '555-1234'})
            db.session.add(store)
            db.session.commit()
            
            assert store.id is not None
            assert store.get_metadata()['hours'] == '9-5'
            print(f"   Store created with ID: {store.id}")
            
            print("✅ Testing Route model...")
            # Test route creation
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
                user_id=user.id
            )
            route.set_route_data(route_data)
            db.session.add(route)
            db.session.commit()
            
            assert route.id is not None
            assert route.get_route_data() == route_data
            print(f"   Route created with ID: {route.id}")
            
            print("✅ Testing RouteOptimization model...")
            # Test route optimization
            optimization = RouteOptimization(
                execution_time=2.5,
                algorithm='genetic_algorithm',
                improvement_score=15.2,
                original_distance=20.0,
                optimized_distance=17.0,
                stores_count=10,
                route_id=route.id,
                user_id=user.id
            )
            optimization.set_parameters({'population_size': 100, 'generations': 50})
            db.session.add(optimization)
            db.session.commit()
            
            assert optimization.id is not None
            assert optimization.get_parameters()['population_size'] == 100
            print(f"   Route optimization created with ID: {optimization.id}")
            
            print("✅ Testing Analytics model...")
            # Test analytics
            analytics = Analytics(
                event_type='route_generated',
                user_id=user.id,
                session_id='test_session_123',
                ip_address='192.168.1.1'
            )
            analytics.set_event_data({
                'route_id': route.id,
                'algorithm': 'nearest_neighbor',
                'execution_time': 1.5
            })
            db.session.add(analytics)
            db.session.commit()
            
            assert analytics.id is not None
            assert analytics.get_event_data()['route_id'] == route.id
            print(f"   Analytics record created with ID: {analytics.id}")
            
            print("✅ Testing relationships...")
            # Test relationships
            user_routes = user.routes
            assert len(user_routes) == 1
            assert user_routes[0].name == 'Test Route'
            
            user_stores = user.stores
            assert len(user_stores) == 1
            assert user_stores[0].name == 'Test Store'
            
            route_optimizations = route.optimizations
            assert len(route_optimizations) == 1
            assert route_optimizations[0].algorithm == 'genetic_algorithm'
            
            print("   All relationships working correctly")
            
            print("✅ Testing model serialization...")
            # Test to_dict methods
            user_dict = user.to_dict()
            assert 'id' in user_dict
            assert 'username' in user_dict
            assert 'password_hash' not in user_dict
            
            store_dict = store.to_dict()
            assert 'id' in store_dict
            assert 'store_metadata' in store_dict
            
            route_dict = route.to_dict()
            assert 'id' in route_dict
            assert 'route_data' in route_dict
            
            print("   Model serialization working correctly")
            
            print("\n🎉 All database schema tests passed!")
            print(f"📊 Database contains:")
            print(f"   - {db.session.query(User).count()} users")
            print(f"   - {db.session.query(Store).count()} stores")
            print(f"   - {db.session.query(Route).count()} routes")
            print(f"   - {db.session.query(RouteOptimization).count()} optimizations")
            print(f"   - {db.session.query(Analytics).count()} analytics records")
            
            # Clean up
            db.drop_all()
            
        # Remove test database file
        if os.path.exists('test_schema.db'):
            os.remove('test_schema.db')
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing database schema: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_database_schema()
    if success:
        print("\n✅ Database schema validation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Database schema validation failed!")
        sys.exit(1)