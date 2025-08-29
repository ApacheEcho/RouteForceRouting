#!/usr/bin/env python3
"""
Full System Integration Test
Tests the complete RouteForce enterprise system including frontend, backend, and APIs
"""

import requests
import json
import time
import sys
from datetime import datetime
import pytest


class RouteForceSystemTest:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_results = []
        self.jwt_token = None
        self.login_and_store_token()

    def login_and_store_token(self):
        """Authenticate and store JWT token for protected endpoints"""
        login_url = f"{self.backend_url}/auth/login"
        credentials = {"email": "admin@routeforce.com", "password": "admin123"}
        try:
            resp = requests.post(login_url, json=credentials, timeout=5)
            if resp.status_code == 200 and resp.json().get("access_token"):
                self.jwt_token = resp.json()["access_token"]
                print("[AUTH] Successfully obtained JWT token.")
            else:
                print(f"[AUTH] Failed to obtain JWT token: {resp.text}")
        except Exception as e:
            print(f"[AUTH] Exception during login: {e}")

    def get_auth_headers(self):
        token = getattr(self, "jwt_token", None)
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}

    def log_test(self, test_name, success, message=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append(
            {
                "test": test_name,
                "success": success,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            }
        )
        print(f"{status} {test_name}: {message}")

    def test_backend_health(self):
        """Test backend health endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Backend Health",
                    True,
                    f"Status: {data.get('status', 'unknown')}",
                )
                return True
            else:
                self.log_test(
                    "Backend Health", False, f"HTTP {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_test(
                "Backend Health", False, f"Connection error: {str(e)}"
            )
            return False

    def test_frontend_accessibility(self):
        """Test frontend accessibility"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.log_test(
                    "Frontend Accessibility",
                    True,
                    "Frontend is serving content",
                )
                return True
            else:
                self.log_test(
                    "Frontend Accessibility",
                    False,
                    f"HTTP {response.status_code}",
                )
                return False
        except Exception as e:
            self.log_test(
                "Frontend Accessibility", False, f"Connection error: {str(e)}"
            )
            return False

    def test_api_endpoints(self):
        """Test core API endpoints"""
        endpoints = [
            "/api/optimize",
            "/api/analytics",
            "/advanced/api/ml-insights",
            "/advanced/api/performance-trends",
            "/advanced/api/predictive-analytics",
            "/advanced/api/real-time-alerts",
            "/advanced/api/optimization-insights",
        ]

        success_count = 0
        for endpoint in endpoints:
            try:
                headers = self.get_auth_headers()
                if endpoint == "/api/optimize":
                    # POST request for optimization
                    test_data = {
                        "stops": [
                            {
                                "id": "1",
                                "lat": 37.7749,
                                "lng": -122.4194,
                                "name": "San Francisco",
                            },
                            {
                                "id": "2",
                                "lat": 37.7849,
                                "lng": -122.4094,
                                "name": "North Beach",
                            },
                        ],
                        "algorithm": "genetic",
                        "depot": {
                            "lat": 37.7649,
                            "lng": -122.4294,
                            "name": "Depot",
                        },
                    }
                    response = requests.post(
                        f"{self.backend_url}{endpoint}",
                        json=test_data,
                        headers=headers,
                        timeout=10,
                    )
                else:
                    # GET request for other endpoints
                    response = requests.get(
                        f"{self.backend_url}{endpoint}", headers=headers, timeout=5
                    )

                if response.status_code in [200, 201]:
                    self.log_test(
                        f"API {endpoint}", True, f"HTTP {response.status_code}"
                    )
                    success_count += 1
                else:
                    self.log_test(
                        f"API {endpoint}",
                        False,
                        f"HTTP {response.status_code}",
                    )

            except Exception as e:
                self.log_test(f"API {endpoint}", False, f"Error: {str(e)}")

        return success_count == len(endpoints)

    def test_database_integration(self):
        """Test database integration"""
        try:
            # Test analytics endpoint that uses database
            response = requests.get(
                f"{self.backend_url}/api/analytics", timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Database Integration", True, "Analytics data retrieved"
                )
                return True
            else:
                self.log_test(
                    "Database Integration",
                    False,
                    f"HTTP {response.status_code}",
                )
                return False
        except Exception as e:
            self.log_test("Database Integration", False, f"Error: {str(e)}")
            return False

    def test_ml_integration(self):
        """Test ML model integration"""
        try:
            response = requests.get(
                f"{self.backend_url}/advanced/api/ml-insights", headers=self.get_auth_headers(), timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test(
                        "ML Integration",
                        True,
                        "ML insights retrieved successfully",
                    )
                    return True
                else:
                    self.log_test(
                        "ML Integration",
                        False,
                        f"ML error: {data.get('error', 'unknown')}",
                    )
                    return False
            else:
                self.log_test(
                    "ML Integration", False, f"HTTP {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_test("ML Integration", False, f"Error: {str(e)}")
            return False

    def test_performance_monitoring(self):
        """Test performance monitoring"""
        try:
            response = requests.get(
                f"{self.backend_url}/advanced/api/performance-trends",
                headers=self.get_auth_headers(),
                timeout=5,
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test(
                        "Performance Monitoring",
                        True,
                        "Performance data available",
                    )
                    return True
                else:
                    self.log_test(
                        "Performance Monitoring", False, "No performance data"
                    )
                    return False
            else:
                self.log_test(
                    "Performance Monitoring",
                    False,
                    f"HTTP {response.status_code}",
                )
                return False
        except Exception as e:
            self.log_test("Performance Monitoring", False, f"Error: {str(e)}")
            return False

    @pytest.mark.timeout(60)
    def test_optimization_algorithms(self):
        """Test optimization algorithms"""
        algorithms = ["genetic", "simulated_annealing", "multi_objective"]
        success_count = 0

        test_data = {
            "stops": [
                {
                    "id": "1",
                    "lat": 37.7749,
                    "lng": -122.4194,
                    "name": "Stop 1",
                },
                {
                    "id": "2",
                    "lat": 37.7849,
                    "lng": -122.4094,
                    "name": "Stop 2",
                },
                {
                    "id": "3",
                    "lat": 37.7649,
                    "lng": -122.4394,
                    "name": "Stop 3",
                },
            ],
            "depot": {"lat": 37.7549, "lng": -122.4494, "name": "Depot"},
        }

        for algorithm in algorithms:
            try:
                test_data["algorithm"] = algorithm
                response = requests.post(
                    f"{self.backend_url}/api/optimize",
                    json=test_data,
                    headers=self.get_auth_headers(),
                    timeout=15,
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_test(
                            f"Algorithm {algorithm}",
                            True,
                            f"Optimized route with {len(data.get('optimized_route', []))} stops",
                        )
                        success_count += 1
                    else:
                        self.log_test(
                            f"Algorithm {algorithm}",
                            False,
                            f"Optimization failed: {data.get('error', 'unknown')}",
                        )
                else:
                    self.log_test(
                        f"Algorithm {algorithm}",
                        False,
                        f"HTTP {response.status_code}",
                    )
            except Exception as e:
                self.log_test(
                    f"Algorithm {algorithm}", False, f"Error: {str(e)}"
                )

        return success_count == len(algorithms)

    def run_full_test_suite(self):
        """Run the complete test suite"""
        print("🚀 Starting RouteForce Enterprise System Integration Test")
        print("=" * 60)

        # Core system tests
        backend_ok = self.test_backend_health()
        frontend_ok = self.test_frontend_accessibility()

        if not backend_ok:
            print(
                "\n❌ Backend is not responding. Please ensure the backend is running on port 8000."
            )
            return False

        if not frontend_ok:
            print(
                "\n⚠️  Frontend is not responding. Please ensure the frontend is running on port 3000."
            )

        # API and integration tests
        print("\n📡 Testing API Endpoints...")
        api_ok = self.test_api_endpoints()

        print("\n🗄️  Testing Database Integration...")
        db_ok = self.test_database_integration()

        print("\n🤖 Testing ML Integration...")
        ml_ok = self.test_ml_integration()

        print("\n📊 Testing Performance Monitoring...")
        perf_ok = self.test_performance_monitoring()

        print("\n🎯 Testing Optimization Algorithms...")
        opt_ok = self.test_optimization_algorithms()

        # Summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(
            1 for result in self.test_results if result["success"]
        )
        failed_tests = total_tests - passed_tests

        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")

        # Overall system status
        print("\n🏆 SYSTEM STATUS:")
        if passed_tests == total_tests:
            print(
                "✅ ALL SYSTEMS OPERATIONAL - Enterprise RouteForce is ready for production!"
            )
        elif passed_tests >= total_tests * 0.8:
            print(
                "⚠️  MOSTLY OPERATIONAL - Minor issues detected, but core functionality is working"
            )
        else:
            print(
                "❌ CRITICAL ISSUES - System requires attention before production deployment"
            )

        # Save results
        with open("integration_test_results.json", "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "summary": {
                        "total_tests": total_tests,
                        "passed_tests": passed_tests,
                        "failed_tests": failed_tests,
                        "success_rate": (passed_tests / total_tests) * 100,
                    },
                    "test_results": self.test_results,
                },
                f,
                indent=2,
            )

        print(f"\n📄 Detailed results saved to: integration_test_results.json")

        return passed_tests == total_tests


if __name__ == "__main__":
    tester = RouteForceSystemTest()
    success = tester.run_full_test_suite()
    sys.exit(0 if success else 1)
