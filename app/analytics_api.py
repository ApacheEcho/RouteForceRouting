"""
Advanced Analytics API Blueprint
Provides endpoints for AI-powered route insights and predictions
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import json
from typing import Dict, Any, List

from app.analytics_ai import get_analytics_engine, RouteInsight, PredictionResult, PerformanceTrend
from app.auth_decorators import analytics_access_required, admin_required, dispatcher_required, optional_auth, audit_log
from app.performance_monitor import get_performance_monitor

analytics_bp = Blueprint('analytics_ai', __name__)

@analytics_bp.route('/insights/route/<route_id>', methods=['GET'])
@analytics_access_required
@audit_log('view_route_insights', 'route_insight')
def get_route_insights(route_id: str):
    """Get AI-powered insights for a specific route"""
    try:
        analytics = get_analytics_engine()
        
        # Get route data (in real app, this would come from database)
        # For demo, we'll use sample data or request parameters
        route_data = {
            'distance': float(request.args.get('distance', 25.5)),
            'duration': float(request.args.get('duration', 85.0)),
            'stops': request.args.get('stops', '5').split(','),
            'fuel_used': float(request.args.get('fuel_used', 3.2)),
            'timestamp': request.args.get('timestamp', datetime.now().isoformat())
        }
        
        # Generate insight
        insight = analytics.analyze_route_efficiency(route_id, route_data)
        
        # Add to historical data for learning
        route_data['route_id'] = route_id
        analytics.add_route_data(route_data)
        
        return jsonify({
            'success': True,
            'insight': {
                'route_id': insight.route_id,
                'type': insight.insight_type,
                'title': insight.title,
                'description': insight.description,
                'impact_score': insight.impact_score,
                'confidence': insight.confidence,
                'recommendations': insight.recommendations,
                'metrics': insight.metrics,
                'timestamp': insight.timestamp
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating route insights: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate route insights'
        }), 500

@analytics_bp.route('/predict/route', methods=['POST'])
@analytics_access_required
@audit_log('predict_route_performance', 'route_performance')
def predict_route_performance():
    """Predict route performance using AI models"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No route data provided'
            }), 400
        
        analytics = get_analytics_engine()
        
        # Enrich the route data with time-based features
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
        
        dt = datetime.fromisoformat(data['timestamp'])
        data.update({
            'hour_of_day': dt.hour,
            'day_of_week': dt.weekday(),
            'is_weekend': dt.weekday() >= 5,
            'is_rush_hour': dt.hour in [7, 8, 9, 17, 18, 19]
        })
        
        # Calculate derived features
        if 'distance' in data and 'stops_count' in data:
            data['avg_stop_distance'] = data['distance'] / max(data['stops_count'], 1)
        
        # Generate prediction
        prediction = analytics.predict_route_performance(data)
        
        return jsonify({
            'success': True,
            'prediction': {
                'route_id': prediction.route_id,
                'predicted_duration': round(prediction.predicted_duration, 1),
                'predicted_duration_minutes': round(prediction.predicted_duration, 1),
                'predicted_fuel_cost': round(prediction.predicted_fuel_cost, 2),
                'confidence_interval': {
                    'min_duration': round(prediction.confidence_interval[0], 1),
                    'max_duration': round(prediction.confidence_interval[1], 1)
                },
                'risk_factors': prediction.risk_factors,
                'optimization_suggestions': prediction.optimization_suggestions
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error predicting route performance: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to predict route performance'
        }), 500

@analytics_bp.route('/trends', methods=['GET'])
@analytics_access_required
@audit_log('view_performance_trends', 'performance_trend')
def get_performance_trends():
    """Get performance trends analysis"""
    try:
        timeframe_days = int(request.args.get('timeframe_days', 30))
        analytics = get_analytics_engine()
        
        trends = analytics.detect_performance_trends(timeframe_days)
        
        return jsonify({
            'success': True,
            'timeframe_days': timeframe_days,
            'trends': [
                {
                    'metric_name': trend.metric_name,
                    'current_value': round(trend.current_value, 2),
                    'trend_direction': trend.trend_direction,
                    'change_percentage': round(trend.change_percentage, 1),
                    'forecast_7d': round(trend.forecast_7d, 2),
                    'forecast_30d': round(trend.forecast_30d, 2)
                }
                for trend in trends
            ]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting performance trends: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get performance trends'
        }), 500

@analytics_bp.route('/fleet/insights', methods=['GET'])
@analytics_access_required
@audit_log('view_fleet_insights', 'fleet_insight')
def get_fleet_insights():
    """Get comprehensive fleet insights and recommendations"""
    try:
        analytics = get_analytics_engine()
        insights = analytics.get_fleet_insights()
        
        return jsonify({
            'success': True,
            'fleet_insights': insights
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting fleet insights: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get fleet insights'
        }), 500

@analytics_bp.route('/insights/batch', methods=['POST'])
@analytics_access_required
@audit_log('analyze_multiple_routes', 'batch_insight')
def analyze_multiple_routes():
    """Analyze multiple routes for batch insights"""
    try:
        data = request.get_json()
        if not data or 'routes' not in data:
            return jsonify({
                'success': False,
                'error': 'No routes data provided'
            }), 400
        
        analytics = get_analytics_engine()
        results = []
        
        for route_data in data['routes']:
            route_id = route_data.get('id', f"route_{len(results)}")
            
            # Generate insight for each route
            insight = analytics.analyze_route_efficiency(route_id, route_data)
            
            # Add to historical data
            route_data['route_id'] = route_id
            analytics.add_route_data(route_data)
            
            results.append({
                'route_id': insight.route_id,
                'type': insight.insight_type,
                'title': insight.title,
                'description': insight.description,
                'impact_score': insight.impact_score,
                'confidence': insight.confidence,
                'recommendations': insight.recommendations,
                'metrics': insight.metrics
            })
        
        # Generate summary statistics
        total_impact = sum(r['impact_score'] for r in results)
        avg_impact = total_impact / len(results) if results else 0
        
        high_impact_routes = [r for r in results if r['impact_score'] >= 70]
        
        return jsonify({
            'success': True,
            'summary': {
                'total_routes_analyzed': len(results),
                'average_impact_score': round(avg_impact, 1),
                'high_impact_routes': len(high_impact_routes),
                'analysis_timestamp': datetime.now().isoformat()
            },
            'insights': results
        })
        
    except Exception as e:
        current_app.logger.error(f"Error analyzing multiple routes: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze routes'
        }), 500

