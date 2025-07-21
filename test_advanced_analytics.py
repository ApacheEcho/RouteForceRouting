#!/usr/bin/env python3
"""
Advanced Analytics Integration Test
Tests the new advanced ML ensemble features, uncertainty quantification, and enhanced analytics
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedAnalyticsTest:
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        
    def setup_test_auth(self) -> bool:
        """Setup authentication for tests"""
        try:
            # Login
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            if response.status_code == 200:
                result = response.json()
                self.auth_token = result.get('access_token')
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                logger.info("✓ Authentication successful")
                return True
            else:
                logger.error(f"✗ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"✗ Authentication error: {e}")
            return False
    
    def test_advanced_analytics_api(self) -> bool:
        """Test advanced analytics API endpoints"""
        try:
            # Test advanced prediction endpoint
            prediction_data = {
                "route_features": {
                    "route_id": "test_advanced_001",
                    "distance": 25.5,
                    "stops_count": 8,
                    "hour_of_day": 10,
                    "day_of_week": 2,
                    "is_weekend": False,
                    "is_rush_hour": False,
                    "avg_stop_distance": 3.2,
                    "weather_factor": 1.1,
                    "traffic_factor": 1.3
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/analytics/predict/advanced",
                json=prediction_data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✓ Advanced prediction API successful")
                logger.info(f"  Prediction confidence: {result.get('model_confidence', 'N/A')}")
                logger.info(f"  Uncertainty range: {result.get('confidence_interval', 'N/A')}")
                return True
            else:
                logger.error(f"✗ Advanced prediction API failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Advanced analytics API test error: {e}")
            return False
    
    def test_performance_monitoring(self) -> bool:
        """Test performance monitoring endpoints"""
        try:
            # Test system metrics
            response = self.session.get(f"{self.base_url}/api/v1/monitoring/metrics")
            if response.status_code == 200:
                metrics = response.json()
                logger.info("✓ Performance monitoring successful")
                logger.info(f"  CPU Usage: {metrics.get('cpu_usage', 'N/A')}")
                logger.info(f"  Memory Usage: {metrics.get('memory_usage', 'N/A')}")
                logger.info(f"  Response Time: {metrics.get('api_response_time', 'N/A')}")
                
                # Test performance trends
                response = self.session.get(f"{self.base_url}/api/v1/monitoring/trends")
                if response.status_code == 200:
                    trends = response.json()
                    logger.info("✓ Performance trends successful")
                    logger.info(f"  Trends available: {len(trends.get('trends', []))}")
                    return True
                    
            logger.error(f"✗ Performance monitoring failed: {response.status_code}")
            return False
            
        except Exception as e:
            logger.error(f"✗ Performance monitoring test error: {e}")
            return False
    
    def test_advanced_dashboard_api(self) -> bool:
        """Test advanced dashboard API endpoints"""
        try:
            # Test ML insights
            response = self.session.get(f"{self.base_url}/api/v1/dashboard/ml-insights")
            if response.status_code == 200:
                insights = response.json()
                logger.info("✓ ML insights API successful")
                logger.info(f"  Model accuracy: {insights.get('model_performance', {}).get('accuracy', 'N/A')}")
                
                # Test predictive analytics
                response = self.session.get(f"{self.base_url}/api/v1/dashboard/predictive-analytics")
                if response.status_code == 200:
                    analytics = response.json()
                    logger.info("✓ Predictive analytics API successful")
                    logger.info(f"  Expected routes today: {analytics.get('route_predictions', {}).get('expected_routes_today', 'N/A')}")
                    
                    # Test optimization insights
                    response = self.session.get(f"{self.base_url}/api/v1/dashboard/optimization-insights")
                    if response.status_code == 200:
                        optimization = response.json()
                        logger.info("✓ Optimization insights API successful")
                        logger.info(f"  Best algorithm: {optimization.get('optimization_patterns', {}).get('best_performing_algorithm', 'N/A')}")
                        return True
                        
            logger.error(f"✗ Advanced dashboard API failed: {response.status_code}")
            return False
            
        except Exception as e:
            logger.error(f"✗ Advanced dashboard API test error: {e}")
            return False
    
    def test_ensemble_training(self) -> bool:
        """Test ensemble model training with sample data"""
        try:
            # Generate sample training data
            training_data = {
                "training_samples": [
                    {
                        "route_id": f"train_{i}",
                        "distance": 10 + i * 2.5,
                        "duration": 30 + i * 5,
                        "stops_count": 3 + i,
                        "fuel_used": 2 + i * 0.5,
                        "hour_of_day": 8 + (i % 12),
                        "day_of_week": i % 7,
                        "weather_factor": 1.0 + (i % 3) * 0.1,
                        "traffic_factor": 1.0 + (i % 4) * 0.2,
                        "timestamp": (datetime.now() - timedelta(days=i)).isoformat()
                    }
                    for i in range(50)  # Generate 50 training samples
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/analytics/train-ensemble",
                json=training_data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✓ Ensemble training successful")
                logger.info(f"  Models trained: {len(result.get('trained_models', {}))}")
                logger.info(f"  Training samples: {result.get('metadata', {}).get('training_samples', 'N/A')}")
                return True
            else:
                logger.error(f"✗ Ensemble training failed: {response.status_code}")
                logger.error(f"  Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Ensemble training test error: {e}")
            return False
    
    def test_uncertainty_quantification(self) -> bool:
        """Test uncertainty quantification features"""
        try:
            # Test prediction with uncertainty
            uncertainty_data = {
                "route_features": {
                    "route_id": "uncertainty_test_001",
                    "distance": 15.0,
                    "stops_count": 6,
                    "hour_of_day": 14,
                    "day_of_week": 3,
                    "weather_factor": 1.2,
                    "traffic_factor": 1.1
                },
                "include_uncertainty": True,
                "confidence_levels": [0.68, 0.95, 0.99]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/analytics/predict/uncertainty",
                json=uncertainty_data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✓ Uncertainty quantification successful")
                logger.info(f"  Epistemic uncertainty: {result.get('epistemic_uncertainty', 'N/A')}")
                logger.info(f"  Aleatoric uncertainty: {result.get('aleatoric_uncertainty', 'N/A')}")
                logger.info(f"  Model agreement: {result.get('model_agreement', 'N/A')}")
                
                # Check confidence intervals
                ci = result.get('confidence_intervals', {})
                if ci:
                    logger.info(f"  95% confidence interval: {ci.get('95%', 'N/A')}")
                
                return True
            else:
                logger.error(f"✗ Uncertainty quantification failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Uncertainty quantification test error: {e}")
            return False
    
    def test_real_time_alerts(self) -> bool:
        """Test real-time alert system"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/dashboard/real-time-alerts")
            if response.status_code == 200:
                alerts = response.json()
                logger.info("✓ Real-time alerts API successful")
                logger.info(f"  Active alerts: {len(alerts.get('alerts', []))}")
                
                # Check alert types
                alert_types = set()
                for alert in alerts.get('alerts', []):
                    alert_types.add(alert.get('type', 'unknown'))
                
                logger.info(f"  Alert types: {', '.join(alert_types) if alert_types else 'None'}")
                return True
            else:
                logger.error(f"✗ Real-time alerts failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Real-time alerts test error: {e}")
            return False
    
    def test_advanced_dashboard_ui(self) -> bool:
        """Test advanced dashboard UI availability"""
        try:
            response = self.session.get(f"{self.base_url}/dashboard/advanced-analytics")
            if response.status_code == 200:
                logger.info("✓ Advanced dashboard UI accessible")
                
                # Check if it contains expected sections
                content = response.text
                ui_sections = [
                    'ML Insights',
                    'Performance Trends',
                    'Predictive Analytics',
                    'Real-time Alerts',
                    'Optimization Insights'
                ]
                
                found_sections = []
                for section in ui_sections:
                    if section in content:
                        found_sections.append(section)
                
                logger.info(f"  UI sections found: {len(found_sections)}/{len(ui_sections)}")
                return len(found_sections) >= 3  # At least 3 sections should be present
            else:
                logger.error(f"✗ Advanced dashboard UI not accessible: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Advanced dashboard UI test error: {e}")
            return False
    
    def run_comprehensive_test(self) -> bool:
        """Run all advanced analytics tests"""
        logger.info("=" * 60)
        logger.info("ADVANCED ANALYTICS COMPREHENSIVE TEST")
        logger.info("=" * 60)
        
        # Setup
        if not self.setup_test_auth():
            return False
        
        # Run tests
        tests = [
            ("Advanced Analytics API", self.test_advanced_analytics_api),
            ("Performance Monitoring", self.test_performance_monitoring),
            ("Advanced Dashboard API", self.test_advanced_dashboard_api),
            ("Ensemble Training", self.test_ensemble_training),
            ("Uncertainty Quantification", self.test_uncertainty_quantification),
            ("Real-time Alerts", self.test_real_time_alerts),
            ("Advanced Dashboard UI", self.test_advanced_dashboard_ui)
        ]
        
        results = []
        for test_name, test_func in tests:
            logger.info(f"\nTesting {test_name}...")
            try:
                result = test_func()
                results.append((test_name, result))
                status = "✓ PASS" if result else "✗ FAIL"
                logger.info(f"{test_name}: {status}")
            except Exception as e:
                logger.error(f"{test_name}: ✗ ERROR - {e}")
                results.append((test_name, False))
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("ADVANCED ANALYTICS TEST RESULTS")
        logger.info("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            logger.info(f"{test_name:.<30} {status}")
        
        logger.info("=" * 60)
        logger.info(f"TOTAL: {passed}/{total} tests passed")
        logger.info(f"SUCCESS RATE: {(passed/total)*100:.1f}%")
        
        if passed == total:
            logger.info("✓ ADVANCED ANALYTICS TEST SUITE: PASSED")
            logger.info("\n🚀 Advanced analytics features are fully operational!")
        else:
            logger.error("✗ ADVANCED ANALYTICS TEST SUITE: FAILED")
            logger.error("\n⚠️  Some advanced features need attention.")
        
        return passed == total

if __name__ == "__main__":
    test_runner = AdvancedAnalyticsTest()
    success = test_runner.run_comprehensive_test()
    exit(0 if success else 1)
