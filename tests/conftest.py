"""
Test configuration and fixtures for RouteForce Routing

This module provides common test fixtures and configuration
for comprehensive test coverage analysis with CodeCov.
"""

import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))


@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture providing test data directory path."""
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def temp_dir():
    """Fixture providing a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_locations():
    """Fixture providing sample location data for routing tests."""
    return [
        {"lat": 37.7749, "lng": -122.4194, "name": "San Francisco"},
        {"lat": 34.0522, "lng": -118.2437, "name": "Los Angeles"},
        {"lat": 32.7157, "lng": -117.1611, "name": "San Diego"},
        {"lat": 37.3382, "lng": -121.8863, "name": "San Jose"},
        {"lat": 38.5816, "lng": -121.4944, "name": "Sacramento"},
    ]


@pytest.fixture
def sample_distance_matrix():
    """Fixture providing sample distance matrix for algorithm tests."""
    return [
        [0, 100, 200, 50, 150],
        [100, 0, 120, 80, 180],
        [200, 120, 0, 170, 300],
        [50, 80, 170, 0, 130],
        [150, 180, 300, 130, 0],
    ]


@pytest.fixture
def mock_flask_app():
    """Fixture providing a mock Flask application for API tests."""
    try:
        from flask import Flask

        app = Flask(__name__)
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test-secret-key"
        return app
    except ImportError:
        pytest.skip("Flask not available for testing")


@pytest.fixture
def api_client(mock_flask_app):
    """Fixture providing a test client for API testing."""
    return mock_flask_app.test_client()


# Performance test fixtures
@pytest.fixture
def performance_test_data():
    """Fixture providing larger datasets for performance testing."""
    import random

    random.seed(42)  # Reproducible results

    # Generate 100 random locations
    locations = []
    for i in range(100):
        locations.append(
            {
                "lat": random.uniform(32.0, 42.0),  # Roughly California bounds
                "lng": random.uniform(-124.0, -114.0),
                "name": f"Location_{i}",
            }
        )

    return locations


# Coverage helper functions
def get_test_coverage_targets():
    """Return list of modules that should be covered by tests."""
    return [
        "app.algorithms",
        "app.routes",
        "app.services",
        "app.monitoring",
        "app.optimization",
    ]


# Test markers for coverage categorization
pytest_plugins = []


def pytest_configure(config):
    """Configure pytest with custom markers for coverage analysis."""
    config.addinivalue_line(
        "markers", "unit: Unit test for specific functionality"
    )
    config.addinivalue_line(
        "markers", "integration: Integration test across components"
    )
    config.addinivalue_line(
        "markers", "algorithm: Algorithm-specific test cases"
    )
    config.addinivalue_line("markers", "api: API endpoint testing")
    config.addinivalue_line(
        "markers", "monitoring: Monitoring and analytics tests"
    )
    config.addinivalue_line(
        "markers", "performance: Performance benchmark tests"
    )
    config.addinivalue_line("markers", "slow: Slow-running tests")
    config.addinivalue_line(
        "markers", "external: Tests requiring external services"
    )


# Coverage reporting hooks
def pytest_sessionstart(session):
    """Hook called at test session start."""
    print(
        "\n🧪 Starting RouteForce Routing test session with coverage analysis"
    )


def pytest_sessionfinish(session, exitstatus):
    """Hook called at test session end."""
    print(f"\n📊 Test session completed with exit status: {exitstatus}")
    print("Coverage reports generated - check htmlcov/ directory")


# Custom collection for better coverage
def pytest_collection_modifyitems(config, items):
    """Modify collected test items for better coverage analysis."""
    for item in items:
        # Add appropriate markers based on test location
        if "algorithm" in str(item.fspath):
            item.add_marker(pytest.mark.algorithm)
        if "api" in str(item.fspath) or "route" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        if "monitoring" in str(item.fspath):
            item.add_marker(pytest.mark.monitoring)
        if "performance" in item.name or "benchmark" in item.name:
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
