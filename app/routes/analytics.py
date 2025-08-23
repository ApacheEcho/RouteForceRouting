from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, List, Any
from app.models.database import User

analytics_bp = Blueprint('analytics', __name__)

def require_admin(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not getattr(user, 'is_admin', False):
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated

@analytics_bp.route('/api/analytics/dashboard', methods=['GET'])
@require_admin
def get_dashboard_analytics():
    """Get comprehensive dashboard analytics"""
    try:
        # Get query parameters
        days = int(request.args.get('days', 30))
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        # Calculate date range
        if not start_date:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        # Fetch analytics data
        analytics_data = {
            'overview': get_overview_stats(start_date, end_date),
            'routing_performance': get_routing_performance(start_date, end_date),
            'usage_trends': get_usage_trends(start_date, end_date),
            'cost_analysis': get_cost_analysis(start_date, end_date),
            'top_routes': get_top_routes(start_date, end_date)
        }
        return jsonify({
            'status': 'success',
            'data': analytics_data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': f'Failed to fetch analytics: {str(e)}'}), 500

@analytics_bp.route('/api/analytics/route-efficiency', methods=['GET'])
@require_admin
def get_route_efficiency():
    """Get route efficiency metrics"""
    try:
        route_id = request.args.get('route_id')
        days = int(request.args.get('days', 30))
        if not route_id:
            return jsonify({'error': 'route_id parameter required'}), 400
        efficiency_data = calculate_route_efficiency(route_id, days)
        return jsonify({
            'status': 'success',
            'route_id': route_id,
            'efficiency_data': efficiency_data
        })
    except Exception as e:
        return jsonify({'error': f'Failed to calculate efficiency: {str(e)}'}), 500

@analytics_bp.route('/api/analytics/export', methods=['GET'])
@require_admin
def export_analytics():
    """Export analytics data in CSV format"""
    try:
        report_type = request.args.get('type', 'summary')
        format_type = request.args.get('format', 'csv')
        days = int(request.args.get('days', 30))
        # Generate export data based on type
        if report_type == 'detailed':
            data = generate_detailed_report(days)
        else:
            data = generate_summary_report(days)
        # Return JSON for now (CSV implementation would require additional libraries)
        return jsonify({
            'status': 'success',
            'report_type': report_type,
            'format': format_type,
            'data': data,
            'generated_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

# Helper functions (unchanged, can be moved to a utils module if needed)
def get_overview_stats(start_date: str, end_date: str) -> Dict[str, Any]:
    return {
        'total_routes': 1250,
        'active_users': 45,
        'total_distance': 25000,  # km
        'avg_optimization_savings': 15.5,  # percentage
        'api_calls': 3200,
        'success_rate': 98.7
    }

def get_routing_performance(start_date: str, end_date: str) -> Dict[str, Any]:
    return {
        'avg_calculation_time': 0.45,  # seconds
        'fastest_route_time': 0.12,
        'slowest_route_time': 2.34,
        'time_by_algorithm': {
            'dijkstra': 0.42,
            'a_star': 0.38,
            'constrained': 0.67
        }
    }

def get_usage_trends(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    return [
        {'date': '2024-01-01', 'routes': 45, 'users': 12},
        {'date': '2024-01-02', 'routes': 52, 'users': 15},
        {'date': '2024-01-03', 'routes': 48, 'users': 14},
    ]

def get_cost_analysis(start_date: str, end_date: str) -> Dict[str, Any]:
    return {
        'estimated_savings': 12500,  # dollars
        'fuel_savings': 3200,  # liters
        'time_savings': 156,  # hours
        'co2_reduction': 8900  # kg
    }

def get_top_routes(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    return [
        {'route_id': 'route_001', 'frequency': 127, 'avg_distance': 45.2},
        {'route_id': 'route_002', 'frequency': 98, 'avg_distance': 32.1},
        {'route_id': 'route_003', 'frequency': 87, 'avg_distance': 67.8}
    ]

def calculate_route_efficiency(route_id: str, days: int) -> Dict[str, Any]:
    return {
        'route_id': route_id,
        'efficiency_score': 87.5,
        'improvement_opportunities': [
            'Optimize waypoint order',
            'Consider alternative routes during peak hours'
        ],
        'historical_comparison': {
            'current_period': 87.5,
            'previous_period': 82.3,
            'improvement': 5.2
        }
    }

def generate_summary_report(days: int) -> Dict[str, Any]:
    return {
        'period': f'Last {days} days',
        'summary': get_overview_stats('', ''),
        'key_insights': [
            '23% increase in API usage compared to last month',
            'Route optimization savings improved by 5%',
            'Peak usage hours: 9-11 AM and 2-4 PM'
        ]
    }

def generate_detailed_report(days: int) -> Dict[str, Any]:
    return {
        'period': f'Last {days} days',
        'detailed_metrics': {
            'hourly_usage': [25, 30, 28, 45, 67, 89, 156, 234, 198, 167, 145, 132, 120, 110, 95, 87, 78, 92, 123, 156, 134, 98, 67, 45],
            'algorithm_performance': {
                'dijkstra': {'avg_time': 0.42, 'success_rate': 99.1},
                'a_star': {'avg_time': 0.38, 'success_rate': 98.9},
                'constrained': {'avg_time': 0.67, 'success_rate': 97.5}
            }
        }
    }