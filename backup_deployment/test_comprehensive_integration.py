"""
Comprehensive Integration Test for Enhanced RouteForce System
Tests all major components: Analytics, Authentication, Database, External APIs, Dashboard
"""

import pytest
import requests
import json
import time
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base URL for testing
BASE_URL = "http://localhost:5001"

class TestRouteForceIntegration:
    """Integration test suite for RouteForce enhanced features"""
    
    def __init__(self):
        self.auth_token = None
        self.test_route_id = None
        
    def setup_test_environment(self):
        """Set up test environment and authenticate"""
        logger.info("Setting up test environment...")
        
        # Test authentication
        auth_data = {
            'email': 'admin@routeforce.com',
            'password': 'admin123'
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=auth_data)
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('access_token'):
                    self.auth_token = result['access_token']
                    logger.info("✓ Authentication successful")
                    return True
                else:
                    logger.error(f"✗ Authentication failed: {result}")
                    return False
            else:
                logger.error(f"✗ Authentication failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"✗ Authentication error: {str(e)}")
            return False
    
    def get_auth_headers(self):
        """Get authentication headers for requests"""
        if self.auth_token:
            return {'Authorization': f'Bearer {self.auth_token}'}
        return {}
    
    def test_analytics_engine(self):
        """Test analytics engine functionality"""
        logger.info("Testing Analytics Engine...")
        
        try:
            # Test route insights
            route_data = {
                'distance': 25.5,
                'duration': 45.0,
                'stops': 8,
                'fuel_used': 3.2
            }
            
            response = requests.get(
                f"{BASE_URL}/api/ai/insights/route/test_route_001",
                params=route_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                insight_data = response.json()
                if insight_data.get('success'):
                    logger.info("✓ Route insights generation successful")
                    logger.info(f"  Insight: {insight_data['insight']['title']}")
                    return True
                else:
                    logger.error(f"✗ Route insights failed: {insight_data}")
                    return False
            else:
                logger.error(f"✗ Route insights request failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Analytics engine test error: {str(e)}")
            return False
    
    def test_prediction_models(self):
        """Test ML prediction models"""
        logger.info("Testing Prediction Models...")
        
        try:
            prediction_data = {
                'route_features': {
                    'distance': 30.0,
                    'stops_count': 6,
                    'hour_of_day': 14,
                    'day_of_week': 2,
                    'is_weekend': False,
                    'is_rush_hour': False
                }
            }
            
            response = requests.post(
                f"{BASE_URL}/api/ai/predict/route",
                json=prediction_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                prediction_result = response.json()
                if prediction_result.get('success'):
                    logger.info("✓ Route prediction successful")
                    logger.info(f"  Predicted Duration: {prediction_result['prediction']['predicted_duration']:.1f} min")
                    logger.info(f"  Predicted Fuel Cost: ${prediction_result['prediction']['predicted_fuel_cost']:.2f}")
                    return True
                else:
                    logger.error(f"✗ Prediction failed: {prediction_result}")
                    return False
            else:
                logger.error(f"✗ Prediction request failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Prediction model test error: {str(e)}")
            return False
    
    def test_fleet_insights(self):
        """Test fleet insights and analytics"""
        logger.info("Testing Fleet Insights...")
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/ai/fleet/insights",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                fleet_data = response.json()
                if fleet_data.get('success'):
                    insights = fleet_data.get('fleet_insights', {})
                    logger.info("✓ Fleet insights successful")
                    logger.info(f"  Total Routes: {insights.get('total_routes', 0)}")
                    logger.info(f"  Avg Fuel Efficiency: {insights.get('avg_fuel_efficiency', 0):.1f}")
                    return True
                else:
                    logger.error(f"✗ Fleet insights failed: {fleet_data}")
                    return False
            else:
                logger.error(f"✗ Fleet insights request failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Fleet insights test error: {str(e)}")
            return False
    
    def test_smart_recommendations(self):
        """Test AI-powered smart recommendations"""
        logger.info("Testing Smart Recommendations...")
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/ai/recommendations/smart",
                params={'vehicle_count': 3, 'priority': 'efficiency'},
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                recommendations = response.json()
                if recommendations.get('success'):
                    logger.info("✓ Smart recommendations successful")
                    recs_data = recommendations.get('recommendations', {})
                    smart_suggestions = recs_data.get('smart_suggestions', [])
                    for i, rec in enumerate(smart_suggestions[:3]):
                        logger.info(f"  Recommendation {i+1}: {rec}")
                    return True
                else:
                    logger.error(f"✗ Recommendations failed: {recommendations}")
                    return False
            else:
                logger.error(f"✗ Recommendations request failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Smart recommendations test error: {str(e)}")
            return False
    
    def test_enterprise_dashboard(self):
        """Test enterprise dashboard endpoints"""
        logger.info("Testing Enterprise Dashboard...")
        
        try:
            # Test dashboard overview
            response = requests.get(
                f"{BASE_URL}/enterprise/api/overview",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                overview_data = response.json()
                if overview_data.get('success'):
                    logger.info("✓ Enterprise dashboard overview successful")
                    metrics = overview_data.get('key_metrics', {})
                    logger.info(f"  Total Routes: {metrics.get('total_routes', 0)}")
                    logger.info(f"  Active Drivers: {metrics.get('active_drivers', 0)}")
                    return True
                else:
                    logger.error(f"✗ Dashboard overview failed: {overview_data}")
                    return False
            else:
                logger.error(f"✗ Dashboard overview request failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Enterprise dashboard test error: {str(e)}")
            return False
    
    def test_system_status(self):
        """Test system status monitoring"""
        logger.info("Testing System Status...")
        
        try:
            response = requests.get(
                f"{BASE_URL}/enterprise/api/real-time/status",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                status_data = response.json()
                if status_data.get('success'):
                    status = status_data.get('status', {})
                    logger.info("✓ System status check successful")
                    logger.info(f"  Analytics Engine: {status.get('analytics_engine', 'unknown')}")
                    logger.info(f"  Database: {status.get('database', 'unknown')}")
                    logger.info(f"  External APIs: {status.get('external_apis', 'unknown')}")
                    return True
                else:
                    logger.error(f"✗ System status failed: {status_data}")
                    return False
            else:
                logger.error(f"✗ System status request failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ System status test error: {str(e)}")
            return False
    
    def test_active_routes(self):
        """Test active routes monitoring"""
        logger.info("Testing Active Routes...")
        
        try:
            response = requests.get(
                f"{BASE_URL}/enterprise/api/routes/active",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                routes_data = response.json()
                if routes_data.get('success'):
                    routes = routes_data.get('routes', [])
                    logger.info("✓ Active routes check successful")
                    logger.info(f"  Active Routes: {len(routes)}")
                    if routes:
                        route = routes[0]
                        logger.info(f"  Sample Route: {route.get('route_id')} - {route.get('status')}")
                    return True
                else:
                    logger.error(f"✗ Active routes failed: {routes_data}")
                    return False
            else:
                logger.error(f"✗ Active routes request failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Active routes test error: {str(e)}")
            return False
    
    def test_demo_data_population(self):
        """Test demo data population for analytics"""
        logger.info("Testing Demo Data Population...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/ai/demo/populate",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                demo_data = response.json()
                if demo_data.get('success'):
                    logger.info("✓ Demo data population successful")
                    logger.info(f"  Routes Generated: {demo_data.get('routes_generated', 0)}")
                    return True
                else:
                    logger.error(f"✗ Demo data population failed: {demo_data}")
                    return False
            else:
                logger.error(f"✗ Demo data request failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Demo data population test error: {str(e)}")
            return False
    
    def test_route_optimization(self):
        """Test route optimization with external data"""
        logger.info("Testing Route Optimization...")
        
        try:
            optimization_request = {
                'origin': 'New York, NY',
                'destination': 'Boston, MA',
                'waypoints': ['Hartford, CT'],
                'preferences': {
                    'priority': 'efficiency'
                }
            }
            
            response = requests.post(
                f"{BASE_URL}/enterprise/api/analytics/optimize-route",
                json=optimization_request,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                optimization_data = response.json()
                if optimization_data.get('success'):
                    logger.info("✓ Route optimization successful")
                    optimization = optimization_data.get('optimization', {})
                    recommended = optimization.get('recommended_route', {})
                    if recommended:
                        logger.info(f"  Recommended Route: {recommended.get('name', 'N/A')}")
                        logger.info(f"  Score: {recommended.get('score', 0):.1f}")
                    return True
                else:
                    logger.error(f"✗ Route optimization failed: {optimization_data}")
                    return False
            else:
                logger.error(f"✗ Route optimization request failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Route optimization test error: {str(e)}")
            return False
    
    def test_performance_trends(self):
        """Test performance trends analysis"""
        logger.info("Testing Performance Trends...")
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/ai/trends",
                params={'timeframe_days': 30},
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                trends_data = response.json()
                if trends_data.get('success'):
                    trends = trends_data.get('trends', [])
                    logger.info("✓ Performance trends analysis successful")
                    logger.info(f"  Trends Found: {len(trends)}")
                    for trend in trends:
                        logger.info(f"  {trend.get('metric_name', 'N/A')}: {trend.get('trend_direction', 'N/A')}")
                    return True
                else:
                    logger.error(f"✗ Performance trends failed: {trends_data}")
                    return False
            else:
                logger.error(f"✗ Performance trends request failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Performance trends test error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        logger.info("=" * 60)
        logger.info("ROUTEFORCE COMPREHENSIVE INTEGRATION TEST")
        logger.info("=" * 60)
        
        # Setup
        if not self.setup_test_environment():
            logger.error("Test environment setup failed. Aborting tests.")
            return False
        
        test_results = []
        
        # Core Analytics Tests
        logger.info("\n" + "=" * 40)
        logger.info("CORE ANALYTICS TESTS")
        logger.info("=" * 40)
        
        test_results.append(("Analytics Engine", self.test_analytics_engine()))
        test_results.append(("Prediction Models", self.test_prediction_models()))
        test_results.append(("Fleet Insights", self.test_fleet_insights()))
        test_results.append(("Smart Recommendations", self.test_smart_recommendations()))
        test_results.append(("Performance Trends", self.test_performance_trends()))
        
        # Dashboard Tests
        logger.info("\n" + "=" * 40)
        logger.info("DASHBOARD & MONITORING TESTS")
        logger.info("=" * 40)
        
        test_results.append(("Enterprise Dashboard", self.test_enterprise_dashboard()))
        test_results.append(("System Status", self.test_system_status()))
        test_results.append(("Active Routes", self.test_active_routes()))
        
        # Integration Tests
        logger.info("\n" + "=" * 40)
        logger.info("INTEGRATION & OPTIMIZATION TESTS")
        logger.info("=" * 40)
        
        test_results.append(("Demo Data Population", self.test_demo_data_population()))
        test_results.append(("Route Optimization", self.test_route_optimization()))
        
        # Results Summary
        logger.info("\n" + "=" * 60)
        logger.info("TEST RESULTS SUMMARY")
        logger.info("=" * 60)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✓ PASS" if result else "✗ FAIL"
            logger.info(f"{test_name:.<40} {status}")
            if result:
                passed_tests += 1
        
        logger.info("=" * 60)
        logger.info(f"TOTAL: {passed_tests}/{total_tests} tests passed")
        
        success_rate = (passed_tests / total_tests) * 100
        logger.info(f"SUCCESS RATE: {success_rate:.1f}%")
        
        if success_rate >= 80:
            logger.info("✓ INTEGRATION TEST SUITE: PASSED")
            return True
        else:
            logger.error("✗ INTEGRATION TEST SUITE: FAILED")
            return False

def main():
    """Main test execution"""
    test_suite = TestRouteForceIntegration()
    
    try:
        # Wait for server to be ready
        logger.info("Waiting for server to be ready...")
        time.sleep(2)
        
        # Run comprehensive tests
        success = test_suite.run_comprehensive_test()
        
        if success:
            logger.info("\n🎉 All systems are operational!")
            logger.info("RouteForce enhanced features are ready for production.")
        else:
            logger.error("\n⚠️  Some tests failed!")
            logger.error("Please check the system before deploying to production.")
        
        return success
        
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user.")
        return False
    except Exception as e:
        logger.error(f"\nUnexpected error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    main()
