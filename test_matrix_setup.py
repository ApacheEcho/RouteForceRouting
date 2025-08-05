#!/usr/bin/env python3
"""
Test script that validates our matrix testing setup.
This mimics the type of tests that would run in our CI matrix.
"""

import pytest
import platform
import sys
import os

def test_platform_info():
    """Test that reports platform information."""
    print(f"Running on: {platform.system()} {platform.release()}")
    print(f"Python version: {sys.version}")
    assert platform.system() in ["Linux", "Windows", "Darwin"], f"Unsupported platform: {platform.system()}"

def test_python_version_support():
    """Test that Python version is supported."""
    version_info = sys.version_info
    supported_versions = [(3, 10), (3, 11), (3, 12)]
    current_version = (version_info.major, version_info.minor)
    assert current_version in supported_versions, f"Python {current_version} not in supported versions {supported_versions}"

def test_core_dependencies():
    """Test that core dependencies can be imported."""
    try:
        import numpy
        import pandas
        import flask
        import sklearn
        assert True, "Core dependencies imported successfully"
    except ImportError as e:
        pytest.fail(f"Failed to import core dependency: {e}")

def test_routing_module():
    """Test that our routing module works."""
    try:
        # Add the project root to Python path
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from routing.route_logger import log_route_score
        assert callable(log_route_score), "log_route_score should be callable"
    except ImportError as e:
        pytest.fail(f"Failed to import routing module: {e}")

@pytest.mark.skipif(
    os.environ.get("SKIP_DB_TESTS") == "true",
    reason="Database tests skipped on non-Linux platforms"
)
def test_database_dependent_feature():
    """Test that would require database (skipped on Windows/macOS)."""
    # This would be skipped on Windows/macOS in our matrix
    print("This test requires database services (PostgreSQL/Redis)")
    assert True, "Database test placeholder"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])