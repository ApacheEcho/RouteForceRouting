import pytest
import logging
import os
from app import create_app

# Configure basic logging for tests
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@pytest.fixture
def app():
    """Create application for testing."""
    # Set test environment variables
    os.environ.update({
        'FLASK_ENV': 'testing',
        'DATABASE_URL': 'sqlite:///:memory:',
        'REDIS_URL': '',  # Disable Redis for testing
        'SECRET_KEY': 'test-secret-key',
        'JWT_SECRET_KEY': 'test-jwt-secret',
        'TESTING': 'True'
    })
    
    app = create_app('testing')
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "DATABASE_URL": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret-key",
        "JWT_SECRET_KEY": "test-jwt-secret",
        "CACHE_TYPE": "SimpleCache",  # Use simple cache instead of Redis
        "RATELIMIT_STORAGE_URL": "memory://",  # Use memory instead of Redis
    })
    
    with app.app_context():
        # Initialize any database tables if needed
        try:
            from app.models.database import db
            db.create_all()
        except ImportError:
            # Database models not available, skip
            pass
        
        yield app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()
