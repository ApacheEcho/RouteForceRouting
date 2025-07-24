#!/usr/bin/env python3
"""
Live System Testing - Real-World Scenarios
Comprehensive validation of the RouteForce system with actual data
"""

import requests
import json
import time
from datetime import datetime
import concurrent.futures


class LiveSystemTest:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.test_results = []

    def log_test(self, name, status, details=None):
        """Log test results"""
        result = {
            "test": name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details,
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {name}: {status}")
        if details:
            print(f"   Details: {details}")

    def test_health_endpoints(self):
        """Test system health endpoints"""
        print("\n🏥 HEALTH CHECK TESTS")
        print("-" * 30)

        try:
            # Test main health endpoint
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Endpoint", "PASS", f"System status: {data.get('status')}"
                )
            else:
                self.log_test(
                    "Health Endpoint", "FAIL", f"Status code: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Health Endpoint", "FAIL", str(e))

    def test_route_optimization_scenarios(self):
        """Test different routing scenarios"""
        print("\n🚗 ROUTE OPTIMIZATION TESTS")
        print("-" * 30)

        # Test Case 1: Small delivery route (realistic scenario)
        test_cases = [
            {
                "name": "Small Delivery Route",
                "stops": [
                    {"lat": 37.7749, "lon": -122.4194, "name": "Warehouse SF"},
                    {"lat": 37.7849, "lon": -122.4094, "name": "Customer A"},
                    {"lat": 37.7649, "lon": -122.4294, "name": "Customer B"},
                    {"lat": 37.7549, "lon": -122.4394, "name": "Customer C"},
                ],
                "algorithm": "genetic",
            },
            {
                "name": "Medium Service Route",
                "stops": [
                    {"lat": 40.7128, "lon": -74.0060, "name": "NYC Office"},
                    {"lat": 40.7589, "lon": -73.9851, "name": "Times Square"},
                    {"lat": 40.6892, "lon": -74.0445, "name": "Statue of Liberty"},
                    {"lat": 40.7831, "lon": -73.9712, "name": "Central Park"},
                    {"lat": 40.7505, "lon": -73.9934, "name": "Empire State"},
                    {"lat": 40.7061, "lon": -74.0087, "name": "Brooklyn Bridge"},
                ],
                "algorithm": "simulated_annealing",
            },
            {
                "name": "Large Multi-Stop Route",
                "stops": [
                    {"lat": 34.0522, "lon": -118.2437, "name": f"Stop {i}"}
                    for i in range(8)
                ],
                "algorithm": "multi_objective",
            },
        ]

        for test_case in test_cases:
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.backend_url}/api/optimize", json=test_case, timeout=30
                )
                processing_time = time.time() - start_time

                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        test_case["name"],
                        "PASS",
                        f"Optimized {len(test_case['stops'])} stops in {processing_time:.2f}s",
                    )
                else:
                    self.log_test(
                        test_case["name"],
                        "FAIL",
                        f"Status: {response.status_code}, Response: {response.text[:100]}",
                    )
            except Exception as e:
                self.log_test(test_case["name"], "FAIL", str(e))

    def test_performance_under_load(self):
        """Test system performance under concurrent load"""
        print("\n⚡ PERFORMANCE LOAD TESTS")
        print("-" * 30)

        def make_optimization_request():
            """Single optimization request"""
            try:
                response = requests.post(
                    f"{self.backend_url}/api/optimize",
                    json={
                        "stops": [
                            {"lat": 37.7749, "lon": -122.4194, "name": "Start"},
                            {"lat": 37.7849, "lon": -122.4094, "name": "End"},
                        ],
                        "algorithm": "genetic",
                    },
                    timeout=10,
                )
                return response.status_code == 200
            except:
                return False

        # Test concurrent requests
        concurrent_requests = 10
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=concurrent_requests
        ) as executor:
            futures = [
                executor.submit(make_optimization_request)
                for _ in range(concurrent_requests)
            ]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        total_time = time.time() - start_time
        success_rate = sum(results) / len(results) * 100

        if success_rate >= 90:
            self.log_test(
                "Concurrent Load Test",
                "PASS",
                f"{concurrent_requests} requests, {success_rate:.1f}% success in {total_time:.2f}s",
            )
        else:
            self.log_test(
                "Concurrent Load Test", "FAIL", f"Only {success_rate:.1f}% success rate"
            )

    def test_real_world_addresses(self):
        """Test with real-world addresses"""
        print("\n🌍 REAL-WORLD ADDRESS TESTS")
        print("-" * 30)

        real_addresses = [
            {"lat": 37.7749, "lon": -122.4194, "name": "San Francisco, CA"},
            {"lat": 40.7128, "lon": -74.0060, "name": "New York, NY"},
            {"lat": 34.0522, "lon": -118.2437, "name": "Los Angeles, CA"},
            {"lat": 41.8781, "lon": -87.6298, "name": "Chicago, IL"},
            {"lat": 29.7604, "lon": -95.3698, "name": "Houston, TX"},
        ]

        try:
            response = requests.post(
                f"{self.backend_url}/api/optimize",
                json={"stops": real_addresses, "algorithm": "genetic"},
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Cross-Country Route",
                    "PASS",
                    f"Distance: {data.get('total_distance_km', 'N/A')} km",
                )
            else:
                self.log_test(
                    "Cross-Country Route", "FAIL", f"Status: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Cross-Country Route", "FAIL", str(e))

    def test_error_handling(self):
        """Test system error handling"""
        print("\n🛡️ ERROR HANDLING TESTS")
        print("-" * 30)

        error_tests = [
            {"name": "Empty Request", "data": {}, "expected_status": [400, 422]},
            {
                "name": "Invalid Coordinates",
                "data": {"stops": [{"lat": "invalid", "lon": "invalid"}]},
                "expected_status": [400, 422],
            },
            {
                "name": "Single Stop",
                "data": {"stops": [{"lat": 37.7749, "lon": -122.4194}]},
                "expected_status": [400, 422],
            },
        ]

        for test in error_tests:
            try:
                response = requests.post(
                    f"{self.backend_url}/api/optimize", json=test["data"], timeout=10
                )

                if response.status_code in test["expected_status"]:
                    self.log_test(
                        test["name"],
                        "PASS",
                        f"Proper error handling: {response.status_code}",
                    )
                else:
                    self.log_test(
                        test["name"],
                        "FAIL",
                        f"Unexpected status: {response.status_code}",
                    )
            except Exception as e:
                self.log_test(test["name"], "FAIL", str(e))

    def generate_report(self):
        """Generate final test report"""
        print("\n" + "=" * 60)
        print("🚀 LIVE SYSTEM TEST REPORT")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])

        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        print(f"📊 SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")

        if success_rate >= 90:
            print(f"\n🎉 SYSTEM STATUS: PRODUCTION READY")
            print(f"✅ System passes real-world testing criteria")
        elif success_rate >= 75:
            print(f"\n⚠️ SYSTEM STATUS: NEEDS MINOR FIXES")
            print(f"🔧 Address failed tests before production")
        else:
            print(f"\n❌ SYSTEM STATUS: NEEDS MAJOR FIXES")
            print(f"🚫 Not ready for production deployment")

        # Save results
        with open("live_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)

        return success_rate >= 90


def main():
    """Run comprehensive live system tests"""
    tester = LiveSystemTest()

    print("🚀 ROUTEFORCE LIVE SYSTEM TESTING")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print(f"Backend URL: {tester.backend_url}")

    # Run all test suites
    tester.test_health_endpoints()
    tester.test_route_optimization_scenarios()
    tester.test_performance_under_load()
    tester.test_real_world_addresses()
    tester.test_error_handling()

    # Generate final report
    is_ready = tester.generate_report()

    return is_ready


if __name__ == "__main__":
    main()
