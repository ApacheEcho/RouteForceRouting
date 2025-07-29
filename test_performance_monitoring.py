#!/usr/bin/env python3
"""
Performance Monitoring Integration Test
Tests the new performance monitoring system and APIs
"""

import requests
import time
import json
import logging
from datetime import datetime
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:5001"


class PerformanceMonitoringTest:
    """Test suite for performance monitoring features"""

    def __init__(self):
        self.auth_token = None
        self.test_results = []

    def authenticate(self):
        """Authenticate and get JWT token"""
        try:
            auth_data = {"email": "admin@routeforce.com", "password": "admin123"}

            response = requests.post(f"{BASE_URL}/auth/login", json=auth_data)
            if response.status_code == 200:
                auth_result = response.json()
                if auth_result.get("success"):
                    self.auth_token = auth_result.get("access_token")
                    logger.info("✓ Authentication successful")
                    return True

            logger.error(f"✗ Authentication failed: {response.status_code}")
            return False

        except Exception as e:
            logger.error(f"✗ Authentication failed: {str(e)}")
            return False

    def get_auth_headers(self):
        """Get authentication headers"""
        if not self.auth_token:
            self.authenticate()
        return {"Authorization": f"Bearer {self.auth_token}"}

    def test_health_check(self):
        """Test basic health check endpoint"""
        logger.info("Testing Health Check...")

        try:
            response = requests.get(f"{BASE_URL}/api/monitoring/health")

            if response.status_code == 200:
                health_data = response.json()
                logger.info("✓ Health check successful")
                logger.info(f"  Service: {health_data.get('service', 'Unknown')}")
                logger.info(f"  Version: {health_data.get('version', 'Unknown')}")
                return True
            else:
                logger.error(f"✗ Health check failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"✗ Health check error: {str(e)}")
            return False

    def test_monitoring_start(self):
        """Test starting performance monitoring"""
        logger.info("Testing Monitoring Start...")

        try:
            response = requests.post(
                f"{BASE_URL}/api/monitoring/start", headers=self.get_auth_headers()
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info("✓ Monitoring start successful")
                    logger.info(f"  Message: {result.get('message', 'N/A')}")
                    return True
                else:
                    logger.error(f"✗ Monitoring start failed: {result}")
                    return False
            else:
                logger.error(
                    f"✗ Monitoring start request failed: {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"✗ Monitoring start error: {str(e)}")
            return False

    def test_current_metrics(self):
        """Test current metrics retrieval"""
        logger.info("Testing Current Metrics...")

        try:
            # Wait a bit for metrics to be collected
            time.sleep(2)

            response = requests.get(
                f"{BASE_URL}/api/monitoring/metrics/current",
                headers=self.get_auth_headers(),
            )

            if response.status_code == 200:
                metrics_data = response.json()
                if metrics_data.get("success"):
                    metrics = metrics_data.get("metrics", {})
                    logger.info("✓ Current metrics retrieval successful")
                    logger.info(f"  Metrics collected: {len(metrics)}")

                    # Log some key metrics
                    for metric_type, metric_data in list(metrics.items())[:3]:
                        value = metric_data.get("value", 0)
                        unit = metric_data.get("unit", "")
                        status = metric_data.get("status", "unknown")
                        logger.info(f"  {metric_type}: {value:.1f}{unit} ({status})")

                    return True
                else:
                    logger.error(f"✗ Current metrics failed: {metrics_data}")
                    return False
            else:
                logger.error(
                    f"✗ Current metrics request failed: {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"✗ Current metrics error: {str(e)}")
            return False

    def test_health_score(self):
        """Test system health score calculation"""
        logger.info("Testing Health Score...")

        try:
            response = requests.get(
                f"{BASE_URL}/api/monitoring/health/score",
                headers=self.get_auth_headers(),
            )

            if response.status_code == 200:
                health_data = response.json()
                if health_data.get("success"):
                    health_score = health_data.get("health_score", {})
                    logger.info("✓ Health score calculation successful")
                    logger.info(f"  Score: {health_score.get('score', 0)}/100")
                    logger.info(f"  Status: {health_score.get('status', 'unknown')}")

                    details = health_score.get("details", {})
                    if details:
                        logger.info(f"  Normal: {details.get('normal', 0)} metrics")
                        logger.info(f"  Warning: {details.get('warning', 0)} metrics")
                        logger.info(f"  Critical: {details.get('critical', 0)} metrics")

                    return True
                else:
                    logger.error(f"✗ Health score failed: {health_data}")
                    return False
            else:
                logger.error(f"✗ Health score request failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"✗ Health score error: {str(e)}")
            return False

    def test_metrics_history(self):
        """Test historical metrics retrieval"""
        logger.info("Testing Metrics History...")

        try:
            # Wait for some historical data
            time.sleep(3)

            response = requests.get(
                f"{BASE_URL}/api/monitoring/metrics/history/cpu_usage",
                params={"hours": 1},
                headers=self.get_auth_headers(),
            )

            if response.status_code == 200:
                history_data = response.json()
                if history_data.get("success"):
                    history = history_data.get("history", [])
                    logger.info("✓ Metrics history retrieval successful")
                    logger.info(f"  Historical data points: {len(history)}")
                    logger.info(
                        f"  Metric type: {history_data.get('metric_type', 'unknown')}"
                    )

                    if history:
                        latest = history[-1]
                        logger.info(
                            f"  Latest value: {latest.get('value', 0):.1f}{latest.get('unit', '')}"
                        )

                    return True
                else:
                    logger.error(f"✗ Metrics history failed: {history_data}")
                    return False
            else:
                logger.error(
                    f"✗ Metrics history request failed: {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"✗ Metrics history error: {str(e)}")
            return False

    def test_alerts_system(self):
        """Test alerts system"""
        logger.info("Testing Alerts System...")

        try:
            response = requests.get(
                f"{BASE_URL}/api/monitoring/alerts", headers=self.get_auth_headers()
            )

            if response.status_code == 200:
                alerts_data = response.json()
                if alerts_data.get("success"):
                    alerts = alerts_data.get("alerts", [])
                    logger.info("✓ Alerts system retrieval successful")
                    logger.info(f"  Active alerts: {len(alerts)}")

                    # Show first few alerts if any
                    for i, alert in enumerate(alerts[:3]):
                        severity = alert.get("severity", "unknown")
                        title = alert.get("title", "No title")
                        logger.info(f"  Alert {i+1}: {title} ({severity})")

                    return True
                else:
                    logger.error(f"✗ Alerts system failed: {alerts_data}")
                    return False
            else:
                logger.error(f"✗ Alerts system request failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"✗ Alerts system error: {str(e)}")
            return False

    def test_performance_summary(self):
        """Test comprehensive performance summary"""
        logger.info("Testing Performance Summary...")

        try:
            response = requests.get(
                f"{BASE_URL}/api/monitoring/summary", headers=self.get_auth_headers()
            )

            if response.status_code == 200:
                summary_data = response.json()
                if summary_data.get("success"):
                    summary = summary_data.get("summary", {})
                    logger.info("✓ Performance summary retrieval successful")

                    # Show key summary information
                    health_score = summary.get("health_score", {})
                    logger.info(f"  Health Score: {health_score.get('score', 0)}/100")

                    current_metrics = summary.get("current_metrics", {})
                    logger.info(f"  Current Metrics: {len(current_metrics)} types")

                    active_alerts = summary.get("active_alerts", [])
                    logger.info(f"  Active Alerts: {len(active_alerts)}")

                    monitoring_status = summary.get("monitoring_status", "unknown")
                    logger.info(f"  Monitoring Status: {monitoring_status}")

                    return True
                else:
                    logger.error(f"✗ Performance summary failed: {summary_data}")
                    return False
            else:
                logger.error(
                    f"✗ Performance summary request failed: {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"✗ Performance summary error: {str(e)}")
            return False

    def test_system_info(self):
        """Test system information retrieval"""
        logger.info("Testing System Info...")

        try:
            response = requests.get(
                f"{BASE_URL}/api/monitoring/system/info",
                headers=self.get_auth_headers(),
            )

            if response.status_code == 200:
                info_data = response.json()
                if info_data.get("success"):
                    system_info = info_data.get("system_info", {})
                    logger.info("✓ System info retrieval successful")
                    logger.info(f"  Platform: {system_info.get('platform', 'unknown')}")
                    logger.info(
                        f"  Python Version: {system_info.get('python_version', 'unknown')}"
                    )
                    logger.info(f"  CPU Count: {system_info.get('cpu_count', 0)}")
                    logger.info(
                        f"  Process Count: {system_info.get('process_count', 0)}"
                    )

                    return True
                else:
                    logger.error(f"✗ System info failed: {info_data}")
                    return False
            else:
                logger.error(f"✗ System info request failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"✗ System info error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all performance monitoring tests"""
        logger.info("=" * 60)
        logger.info("PERFORMANCE MONITORING INTEGRATION TEST")
        logger.info("=" * 60)

        # Wait for server to be ready
        logger.info("Waiting for server to be ready...")
        time.sleep(3)

        # Authenticate
        if not self.authenticate():
            logger.error("Authentication failed - aborting tests")
            return False

        # Define test functions
        tests = [
            ("Health Check", self.test_health_check),
            ("Monitoring Start", self.test_monitoring_start),
            ("Current Metrics", self.test_current_metrics),
            ("Health Score", self.test_health_score),
            ("Metrics History", self.test_metrics_history),
            ("Alerts System", self.test_alerts_system),
            ("Performance Summary", self.test_performance_summary),
            ("System Info", self.test_system_info),
        ]

        logger.info("\n" + "=" * 40)
        logger.info("PERFORMANCE MONITORING TESTS")
        logger.info("=" * 40)

        # Run tests
        test_results = []
        for test_name, test_func in tests:
            result = test_func()
            test_results.append((test_name, result))
            time.sleep(1)  # Brief pause between tests

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("PERFORMANCE MONITORING TEST RESULTS SUMMARY")
        logger.info("=" * 60)

        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)

        for test_name, result in test_results:
            status = "✓ PASS" if result else "✗ FAIL"
            logger.info(f"{test_name:.<40} {status}")

        logger.info("=" * 60)
        logger.info(f"TOTAL: {passed}/{total} tests passed")
        logger.info(f"SUCCESS RATE: {(passed/total)*100:.1f}%")

        if passed == total:
            logger.info("✓ PERFORMANCE MONITORING TEST SUITE: PASSED")
            logger.info("\n🎉 Performance monitoring system is operational!")
        else:
            logger.error("✗ PERFORMANCE MONITORING TEST SUITE: FAILED")
            logger.error("\n⚠️  Some tests failed!")

        return passed == total


def main():
    """Main test execution"""
    test_suite = PerformanceMonitoringTest()
    success = test_suite.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
