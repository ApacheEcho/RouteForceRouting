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
from app import create_app, db
from app.models.database import User
from flask_jwt_extended import create_access_token
from routing_engine import Store
import sys
from types import ModuleType
from urllib.parse import urlparse


# Ensure fast, network-free behavior in tests
os.environ.setdefault("ROUTEFORCE_TESTING", "1")

# Install a lightweight requests shim to route localhost calls to Flask test client
try:
    import requests as _real_requests  # noqa: F401
except Exception:
    _real_requests = None


_shim_app = None
_shim_client = None


def _ensure_client():
    global _shim_app, _shim_client
    if _shim_app is None or _shim_client is None:
        _shim_app = create_app("testing", testing=True)
        _shim_client = _shim_app.test_client()
    return _shim_client


def _flask_request(method: str, url: str, **kwargs):
    parsed = urlparse(url)
    if parsed.hostname in {"localhost", "127.0.0.1"}:
        client = _ensure_client()
        path = parsed.path or "/"
        headers = kwargs.get("headers") or {}
        json_data = kwargs.get("json")
        data = kwargs.get("data")

        if method == "GET":
            resp = client.get(path, headers=headers)
        elif method == "POST":
            if json_data is not None:
                resp = client.post(path, headers=headers, json=json_data)
            else:
                resp = client.post(path, headers=headers, data=data)
        elif method == "PUT":
            resp = client.put(path, headers=headers, json=json_data or data)
        elif method == "DELETE":
            resp = client.delete(path, headers=headers)
        else:
            return None

        class _Adapter:
            status_code = resp.status_code

            def json(self):
                try:
                    return resp.get_json()
                except Exception:
                    return None

            @property
            def text(self):
                try:
                    return resp.get_data(as_text=True)
                except Exception:
                    return ""

        return _Adapter()
    return None


class _RequestsProxy(ModuleType):
    def __init__(self, real_mod):
        super().__init__("requests")
        self._real = real_mod

    def __getattr__(self, name):
        return getattr(self._real, name)

    def get(self, url, **kwargs):
        resp = _flask_request("GET", url, **kwargs)
        return resp if resp is not None else self._real.get(url, **kwargs)

    def post(self, url, **kwargs):
        resp = _flask_request("POST", url, **kwargs)
        return resp if resp is not None else self._real.post(url, **kwargs)

    def put(self, url, **kwargs):
        resp = _flask_request("PUT", url, **kwargs)
        return resp if resp is not None else self._real.put(url, **kwargs)

    def delete(self, url, **kwargs):
        resp = _flask_request("DELETE", url, **kwargs)
        return resp if resp is not None else self._real.delete(url, **kwargs)


if "requests" in sys.modules:
    # Replace already-imported requests with proxy
    sys.modules["requests"] = _RequestsProxy(sys.modules["requests"])  # type: ignore[arg-type]
elif _real_requests is not None:
    sys.modules["requests"] = _RequestsProxy(_real_requests)

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


@pytest.fixture(scope='module')
def test_app():
    app = create_app(config_name="testing")
    with app.app_context():
        yield app


@pytest.fixture(scope='module')
def client(test_app):
    return test_app.test_client()


@pytest.fixture(scope='function')
def init_database(test_app):
    with test_app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def admin_user(init_database):
    user = User(username="adminuser", email="admin@test.com", role="admin")
    user.set_password("adminpass")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def regular_user(init_database):
    user = User(username="regularuser", email="user@test.com", role="user")
    user.set_password("userpass")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def admin_token(admin_user):
    return create_access_token(identity=admin_user.email)


@pytest.fixture(scope='function')
def user_token(regular_user):
    return create_access_token(identity=regular_user.email)


# Additional fixtures used by some multi-vehicle routing tests
@pytest.fixture
def large_store_dataset():
    stores = []
    store_templates = [
        {"chain": "CVS", "base_weight": 20, "base_packages": 4},
        {"chain": "WLG", "base_weight": 30, "base_packages": 6},
        {"chain": "RIT", "base_weight": 25, "base_packages": 5},
    ]

    coordinates = [
        {"lat": 40.7128, "lng": -74.0060},
        {"lat": 40.7589, "lng": -73.9851},
        {"lat": 40.7505, "lng": -73.9934},
        {"lat": 40.6892, "lng": -73.9442},
        {"lat": 40.7831, "lng": -73.9712},
        {"lat": 40.7282, "lng": -73.9442},
        {"lat": 40.7336, "lng": -73.9890},
        {"lat": 40.8621, "lng": -73.9036},
        {"lat": 40.6441, "lng": -74.0776},
        {"lat": 40.7048, "lng": -73.6501},
        {"lat": 40.7400, "lng": -73.9900},
        {"lat": 40.7614, "lng": -73.9776},
        {"lat": 40.7180, "lng": -74.0020},
        {"lat": 40.7295, "lng": -73.9965},
        {"lat": 40.7549, "lng": -73.9840},
    ]

    priorities = ["high", "medium", "low"] * 5
    delivery_windows = [
        "09:00-17:00",
        "10:00-16:00",
        "08:00-18:00",
        "11:00-15:00",
        "09:30-16:30",
    ] * 3

    for i in range(15):
        template = store_templates[i % 3]
        weight_variation = (-5 + (i % 11)) * 2
        package_variation = -2 + (i % 5)

        stores.append(
            Store(
                store_id=f"{template['chain']}_{i + 1:03d}",
                name=f"{template['chain']} Store #{i + 1}",
                address=f"{100 + i * 10} Test St, New York, NY 1000{i % 10}",
                coordinates=coordinates[i],
                delivery_window=delivery_windows[i],
                priority=priorities[i],
                estimated_service_time=10 + (i % 3) * 5,
                packages=max(1, template["base_packages"] + package_variation),
                weight_kg=max(5.0, template["base_weight"] + weight_variation),
                special_requirements={"signature_required": i % 2 == 0},
            )
        )

    return stores


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
