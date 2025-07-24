"""
Real-time WebSocket Manager for RouteForce
Handles real-time route updates, driver tracking, and notifications
"""

from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask import request, current_app
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import logging
from dataclasses import dataclass, asdict
from threading import Lock
import uuid

# Thread-safe storage for active connections and data
active_connections = {}
route_updates = {}
driver_locations = {}
connection_lock = Lock()


@dataclass
class ConnectionInfo:
    """Connection information for a client"""

    session_id: str
    user_id: str
    user_type: str  # 'driver', 'dispatcher', 'admin'
    connected_at: datetime
    last_activity: datetime
    rooms: List[str]


@dataclass
class RouteUpdate:
    """Real-time route update"""

    route_id: str
    status: str
    current_stop: int
    total_stops: int
    estimated_completion: str
    distance_remaining: float
    driver_id: str
    timestamp: str
    coordinates: Optional[Dict[str, float]] = None


@dataclass
class DriverLocation:
    """Real-time driver location"""

    driver_id: str
    latitude: float
    longitude: float
    heading: float
    speed: float
    timestamp: str
    route_id: Optional[str] = None


def init_websocket(socketio: SocketIO):
    """Initialize WebSocket event handlers"""

    @socketio.on("connect")
    def handle_connect(auth=None):
        """Handle client connection"""
        session_id = request.sid
        user_id = (
            auth.get("user_id", f"anonymous_{uuid.uuid4().hex[:8]}")
            if auth
            else f"anonymous_{uuid.uuid4().hex[:8]}"
        )
        user_type = auth.get("user_type", "guest") if auth else "guest"

        # Create connection info
        connection_info = ConnectionInfo(
            session_id=session_id,
            user_id=user_id,
            user_type=user_type,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
            rooms=[],
        )

        with connection_lock:
            active_connections[session_id] = connection_info

        # Send welcome message
        emit(
            "connection_established",
            {
                "session_id": session_id,
                "user_id": user_id,
                "server_time": datetime.now().isoformat(),
                "message": "Connected to RouteForce real-time updates",
            },
        )

        # Send current system status
        emit("system_status", get_system_status())

        logging.info(
            f"Client connected: {user_id} ({user_type}) - Session: {session_id}"
        )

    @socketio.on("disconnect")
    def handle_disconnect():
        """Handle client disconnection"""
        session_id = request.sid

        with connection_lock:
            if session_id in active_connections:
                connection_info = active_connections[session_id]
                # Leave all rooms
                for room in connection_info.rooms:
                    leave_room(room)

                logging.info(
                    f"Client disconnected: {connection_info.user_id} - Session: {session_id}"
                )
                del active_connections[session_id]

    @socketio.on("join_route_updates")
    def handle_join_route_updates(data):
        """Join room for route-specific updates"""
        session_id = request.sid
        route_id = data.get("route_id")

        if not route_id:
            emit("error", {"message": "Route ID required"})
            return

        room_name = f"route_{route_id}"
        join_room(room_name)

        with connection_lock:
            if session_id in active_connections:
                active_connections[session_id].rooms.append(room_name)
                active_connections[session_id].last_activity = datetime.now()

        emit(
            "joined_room",
            {
                "room": room_name,
                "route_id": route_id,
                "message": f"Subscribed to updates for route {route_id}",
            },
        )

        # Send current route status if available
        if route_id in route_updates:
            emit("route_update", asdict(route_updates[route_id]))

    @socketio.on("join_driver_tracking")
    def handle_join_driver_tracking(data):
        """Join room for driver tracking updates"""
        session_id = request.sid
        driver_id = data.get("driver_id")

        if not driver_id:
            emit("error", {"message": "Driver ID required"})
            return

        room_name = f"driver_{driver_id}"
        join_room(room_name)

        with connection_lock:
            if session_id in active_connections:
                active_connections[session_id].rooms.append(room_name)
                active_connections[session_id].last_activity = datetime.now()

        emit(
            "joined_room",
            {
                "room": room_name,
                "driver_id": driver_id,
                "message": f"Subscribed to tracking for driver {driver_id}",
            },
        )

        # Send current driver location if available
        if driver_id in driver_locations:
            emit("driver_location", asdict(driver_locations[driver_id]))

    @socketio.on("update_driver_location")
    def handle_driver_location_update(data):
        """Handle driver location update from mobile app"""
        session_id = request.sid

        with connection_lock:
            if session_id not in active_connections:
                emit("error", {"message": "Not authenticated"})
                return

            connection_info = active_connections[session_id]
            if connection_info.user_type != "driver":
                emit("error", {"message": "Only drivers can update locations"})
                return

        try:
            location = DriverLocation(
                driver_id=data["driver_id"],
                latitude=float(data["latitude"]),
                longitude=float(data["longitude"]),
                heading=float(data.get("heading", 0)),
                speed=float(data.get("speed", 0)),
                timestamp=datetime.now().isoformat(),
                route_id=data.get("route_id"),
            )

            # Store location
            driver_locations[location.driver_id] = location

            # Broadcast to subscribers
            socketio.emit(
                "driver_location", asdict(location), room=f"driver_{location.driver_id}"
            )

            # If on a route, also broadcast to route subscribers
            if location.route_id:
                socketio.emit(
                    "driver_location",
                    asdict(location),
                    room=f"route_{location.route_id}",
                )

            emit(
                "location_updated",
                {"status": "success", "timestamp": location.timestamp},
            )

        except (KeyError, ValueError, TypeError) as e:
            emit("error", {"message": f"Invalid location data: {str(e)}"})

    @socketio.on("update_route_status")
    def handle_route_status_update(data):
        """Handle route status update"""
        session_id = request.sid

        with connection_lock:
            if session_id not in active_connections:
                emit("error", {"message": "Not authenticated"})
                return

            connection_info = active_connections[session_id]
            if connection_info.user_type not in ["driver", "dispatcher", "admin"]:
                emit("error", {"message": "Insufficient permissions"})
                return

        try:
            route_update = RouteUpdate(
                route_id=data["route_id"],
                status=data["status"],
                current_stop=int(data.get("current_stop", 0)),
                total_stops=int(data.get("total_stops", 0)),
                estimated_completion=data.get("estimated_completion", ""),
                distance_remaining=float(data.get("distance_remaining", 0)),
                driver_id=data["driver_id"],
                timestamp=datetime.now().isoformat(),
                coordinates=data.get("coordinates"),
            )

            # Store update
            route_updates[route_update.route_id] = route_update

            # Broadcast to route subscribers
            socketio.emit(
                "route_update",
                asdict(route_update),
                room=f"route_{route_update.route_id}",
            )

            # Broadcast to all dispatchers and admins
            socketio.emit(
                "fleet_update",
                {"type": "route_status", "data": asdict(route_update)},
                room="dispatchers",
            )

            emit(
                "route_updated",
                {"status": "success", "timestamp": route_update.timestamp},
            )

        except (KeyError, ValueError, TypeError) as e:
            emit("error", {"message": f"Invalid route data: {str(e)}"})

    @socketio.on("join_fleet_updates")
    def handle_join_fleet_updates(data):
        """Join room for fleet-wide updates (dispatchers/admins)"""
        session_id = request.sid

        with connection_lock:
            if session_id not in active_connections:
                emit("error", {"message": "Not authenticated"})
                return

            connection_info = active_connections[session_id]
            if connection_info.user_type not in ["dispatcher", "admin"]:
                emit("error", {"message": "Insufficient permissions"})
                return

        join_room("dispatchers")

        with connection_lock:
            active_connections[session_id].rooms.append("dispatchers")
            active_connections[session_id].last_activity = datetime.now()

        emit(
            "joined_room",
            {"room": "dispatchers", "message": "Subscribed to fleet-wide updates"},
        )

        # Send current fleet status
        emit("fleet_status", get_fleet_status())

    @socketio.on("send_notification")
    def handle_send_notification(data):
        """Send notification to specific users or groups"""
        session_id = request.sid

        with connection_lock:
            if session_id not in active_connections:
                emit("error", {"message": "Not authenticated"})
                return

            connection_info = active_connections[session_id]
            if connection_info.user_type not in ["dispatcher", "admin"]:
                emit("error", {"message": "Insufficient permissions"})
                return

        notification = {
            "id": str(uuid.uuid4()),
            "type": data.get("type", "info"),
            "title": data.get("title", "Notification"),
            "message": data["message"],
            "sender": connection_info.user_id,
            "timestamp": datetime.now().isoformat(),
            "priority": data.get("priority", "normal"),
        }

        # Determine recipients
        target_type = data.get("target_type", "all")
        target_id = data.get("target_id")

        if target_type == "driver" and target_id:
            socketio.emit("notification", notification, room=f"driver_{target_id}")
        elif target_type == "route" and target_id:
            socketio.emit("notification", notification, room=f"route_{target_id}")
        elif target_type == "dispatchers":
            socketio.emit("notification", notification, room="dispatchers")
        else:
            # Broadcast to all connected clients
            socketio.emit("notification", notification)

        emit(
            "notification_sent",
            {
                "status": "success",
                "notification_id": notification["id"],
                "recipients": target_type,
            },
        )

    @socketio.on("get_active_connections")
    def handle_get_active_connections():
        """Get list of active connections (admin only)"""
        session_id = request.sid

        with connection_lock:
            if session_id not in active_connections:
                emit("error", {"message": "Not authenticated"})
                return

            connection_info = active_connections[session_id]
            if connection_info.user_type != "admin":
                emit("error", {"message": "Admin access required"})
                return

        connections_summary = []
        with connection_lock:
            for conn_info in active_connections.values():
                connections_summary.append(
                    {
                        "user_id": conn_info.user_id,
                        "user_type": conn_info.user_type,
                        "connected_at": conn_info.connected_at.isoformat(),
                        "last_activity": conn_info.last_activity.isoformat(),
                        "rooms": conn_info.rooms,
                    }
                )

        emit(
            "active_connections",
            {
                "total_connections": len(connections_summary),
                "connections": connections_summary,
            },
        )


