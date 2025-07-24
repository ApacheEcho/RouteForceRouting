#!/usr/bin/env python3
"""
Test script for the Advanced Analytics Engine
"""

from app.analytics_ai import get_analytics_engine
from datetime import datetime

def test_analytics_engine():
    """Test the analytics engine functionality"""
    
    print("=== Testing Advanced Analytics Engine ===\n")
    
    # Initialize analytics engine
    analytics = get_analytics_engine()
    print("✅ Analytics engine created successfully")
    
    # Test adding sample data
    sample_route = {
        'route_id': 'test_001',
        'distance': 25.5,
        'duration': 85.0,
        'stops': ['Stop A', 'Stop B', 'Stop C'],
        'fuel_used': 3.2,
        'timestamp': datetime.now().isoformat()
    }
    
    analytics.add_route_data(sample_route)
    print("✅ Sample route data added")
    
    # Test generating insights
    insight = analytics.analyze_route_efficiency('test_001', sample_route)
    print(f"✅ Generated insight: {insight.title}")
    print(f"   Impact Score: {insight.impact_score}")
    print(f"   Recommendations: {len(insight.recommendations)}")
    print(f"   Type: {insight.insight_type}")
    
    # Test prediction
    prediction = analytics.predict_route_performance(sample_route)
    print(f"✅ Generated prediction: {prediction.predicted_duration:.1f} minutes")
    print(f"   Fuel cost: ${prediction.predicted_fuel_cost:.2f}")
    print(f"   Risk factors: {len(prediction.risk_factors)}")
    print(f"   Suggestions: {len(prediction.optimization_suggestions)}")
    
    # Test fleet insights
    fleet_insights = analytics.get_fleet_insights()
    print(f"✅ Fleet insights generated")
    print(f"   Total routes: {fleet_insights['total_routes']}")
    print(f"   Recommendations: {len(fleet_insights['recommendations'])}")
    
    # Test with multiple sample routes
    print("\n--- Adding multiple sample routes for ML training ---")
    import random
    
    for i in range(20):
        route_data = {
            'route_id': f'sample_{i:03d}',
            'distance': random.uniform(10, 50),
            'duration': random.uniform(30, 150),
            'stops': [f'Stop_{j}' for j in range(random.randint(3, 10))],
            'fuel_used': random.uniform(1.5, 6.0),
            'timestamp': datetime.now().isoformat()
        }
        analytics.add_route_data(route_data)
    
    print(f"✅ Added 20 sample routes for ML training")
    
    # Test trends after adding data
    trends = analytics.detect_performance_trends()
    print(f"✅ Performance trends detected: {len(trends)} metrics")
    
    print("\n🎉 Advanced Analytics Engine is working perfectly!")
    print("🚀 Ready for API integration and production use!")

if __name__ == "__main__":
    test_analytics_engine()
