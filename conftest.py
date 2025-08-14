"""
Test configuration for RouteForce Routing

Simplified configuration without retry logic that was causing issues.
"""

import pytest
import logging
import os
import tempfile
from app import create_app

# Set up basic logging
log_dir = "logs/2025-07-XX/"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, "test.log"), 
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@pytest.fixture
def app():
    """Create application for testing."""
    # Set environment variables for testing
    os.environ['RATE_LIMITS'] = '1000/minute;10000/hour'  # Very high limits for testing
    os.environ['FLASK_ENV'] = 'testing'
    
    # Create the app with test config
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'RATELIMIT_ENABLED': False,  # Disable rate limiting completely for tests
    })
    
    # Create temporary directory for file uploads
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    
    yield app
    
    # Cleanup
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        import shutil
        shutil.rmtree(app.config['UPLOAD_FOLDER'])

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()