def get_system_status() -> Dict[str, Any]:
    """Get current system status"""
    with connection_lock:
        return {
            "active_connections": len(active_connections),
            "active_routes": len(route_updates),
            "tracked_drivers": len(driver_locations),
            "server_time": datetime.now().isoformat(),
            "status": "operational",
        }


def get_fleet_status() -> Dict[str, Any]:
    """Get current fleet status"""
    active_routes = []
    for route_update in route_updates.values():
        active_routes.append(asdict(route_update))

    active_drivers = []
    for driver_location in driver_locations.values():
        active_drivers.append(asdict(driver_location))

    return {
        "active_routes": active_routes,
        "active_drivers": active_drivers,
        "total_active_routes": len(active_routes),
        "total_active_drivers": len(active_drivers),
        "last_updated": datetime.now().isoformat(),
    }


def broadcast_emergency_alert(alert_data: Dict[str, Any]):
    """Broadcast emergency alert to all connected clients"""
    from app import socketio

    emergency_notification = {
        "id": str(uuid.uuid4()),
        "type": "emergency",
        "title": "EMERGENCY ALERT",
        "message": alert_data.get("message", "Emergency situation detected"),
        "location": alert_data.get("location"),
        "timestamp": datetime.now().isoformat(),
        "priority": "critical",
    }

    socketio.emit("emergency_alert", emergency_notification)
    logging.critical(f"Emergency alert broadcasted: {emergency_notification}")


def cleanup_inactive_connections():
    """Clean up inactive connections (called periodically)"""
    cutoff_time = datetime.now() - timedelta(minutes=30)
    inactive_sessions = []

    with connection_lock:
        for session_id, conn_info in active_connections.items():
            if conn_info.last_activity < cutoff_time:
                inactive_sessions.append(session_id)

        for session_id in inactive_sessions:
            del active_connections[session_id]
            logging.info(f"Cleaned up inactive connection: {session_id}")

    return len(inactive_sessions)
