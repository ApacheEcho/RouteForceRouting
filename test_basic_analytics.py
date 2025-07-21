#!/usr/bin/env python3
"""
Simple Analytics Test - Tests basic functionality without authentication
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_analytics_endpoints():
    """Test analytics endpoints"""
    base_url = "http://localhost:5001"
    
    # Test basic server health
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            logger.info("✓ Server is healthy")
        else:
            logger.error(f"✗ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"✗ Cannot connect to server: {e}")
        return False
    
    # Test analytics demo endpoint (without auth)
    try:
        response = requests.get(f"{base_url}/api/ai/ensemble/status")
        logger.info(f"Ensemble status endpoint: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✓ Ensemble status: {result}")
        elif response.status_code == 401:
            logger.info("Authentication required for ensemble status")
        else:
            logger.info(f"Ensemble status response: {response.text}")
    except Exception as e:
        logger.error(f"Error testing ensemble status: {e}")
    
    # Test monitoring endpoints
    try:
        response = requests.get(f"{base_url}/api/v1/monitoring/metrics")
        logger.info(f"Monitoring metrics endpoint: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✓ Monitoring metrics available")
            logger.info(f"  CPU Usage: {result.get('cpu_usage', 'N/A')}")
            logger.info(f"  Memory Usage: {result.get('memory_usage', 'N/A')}")
        else:
            logger.info(f"Monitoring response: {response.text}")
    except Exception as e:
        logger.error(f"Error testing monitoring: {e}")
    
    # Test dashboard endpoints
    try:
        response = requests.get(f"{base_url}/dashboard/advanced-analytics")
        logger.info(f"Advanced dashboard endpoint: {response.status_code}")
        if response.status_code == 200:
            logger.info("✓ Advanced dashboard is accessible")
        else:
            logger.info(f"Dashboard response: {response.status_code}")
    except Exception as e:
        logger.error(f"Error testing dashboard: {e}")
    
    # Test basic route generation (this usually works without auth)
    try:
        test_data = {
            "stores": [
                {"id": "1", "name": "Store 1", "lat": 40.7128, "lon": -74.0060, "priority": 1},
                {"id": "2", "name": "Store 2", "lat": 40.7589, "lon": -73.9851, "priority": 2}
            ]
        }
        response = requests.post(f"{base_url}/api/v1/routes/generate", json=test_data)
        logger.info(f"Route generation endpoint: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            logger.info("✓ Route generation successful")
            logger.info(f"  Generated route with {len(result.get('route', []))} stops")
        else:
            logger.info(f"Route generation response: {response.text[:200]}")
    except Exception as e:
        logger.error(f"Error testing route generation: {e}")
    
    logger.info("\n🎯 Basic functionality test completed")
    return True

if __name__ == "__main__":
    test_analytics_endpoints()
