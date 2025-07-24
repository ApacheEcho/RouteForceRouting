#!/usr/bin/env python3
"""
Comprehensive test suite for Advanced AI Analytics API
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:5001/api/ai"


def test_api_endpoint(
    endpoint: str, method: str = "GET", data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Test an API endpoint and return the response"""
    url = f"{BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")

        return {
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "data": (
                response.json()
                if response.headers.get("content-type", "").startswith(
                    "application/json"
                )
                else response.text
            ),
            "response_time": response.elapsed.total_seconds(),
        }
    except Exception as e:
        return {
            "status_code": 0,
            "success": False,
            "data": {"error": str(e)},
            "response_time": 0,
        }


def run_comprehensive_test():
    """Run comprehensive test suite for AI analytics"""

    print("🧪 RouteForce AI Analytics - Comprehensive Test Suite")
    print("=" * 60)

    tests = []

    # Test 1: Populate demo data
    print("\n1️⃣  Testing Demo Data Population...")
    result = test_api_endpoint("/demo/populate", "POST")
    tests.append(("Demo Data Population", result))

    if result["success"]:
        print(f"   ✅ Success: {result['data'].get('message', 'Data populated')}")
        print(f"   📊 Response time: {result['response_time']:.3f}s")
    else:
        print(f"   ❌ Failed: {result['data']}")

    # Test 2: Route insights
    print("\n2️⃣  Testing Route Insights...")
    result = test_api_endpoint(
        "/insights/route/test_route_ai?distance=35.2&duration=95&stops=6&fuel_used=4.1"
    )
    tests.append(("Route Insights", result))

    if result["success"]:
        insight = result["data"]["insight"]
        print(f"   ✅ Success: {insight['title']}")
        print(f"   📈 Impact Score: {insight['impact_score']}")
        print(f"   🎯 Confidence: {insight['confidence']}")
        print(f"   💡 Recommendations: {len(insight['recommendations'])}")
    else:
        print(f"   ❌ Failed: {result['data']}")

    # Test 3: Route prediction
    print("\n3️⃣  Testing Route Prediction...")
    prediction_data = {
        "route_id": "prediction_test",
        "distance": 28.5,
        "stops_count": 7,
        "hour_of_day": 10,
        "day_of_week": 3,
    }
    result = test_api_endpoint("/predict/route", "POST", prediction_data)
    tests.append(("Route Prediction", result))

    if result["success"]:
        prediction = result["data"]["prediction"]
        print(
            f"   ✅ Success: Predicted duration {prediction['predicted_duration_minutes']} min"
        )
        print(f"   💰 Fuel cost: ${prediction['predicted_fuel_cost']:.2f}")
        print(f"   ⚠️  Risk factors: {len(prediction['risk_factors'])}")
        print(f"   🔧 Suggestions: {len(prediction['optimization_suggestions'])}")
    else:
        print(f"   ❌ Failed: {result['data']}")

    # Test 4: Performance trends
    print("\n4️⃣  Testing Performance Trends...")
    result = test_api_endpoint("/trends?timeframe_days=30")
    tests.append(("Performance Trends", result))

    if result["success"]:
        trends = result["data"]["trends"]
        print(f"   ✅ Success: {len(trends)} trend metrics detected")
        for trend in trends[:2]:  # Show first 2
            print(
                f"   📊 {trend['metric_name']}: {trend['trend_direction']} ({trend['change_percentage']:+.1f}%)"
            )
    else:
        print(f"   ❌ Failed: {result['data']}")

    # Test 5: Fleet insights
    print("\n5️⃣  Testing Fleet Insights...")
    result = test_api_endpoint("/fleet/insights")
    tests.append(("Fleet Insights", result))

    if result["success"]:
        insights = result["data"]["fleet_insights"]
        print(f"   ✅ Success: Fleet analysis complete")
        print(f"   🚛 Total routes: {insights['total_routes']}")
        print(f"   📋 Recommendations: {len(insights['recommendations'])}")
    else:
        print(f"   ❌ Failed: {result['data']}")

    # Test 6: Smart recommendations
    print("\n6️⃣  Testing Smart Recommendations...")
    result = test_api_endpoint(
        "/recommendations/smart?vehicle_count=3&time_window=afternoon&priority=speed"
    )
    tests.append(("Smart Recommendations", result))

    if result["success"]:
        recommendations = result["data"]["recommendations"]
        print(
            f"   ✅ Success: {len(recommendations['smart_suggestions'])} smart suggestions"
        )
        print(f"   🎯 Confidence: {recommendations['confidence']}")
        print(
            f"   📝 Context: {recommendations['context']['time_window']} / {recommendations['context']['priority']}"
        )
    else:
        print(f"   ❌ Failed: {result['data']}")

    # Test 7: Batch analysis
    print("\n7️⃣  Testing Batch Route Analysis...")
    batch_data = {
        "routes": [
            {
                "id": "batch_01",
                "distance": 25.0,
                "duration": 80,
                "fuel_used": 3.2,
                "stops": ["A", "B", "C"],
            },
            {
                "id": "batch_02",
                "distance": 45.5,
                "duration": 150,
                "fuel_used": 6.1,
                "stops": ["D", "E", "F", "G"],
            },
            {
                "id": "batch_03",
                "distance": 15.2,
                "duration": 65,
                "fuel_used": 2.1,
                "stops": ["H", "I"],
            },
        ]
    }
    result = test_api_endpoint("/insights/batch", "POST", batch_data)
    tests.append(("Batch Analysis", result))

    if result["success"]:
        summary = result["data"]["summary"]
        print(f"   ✅ Success: Analyzed {summary['total_routes_analyzed']} routes")
        print(f"   📊 Average impact: {summary['average_impact_score']}")
        print(f"   🚨 High impact routes: {summary['high_impact_routes']}")
    else:
        print(f"   ❌ Failed: {result['data']}")

    # Test summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)

    successful_tests = sum(1 for _, result in tests if result["success"])
    total_tests = len(tests)
    success_rate = (successful_tests / total_tests) * 100

    print(f"Total tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success rate: {success_rate:.1f}%")

    avg_response_time = sum(result["response_time"] for _, result in tests) / len(tests)
    print(f"Average response time: {avg_response_time:.3f}s")

    if success_rate == 100:
        print("\n🎉 ALL TESTS PASSED! AI Analytics system is fully operational.")
    elif success_rate >= 80:
        print("\n✅ Most tests passed. System is largely functional.")
    else:
        print("\n⚠️  Some tests failed. Review the errors above.")

    print("\n🚀 Advanced AI Analytics features:")
    print("   • Route performance insights with ML predictions")
    print("   • Real-time anomaly detection")
    print("   • Smart contextual recommendations")
    print("   • Performance trend analysis")
    print("   • Fleet-wide optimization insights")
    print("   • Batch route analysis capabilities")

    return tests


if __name__ == "__main__":
    # Wait a moment for server to be ready
    time.sleep(2)
    run_comprehensive_test()
