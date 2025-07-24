"""
Enhanced Analytics Dashboard
Integrates AI analytics with real-time WebSocket updates
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from datetime import datetime, timedelta
from app.analytics_ai import get_analytics_engine
import json

enhanced_dashboard_bp = Blueprint('enhanced_dashboard', __name__, url_prefix='/dashboard')

@enhanced_dashboard_bp.route('/analytics')
def analytics_dashboard():
    """Enhanced analytics dashboard page"""
    return render_template('dashboard/enhanced_analytics.html',
                         page_title='Advanced Analytics Dashboard')

@enhanced_dashboard_bp.route('/realtime')
def realtime_dashboard():
    """Real-time monitoring dashboard"""
    return render_template('dashboard/realtime_monitoring.html',
                         page_title='Real-time Fleet Monitoring')

@enhanced_dashboard_bp.route('/api/analytics/summary')
def analytics_summary():
    """Get analytics summary for dashboard"""
    try:
        analytics = get_analytics_engine()
        
        # Get fleet insights
        fleet_insights = analytics.get_fleet_insights()
        
        # Get recent trends
        trends = analytics.detect_performance_trends(timeframe_days=7)
        
        # Calculate key metrics
        summary = {
            'total_routes': fleet_insights.get('total_routes', 0),
            'avg_fuel_efficiency': round(fleet_insights.get('avg_fuel_efficiency', 0), 2),
            'avg_duration': round(fleet_insights.get('avg_duration_minutes', 0), 1),
            'trends': [
                {
                    'metric': trend.metric_name,
                    'value': round(trend.current_value, 2),
                    'direction': trend.trend_direction,
                    'change': round(trend.change_percentage, 1)
                } for trend in trends
            ],
            'recommendations': fleet_insights.get('recommendations', [])[:3],  # Top 3
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_dashboard_bp.route('/api/performance/alerts')
def performance_alerts():
    """Get performance alerts and anomalies"""
    try:
        analytics = get_analytics_engine()
        
        # Analyze recent data for alerts
        alerts = []
        
        # Get fleet insights to check for issues
        fleet_insights = analytics.get_fleet_insights()
        trends = analytics.detect_performance_trends()
        
        # Generate alerts based on trends
        for trend in trends:
            if trend.trend_direction == 'declining':
                severity = 'high' if abs(trend.change_percentage) > 15 else 'medium'
                alerts.append({
                    'id': f"trend_{trend.metric_name.lower().replace(' ', '_')}",
                    'type': 'performance_decline',
                    'severity': severity,
                    'title': f"{trend.metric_name} Declining",
                    'message': f"{trend.metric_name} has declined by {abs(trend.change_percentage):.1f}% recently",
                    'metric': trend.metric_name,
                    'value': trend.current_value,
                    'change': trend.change_percentage,
                    'timestamp': datetime.now().isoformat()
                })
        
        # Check fuel efficiency threshold
        avg_efficiency = fleet_insights.get('avg_fuel_efficiency', 0)
        if avg_efficiency < 8.0:  # Below 8 km/L
            alerts.append({
                'id': 'fuel_efficiency_low',
                'type': 'efficiency_warning',
                'severity': 'medium',
                'title': 'Low Fuel Efficiency',
                'message': f'Fleet average fuel efficiency is {avg_efficiency:.1f} km/L, below optimal range',
                'metric': 'Fuel Efficiency',
                'value': avg_efficiency,
                'threshold': 8.0,
                'timestamp': datetime.now().isoformat()
            })
        
        # Check average duration threshold
        avg_duration = fleet_insights.get('avg_duration_minutes', 0)
        if avg_duration > 150:  # Above 2.5 hours
            alerts.append({
                'id': 'duration_high',
                'type': 'time_warning',
                'severity': 'medium',
                'title': 'High Average Duration',
                'message': f'Routes taking {avg_duration:.1f} minutes on average, consider optimization',
                'metric': 'Duration',
                'value': avg_duration,
                'threshold': 150,
                'timestamp': datetime.now().isoformat()
            })
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'total_alerts': len(alerts)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_dashboard_bp.route('/api/insights/generate', methods=['POST'])
def generate_insights():
    """Generate AI insights for specific routes or timeframes"""
    try:
        data = request.get_json()
        analytics = get_analytics_engine()
        
        insight_type = data.get('type', 'fleet')
        timeframe = data.get('timeframe', 7)  # days
        
        insights = []
        
        if insight_type == 'fleet':
            # Generate fleet-wide insights
            fleet_data = analytics.get_fleet_insights()
            trends = analytics.detect_performance_trends(timeframe_days=timeframe)
            
            # Convert trends to insights
            for trend in trends:
                if trend.trend_direction != 'stable':
                    insight = {
                        'id': f"trend_{trend.metric_name.lower().replace(' ', '_')}",
                        'type': 'trend_analysis',
                        'title': f"{trend.metric_name} Trend Analysis",
                        'description': f"{trend.metric_name} is {trend.trend_direction} by {abs(trend.change_percentage):.1f}%",
                        'impact_score': min(abs(trend.change_percentage) * 2, 100),
                        'confidence': 0.85,
                        'recommendations': generate_trend_recommendations(trend),
                        'data': {
                            'current_value': trend.current_value,
                            'change_percentage': trend.change_percentage,
                            'forecast_7d': trend.forecast_7d,
                            'forecast_30d': trend.forecast_30d
                        },
                        'timestamp': datetime.now().isoformat()
                    }
                    insights.append(insight)
        
        elif insight_type == 'route' and 'route_id' in data:
            # Generate route-specific insights
            route_id = data['route_id']
            route_data = data.get('route_data', {})
            
            if route_data:
                insight = analytics.analyze_route_efficiency(route_id, route_data)
                insights.append({
                    'id': f"route_{route_id}",
                    'type': insight.insight_type,
                    'title': insight.title,
                    'description': insight.description,
                    'impact_score': insight.impact_score,
                    'confidence': insight.confidence,
                    'recommendations': insight.recommendations,
                    'data': insight.metrics,
                    'timestamp': insight.timestamp
                })
        
        return jsonify({
            'success': True,
            'insights': insights,
            'total_insights': len(insights),
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_trend_recommendations(trend):
    """Generate recommendations based on trend analysis"""
    recommendations = []
    
    metric = trend.metric_name.lower()
    direction = trend.trend_direction
    change = abs(trend.change_percentage)
    
    if 'fuel' in metric and direction == 'declining':
        recommendations.extend([
            "Implement fuel-efficient driving training",
            "Review vehicle maintenance schedules",
            "Consider route optimization to reduce distance"
        ])
    elif 'duration' in metric and direction == 'declining':  # Longer duration is bad
        recommendations.extend([
            "Analyze traffic patterns and adjust schedules",
            "Review stop optimization algorithms",
            "Consider alternative routes during peak hours"
        ])
    elif direction == 'improving':
        recommendations.extend([
            "Document best practices from recent improvements",
            "Apply successful strategies to other routes",
            "Continue monitoring to maintain gains"
        ])
    else:
        recommendations.extend([
            "Investigate root causes of performance changes",
            "Collect additional data for better analysis",
            "Review operational procedures"
        ])
    
    if change > 20:
        recommendations.append("Consider immediate intervention due to significant change")
    
    return recommendations

@enhanced_dashboard_bp.route('/api/predictions/bulk', methods=['POST'])
def bulk_predictions():
    """Generate predictions for multiple routes"""
    try:
        data = request.get_json()
        routes = data.get('routes', [])
        analytics = get_analytics_engine()
        
        predictions = []
        for route_data in routes:
            try:
                prediction = analytics.predict_route_performance(route_data)
                predictions.append({
                    'route_id': route_data.get('route_id', 'unknown'),
                    'predicted_duration': round(prediction.predicted_duration, 2),
                    'predicted_fuel_cost': round(prediction.predicted_fuel_cost, 2),
                    'confidence_interval': [
                        round(prediction.confidence_interval[0], 2),
                        round(prediction.confidence_interval[1], 2)
                    ],
                    'risk_factors': prediction.risk_factors,
                    'optimization_suggestions': prediction.optimization_suggestions
                })
            except Exception as e:
                predictions.append({
                    'route_id': route_data.get('route_id', 'unknown'),
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'total_routes': len(routes),
            'successful_predictions': len([p for p in predictions if 'error' not in p])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
