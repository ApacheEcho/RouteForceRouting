from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.database import User
from datetime import datetime

activity_bp = Blueprint('activity', __name__)

@activity_bp.route('/api/analytics/user-activity', methods=['GET'])
@jwt_required()
def get_user_activity():
    """Get current user's activity analytics"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        activity_data = {
            'user_id': user_id,
            'monthly_usage': get_user_monthly_usage(user_id),
            'favorite_routes': get_user_favorite_routes(user_id),
            'performance_stats': get_user_performance_stats(user_id)
        }

        return jsonify({
            'status': 'success',
            'data': activity_data
        })
    except Exception as e:
        return jsonify({'error': f'Failed to fetch activity: {str(e)}'}), 500

def get_user_monthly_usage(user_id):
    """Get user's monthly API usage (stubbed)"""
    return {
        'routes_created': 45,
        'api_calls': 127,
        'avg_routes_per_day': 1.5,
        'peak_usage_day': 'Wednesday'
    }

def get_user_favorite_routes(user_id):
    """Get user's most frequently used routes (stubbed)"""
    return [
        {'route_name': 'Daily Commute', 'frequency': 22, 'last_used': '2024-01-03'},
        {'route_name': 'Client Visits', 'frequency': 18, 'last_used': '2024-01-02'},
        {'route_name': 'Warehouse Runs', 'frequency': 15, 'last_used': '2024-01-03'}
    ]

def get_user_performance_stats(user_id):
    """Get user's performance statistics (stubbed)"""
    return {
        'optimization_achievements': 12,
        'routes_shared': 8,
        'collaboration_score': 78
    }