@analytics_bp.route('/recommendations/smart', methods=['GET'])
@analytics_access_required
@audit_log('get_smart_recommendations', 'smart_recommendation')
def get_smart_recommendations():
    """Get AI-powered smart recommendations for route optimization"""
    try:
        # Get request parameters
        vehicle_count = int(request.args.get('vehicle_count', 3))
        time_window = request.args.get('time_window', 'morning')  # morning, afternoon, evening
        priority = request.args.get('priority', 'efficiency')  # efficiency, speed, cost
        
        analytics = get_analytics_engine()
        
        # Generate contextual recommendations based on historical patterns
        recommendations = []
        
        # Time-based recommendations
        if time_window == 'morning':
            recommendations.extend([
                "Schedule deliveries before 9 AM to avoid rush hour traffic",
                "Start with residential areas where people are home",
                "Consider breakfast/coffee stops for driver efficiency"
            ])
        elif time_window == 'afternoon':
            recommendations.extend([
                "Focus on commercial deliveries during business hours",
                "Avoid school zones between 2-4 PM",
                "Plan for lunch breaks in route optimization"
            ])
        else:  # evening
            recommendations.extend([
                "Prioritize residential deliveries when people are home",
                "Avoid dinner time (5-7 PM) for commercial stops",
                "Consider well-lit routes for safety"
            ])
        
        # Priority-based recommendations
        if priority == 'efficiency':
            recommendations.extend([
                "Use clustering algorithms to group nearby stops",
                "Minimize left turns to reduce waiting time",
                "Consider driver familiarity with routes"
            ])
        elif priority == 'speed':
            recommendations.extend([
                "Prioritize highway routes over city streets",
                "Use real-time traffic data for dynamic routing",
                "Consider express delivery time windows"
            ])
        else:  # cost
            recommendations.extend([
                "Optimize for minimum fuel consumption",
                "Consolidate stops to reduce total distance",
                "Consider vehicle capacity optimization"
            ])
        
        # Vehicle-specific recommendations
        if vehicle_count > 5:
            recommendations.append("Consider fleet coordination to avoid overlapping territories")
        elif vehicle_count == 1:
            recommendations.append("Single vehicle - optimize for sequential efficiency")
        
        # Get insights from historical data
        fleet_insights = analytics.get_fleet_insights()
        if fleet_insights.get('recommendations') and isinstance(fleet_insights['recommendations'], list):
            recommendations.extend(fleet_insights['recommendations'][:3])
        
        return jsonify({
            'success': True,
            'recommendations': {
                'smart_suggestions': recommendations[:8],  # Limit to top 8
                'context': {
                    'vehicle_count': vehicle_count,
                    'time_window': time_window,
                    'priority': priority,
                    'generated_at': datetime.now().isoformat()
                },
                'confidence': 0.85,
                'based_on': 'Historical data analysis and contextual factors'
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating smart recommendations: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate recommendations'
        }), 500

@analytics_bp.route('/demo/populate', methods=['POST'])
@admin_required
@audit_log('populate_demo_data', 'demo_data')
def populate_demo_data():
    """Populate the analytics engine with demo data for testing"""
    try:
        analytics = get_analytics_engine()
        
        # Generate diverse demo route data
        import random
        from datetime import datetime, timedelta
        
        demo_routes = []
        base_time = datetime.now() - timedelta(days=60)
        
        for i in range(100):
            # Vary parameters realistically
            stops_count = random.randint(3, 15)
            distance = stops_count * random.uniform(1.5, 4.0)  # km per stop
            
            # Time varies based on stops and traffic
            base_time_per_stop = random.uniform(8, 20)  # minutes
            traffic_factor = random.uniform(0.8, 1.4)
            duration = stops_count * base_time_per_stop * traffic_factor
            
            # Fuel varies with distance and efficiency
            fuel_efficiency = random.uniform(7, 12)  # km per liter
            fuel_used = distance / fuel_efficiency
            
            # Time progression
            route_time = base_time + timedelta(days=i/2, hours=random.randint(7, 18))
            
            route_data = {
                'route_id': f"demo_route_{i+1:03d}",
                'distance': round(distance, 1),
                'duration': round(duration, 1),
                'stops_count': stops_count,
                'fuel_used': round(fuel_used, 2),
                'timestamp': route_time.isoformat(),
                'driver_id': f"driver_{random.randint(1, 10)}",
                'vehicle_type': random.choice(['van', 'truck', 'car'])
            }
            
            analytics.add_route_data(route_data)
            demo_routes.append(route_data)
        
        return jsonify({
            'success': True,
            'message': f'Successfully populated {len(demo_routes)} demo routes',
            'sample_data': demo_routes[:5]  # Show first 5 for verification
        })
        
    except Exception as e:
        current_app.logger.error(f"Error populating demo data: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to populate demo data'
        }), 500

