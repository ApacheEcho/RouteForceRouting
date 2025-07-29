"""
Real-time Analytics WebSocket Events
Extends the existing WebSocket system with AI analytics events
"""

from flask_socketio import emit
from flask import request
from datetime import datetime
from app.analytics_ai import get_analytics_engine
import json


def init_analytics_websocket_events(websocket_manager):
    """Initialize analytics-specific WebSocket events"""

    @websocket_manager.socketio.on("request_live_analytics")
    def handle_live_analytics_request(data):
        """Handle request for live analytics updates"""
        try:
            analytics = get_analytics_engine()

            # Get fleet insights
            fleet_insights = analytics.get_fleet_insights()

            # Get performance trends
            trends = analytics.detect_performance_trends()

            # Emit analytics update
            emit(
                "analytics_update",
                {
                    "type": "fleet_analytics",
                    "fleet_insights": fleet_insights,
                    "trends": [
                        trend.__dict__ if hasattr(trend, "__dict__") else trend
                        for trend in trends
                    ],
                    "timestamp": datetime.now().isoformat(),
                },
            )

        except Exception as e:
            emit("error", {"message": f"Error fetching analytics: {str(e)}"})

    @websocket_manager.socketio.on("request_route_prediction")
    def handle_route_prediction_request(data):
        """Handle real-time route prediction request"""
        try:
            analytics = get_analytics_engine()
            route_features = data.get("route_features", {})

            # Generate prediction
            prediction = analytics.predict_route_performance(route_features)

            # Emit prediction result
            emit(
                "route_prediction",
                {
                    "route_id": route_features.get("route_id", "unknown"),
                    "prediction": {
                        "predicted_duration": prediction.predicted_duration,
                        "predicted_fuel_cost": prediction.predicted_fuel_cost,
                        "confidence_interval": prediction.confidence_interval,
                        "risk_factors": prediction.risk_factors,
                        "optimization_suggestions": prediction.optimization_suggestions,
                    },
                    "timestamp": datetime.now().isoformat(),
                },
            )

        except Exception as e:
            emit("error", {"message": f"Error generating prediction: {str(e)}"})

    @websocket_manager.socketio.on("subscribe_analytics")
    def handle_analytics_subscription(data):
        """Subscribe to periodic analytics updates"""
        try:
            analytics_type = data.get("type", "fleet")
            interval = data.get("interval", 30)  # seconds

            # Add client to analytics subscription
            client_id = request.sid

            emit(
                "analytics_subscribed",
                {
                    "type": analytics_type,
                    "interval": interval,
                    "message": f"Subscribed to {analytics_type} analytics updates every {interval} seconds",
                },
            )

            # Note: Periodic updates would be handled by a background task

        except Exception as e:
            emit("error", {"message": f"Error subscribing to analytics: {str(e)}"})


def broadcast_analytics_insights(socketio, insight_data):
    """Broadcast analytics insights to all connected clients"""
    socketio.emit(
        "analytics_insight",
        {
            "type": "new_insight",
            "data": insight_data,
            "timestamp": datetime.now().isoformat(),
        },
    )


def broadcast_performance_alert(socketio, alert_data):
    """Broadcast performance alerts to supervisors"""
    socketio.emit(
        "performance_alert",
        {
            "type": "performance_degradation",
            "severity": alert_data.get("severity", "medium"),
            "message": alert_data.get("message"),
            "affected_routes": alert_data.get("routes", []),
            "recommended_actions": alert_data.get("actions", []),
            "timestamp": datetime.now().isoformat(),
        },
        room="supervisors",
    )
