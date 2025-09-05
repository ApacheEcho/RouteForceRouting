"""
Real-time WebSocket Handlers for RouteForce Routing
Provides live route updates, driver tracking, and collaborative features
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from flask import request, session
from flask_socketio import SocketIO, emit, join_room, leave_room

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and real-time updates"""

    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.active_connections = {}  # sid -> user_data
        self.active_routes = {}  # route_id -> route_data
        self.user_rooms = {}  # user_id -> room_id

        # Register event handlers
        self.register_handlers()

    def register_handlers(self):
        """Register all WebSocket event handlers"""

        @self.socketio.on("connect")
        def handle_connect():
            """Handle client connection"""
            try:
                user_id = session.get("user_id")
                username = session.get("username", "Anonymous")

                logger.info(f"Client connected: {request.sid}, User: {username}")

                # Store connection info
                self.active_connections[request.sid] = {
                    "user_id": user_id,
                    "username": username,
                    "connected_at": datetime.now(),
                    "last_activity": datetime.now(),
                }

                # Join user-specific room
                if user_id:
                    room_id = f"user_{user_id}"
                    join_room(room_id)
                    self.user_rooms[user_id] = room_id

                # Send welcome message
                emit(
                    "connected",
                    {
                        "message": f"Welcome {username}! Real-time updates enabled.",
                        "timestamp": datetime.now().isoformat(),
                        "active_users": len(self.active_connections),
                    },
                )

                # Broadcast user count update
                self.socketio.emit(
                    "user_count_update", {"active_users": len(self.active_connections)}
                )

            except Exception as e:
                logger.error(f"Error handling connect: {str(e)}")
                emit("error", {"message": "Connection error occurred"})

        @self.socketio.on("disconnect")
        def handle_disconnect():
            """Handle client disconnection"""
            try:
                if request.sid in self.active_connections:
                    user_data = self.active_connections[request.sid]
                    username = user_data.get("username", "Unknown")
                    user_id = user_data.get("user_id")

                    logger.info(f"Client disconnected: {request.sid}, User: {username}")

                    # Leave user room
                    if user_id and user_id in self.user_rooms:
                        leave_room(self.user_rooms[user_id])
                        del self.user_rooms[user_id]

                    # Remove connection
                    del self.active_connections[request.sid]

                    # Broadcast user count update
                    self.socketio.emit(
                        "user_count_update",
                        {"active_users": len(self.active_connections)},
                    )

            except Exception as e:
                logger.error(f"Error handling disconnect: {str(e)}")

        @self.socketio.on("join_route")
        def handle_join_route(data):
            """Handle joining a route room for real-time updates"""
            try:
                route_id = data.get("route_id")
                if not route_id:
                    emit("error", {"message": "Route ID required"})
                    return

                room_id = f"route_{route_id}"
                join_room(room_id)

                user_data = self.active_connections.get(request.sid, {})
                username = user_data.get("username", "Unknown")

                logger.info(f"User {username} joined route {route_id}")

                # Notify others in the room
                emit(
                    "user_joined_route",
                    {
                        "username": username,
                        "route_id": route_id,
                        "timestamp": datetime.now().isoformat(),
                    },
                    room=room_id,
                    include_self=False,
                )

                # Send confirmation
                emit(
                    "joined_route",
                    {
                        "route_id": route_id,
                        "message": f"Joined route {route_id} for real-time updates",
                    },
                )

            except Exception as e:
                logger.error(f"Error joining route: {str(e)}")
                emit("error", {"message": "Failed to join route"})

        @self.socketio.on("leave_route")
        def handle_leave_route(data):
            """Handle leaving a route room"""
            try:
                route_id = data.get("route_id")
                if not route_id:
                    emit("error", {"message": "Route ID required"})
                    return

                room_id = f"route_{route_id}"
                leave_room(room_id)

                user_data = self.active_connections.get(request.sid, {})
                username = user_data.get("username", "Unknown")

                logger.info(f"User {username} left route {route_id}")

                # Notify others in the room
                emit(
                    "user_left_route",
                    {
                        "username": username,
                        "route_id": route_id,
                        "timestamp": datetime.now().isoformat(),
                    },
                    room=room_id,
                    include_self=False,
                )

                # Send confirmation
                emit(
                    "left_route",
                    {"route_id": route_id, "message": f"Left route {route_id}"},
                )

            except Exception as e:
                logger.error(f"Error leaving route: {str(e)}")
                emit("error", {"message": "Failed to leave route"})

        @self.socketio.on("route_progress_update")
        def handle_route_progress(data):
            """Handle route progress updates from drivers"""
            try:
                route_id = data.get("route_id")
                progress = data.get("progress", {})

                if not route_id:
                    emit("error", {"message": "Route ID required"})
                    return

                # Update route progress
                room_id = f"route_{route_id}"
                progress_data = {
                    "route_id": route_id,
                    "progress": progress,
                    "timestamp": datetime.now().isoformat(),
                    "updated_by": self.active_connections.get(request.sid, {}).get(
                        "username", "Unknown"
                    ),
                }

                # Broadcast to all users watching this route
                self.socketio.emit("route_progress", progress_data, room=room_id)

                logger.info(f"Route {route_id} progress updated: {progress}")

            except Exception as e:
                logger.error(f"Error updating route progress: {str(e)}")
                emit("error", {"message": "Failed to update route progress"})

        @self.socketio.on("request_route_status")
        def handle_route_status_request(data):
            """Handle request for current route status"""
            try:
                route_id = data.get("route_id")
                if not route_id:
                    emit("error", {"message": "Route ID required"})
                    return

                # Get route status (this would integrate with your routing service)
                route_status = self.get_route_status(route_id)

                emit(
                    "route_status",
                    {
                        "route_id": route_id,
                        "status": route_status,
                        "timestamp": datetime.now().isoformat(),
                    },
                )

            except Exception as e:
                logger.error(f"Error getting route status: {str(e)}")
                emit("error", {"message": "Failed to get route status"})

        @self.socketio.on("ping")
        def handle_ping():
            """Handle ping for connection health check"""
            try:
                # Update last activity
                if request.sid in self.active_connections:
                    self.active_connections[request.sid][
                        "last_activity"
                    ] = datetime.now()

                emit("pong", {"timestamp": datetime.now().isoformat()})

            except Exception as e:
                logger.error(f"Error handling ping: {str(e)}")

    def broadcast_route_update(self, route_id: str, update_data: dict[str, Any]):
        """Broadcast route update to all connected clients"""
        try:
            room_id = f"route_{route_id}"
            update_data["timestamp"] = datetime.now().isoformat()

            self.socketio.emit("route_update", update_data, room=room_id)
            logger.info(f"Broadcasted route update for {route_id}")

        except Exception as e:
            logger.error(f"Error broadcasting route update: {str(e)}")

    def broadcast_optimization_progress(self, route_id: str, progress: dict[str, Any]):
        """Broadcast optimization progress to interested clients"""
        try:
            room_id = f"route_{route_id}"
            progress_data = {
                "route_id": route_id,
                "optimization_progress": progress,
                "timestamp": datetime.now().isoformat(),
            }

            self.socketio.emit("optimization_progress", progress_data, room=room_id)
            logger.info(f"Broadcasted optimization progress for {route_id}")

        except Exception as e:
            logger.error(f"Error broadcasting optimization progress: {str(e)}")

    def notify_user(self, user_id: int, notification: dict[str, Any]):
        """Send notification to specific user"""
        try:
            if user_id in self.user_rooms:
                room_id = self.user_rooms[user_id]
                notification["timestamp"] = datetime.now().isoformat()

                self.socketio.emit("notification", notification, room=room_id)
                logger.info(f"Sent notification to user {user_id}")

        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")

    def get_route_status(self, route_id: str) -> dict[str, Any]:
        """Get current route status (placeholder for integration)"""
        # This would integrate with your routing service
        return {
            "id": route_id,
            "status": "active",
            "completion_percentage": 0,
            "current_location": None,
            "estimated_completion": None,
        }

    def get_active_users(self) -> list[dict[str, Any]]:
        """Get list of active users"""
        return [
            {
                "username": data["username"],
                "connected_at": data["connected_at"].isoformat(),
                "last_activity": data["last_activity"].isoformat(),
            }
            for data in self.active_connections.values()
        ]

    def cleanup_inactive_connections(self):
        """Clean up inactive connections (call periodically)"""
        current_time = datetime.now()
        inactive_threshold = 300  # 5 minutes

        inactive_sids = [
            sid
            for sid, data in self.active_connections.items()
            if (current_time - data["last_activity"]).seconds > inactive_threshold
        ]

        for sid in inactive_sids:
            logger.info(f"Cleaning up inactive connection: {sid}")
            if sid in self.active_connections:
                del self.active_connections[sid]


def init_websocket(app, socketio):
    """Initialize WebSocket functionality"""
    websocket_manager = WebSocketManager(socketio)

    # Store manager in app context for access from other modules
    app.websocket_manager = websocket_manager

    return websocket_manager