@analytics_bp.route('/predict/advanced', methods=['POST'])
@analytics_access_required
@audit_log('predict_advanced_route_performance', 'advanced_prediction')
def predict_advanced_route_performance():
    """Predict route performance using advanced ensemble models with uncertainty quantification"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No route data provided'
            }), 400
        
        analytics = get_analytics_engine()
        
        # Enrich the route data with time-based features
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
        
        dt = datetime.fromisoformat(data['timestamp'])
        data.update({
            'hour_of_day': dt.hour,
            'day_of_week': dt.weekday(),
            'is_weekend': dt.weekday() >= 5,
            'is_rush_hour': dt.hour in [7, 8, 9, 17, 18, 19]
        })
        
        # Calculate derived features
        if 'distance' in data and 'stops_count' in data:
            data['avg_stop_distance'] = data['distance'] / max(data['stops_count'], 1)
        
        # Generate advanced prediction with uncertainty quantification
        prediction = analytics.predict_with_advanced_models(data)
        
        return jsonify({
            'success': True,
            'prediction': {
                'route_id': prediction.route_id,
                'predicted_duration': round(prediction.predicted_duration, 2),
                'predicted_fuel_cost': round(prediction.predicted_fuel_cost, 2),
                'uncertainty': {
                    'mean_prediction': round(prediction.uncertainty.mean_prediction, 2),
                    'std_prediction': round(prediction.uncertainty.std_prediction, 2),
                    'confidence_interval_95': [
                        round(prediction.uncertainty.confidence_interval_95[0], 2),
                        round(prediction.uncertainty.confidence_interval_95[1], 2)
                    ],
                    'model_confidence': round(prediction.uncertainty.model_confidence, 3),
                    'epistemic_uncertainty': round(prediction.uncertainty.epistemic_uncertainty, 2),
                    'aleatoric_uncertainty': round(prediction.uncertainty.aleatoric_uncertainty, 2)
                },
                'risk_factors': prediction.risk_factors,
                'optimization_suggestions': prediction.optimization_suggestions,
                'feature_importance': {
                    k: round(v, 3) for k, v in prediction.feature_importance.items()
                },
                'explainability': prediction.model_explainability
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in advanced route prediction: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to predict advanced route performance'
        }), 500

@analytics_bp.route('/performance/monitor', methods=['GET'])
@analytics_access_required
@audit_log('view_performance_monitoring', 'performance_monitoring')
def get_performance_monitoring():
    """Get real-time performance monitoring data"""
    try:
        monitor = get_performance_monitor()
        
        # Get current metrics
        current_metrics = monitor.get_current_metrics()
        
        # Get active alerts
        alerts = monitor.get_active_alerts()
        
        # Get health score
        health_score = monitor.get_system_health_score()
        
        return jsonify({
            'success': True,
            'monitoring': {
                'current_metrics': current_metrics,
                'active_alerts': alerts,
                'health_score': health_score,
                'monitoring_status': 'active' if monitor.monitoring_active else 'inactive'
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving performance monitoring: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve performance monitoring data'
        }), 500

@analytics_bp.route('/ensemble/status', methods=['GET'])
@analytics_access_required
@audit_log('view_ensemble_status', 'ml_ensemble')
def get_ensemble_status():
    """Get status of advanced ML ensemble models"""
    try:
        analytics = get_analytics_engine()
        
        ensemble_status = {
            'advanced_models_trained': analytics.advanced_models_trained,
            'historical_data_count': len(analytics.historical_data),
            'feature_columns': analytics.feature_columns,
            'basic_model_available': analytics.route_predictor is not None,
            'anomaly_detector_available': analytics.anomaly_detector is not None
        }
        
        if hasattr(analytics.ensemble_engine, 'model_metadata'):
            ensemble_status.update({
                'ensemble_metadata': analytics.ensemble_engine.model_metadata
            })
        
        return jsonify({
            'success': True,
            'ensemble_status': ensemble_status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving ensemble status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve ensemble status'
        }), 500
