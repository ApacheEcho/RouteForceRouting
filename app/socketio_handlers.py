"""
WebSocket handlers for real-time features
"""
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request, current_app
from app.monitoring import metrics_collector
import logging
import json
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')

# Store connected clients
connected_clients = {}
active_routes = {}

@socketio.on('connect')
def handle_connect():
    """Handle new client connection"""
    client_id = request.sid
    connected_clients[client_id] = {
        'connected_at': time.time(),
        'ip': request.remote_addr,
        'rooms': []
    }
    
    logger.info(f"Client {client_id} connected from {request.remote_addr}")
    
    # Send initial metrics
    try:
        metrics = metrics_collector.get_metrics()
        emit('metrics_update', metrics)
    except Exception as e:
        logger.error(f"Error sending initial metrics: {e}")
    
    # Update connection count
    emit('connection_count', len(connected_clients), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    client_id = request.sid
    
    if client_id in connected_clients:
        # Leave all rooms
        for room in connected_clients[client_id]['rooms']:
            leave_room(room)
        
        # Remove from connected clients
        del connected_clients[client_id]
        
        logger.info(f"Client {client_id} disconnected")
    
    # Update connection count
    emit('connection_count', len(connected_clients), broadcast=True)

@socketio.on('join_dashboard')
def handle_join_dashboard():
    """Handle client joining dashboard room"""
    client_id = request.sid
    room = 'dashboard'
    
    join_room(room)
    
    if client_id in connected_clients:
        connected_clients[client_id]['rooms'].append(room)
    
    logger.info(f"Client {client_id} joined dashboard room")
    
    # Send current metrics to the new dashboard client
    try:
        metrics = metrics_collector.get_metrics()
        emit('metrics_update', metrics, room=room)
    except Exception as e:
        logger.error(f"Error sending metrics to dashboard: {e}")

@socketio.on('leave_dashboard')
def handle_leave_dashboard():
    """Handle client leaving dashboard room"""
    client_id = request.sid
    room = 'dashboard'
    
    leave_room(room)
    
    if client_id in connected_clients and room in connected_clients[client_id]['rooms']:
        connected_clients[client_id]['rooms'].remove(room)
    
    logger.info(f"Client {client_id} left dashboard room")

@socketio.on('start_route_tracking')
def handle_start_route_tracking(data):
    """Handle starting route tracking"""
    client_id = request.sid
    route_id = data.get('route_id')
    
    if not route_id:
        emit('error', {'message': 'Route ID required'})
        return
    
    room = f'route_{route_id}'
    join_room(room)
    
    if client_id in connected_clients:
        connected_clients[client_id]['rooms'].append(room)
    
    # Initialize route tracking
    active_routes[route_id] = {
        'created_at': time.time(),
        'clients': [client_id],
        'current_stop': 0,
        'total_stops': data.get('total_stops', 0),
        'status': 'active'
    }
    
    logger.info(f"Started route tracking for route {route_id}")
    
    # Send route status
    emit('route_status', {
        'route_id': route_id,
        'status': 'started',
        'current_stop': 0,
        'total_stops': active_routes[route_id]['total_stops']
    }, room=room)

@socketio.on('update_route_progress')
def handle_route_progress(data):
    """Handle route progress updates"""
    route_id = data.get('route_id')
    current_stop = data.get('current_stop', 0)
    location = data.get('location', {})
    
    if route_id not in active_routes:
        emit('error', {'message': 'Route not found'})
        return
    
    # Update route progress
    active_routes[route_id]['current_stop'] = current_stop
    active_routes[route_id]['last_update'] = time.time()
    
    room = f'route_{route_id}'
    
    # Broadcast progress update
    emit('route_progress', {
        'route_id': route_id,
        'current_stop': current_stop,
        'total_stops': active_routes[route_id]['total_stops'],
        'location': location,
        'timestamp': time.time()
    }, room=room)
    
    logger.info(f"Route {route_id} progress: {current_stop}/{active_routes[route_id]['total_stops']}")

@socketio.on('request_metrics')
def handle_metrics_request():
    """Handle request for current metrics"""
    try:
        metrics = metrics_collector.get_metrics()
        
        # Add real-time data
        metrics['connected_clients'] = len(connected_clients)
        metrics['active_routes'] = len(active_routes)
        
        emit('metrics_update', metrics)
    except Exception as e:
        logger.error(f"Error sending metrics: {e}")
        emit('error', {'message': 'Failed to get metrics'})

@socketio.on('ping')
def handle_ping():
    """Handle ping for connection testing"""
    emit('pong', {'timestamp': time.time()})

def broadcast_metrics_update():
    """Broadcast metrics update to all dashboard clients"""
    try:
        metrics = metrics_collector.get_metrics()
        
        # Add real-time connection data
        metrics['connected_clients'] = len(connected_clients)
        metrics['active_routes'] = len(active_routes)
        
        socketio.emit('metrics_update', metrics, room='dashboard')
    except Exception as e:
        logger.error(f"Error broadcasting metrics: {e}")

def broadcast_route_update(route_id: str, update_data: Dict[str, Any]):
    """Broadcast route update to all clients tracking the route"""
    room = f'route_{route_id}'
    socketio.emit('route_update', {
        'route_id': route_id,
        'data': update_data,
        'timestamp': time.time()
    }, room=room)

def broadcast_system_alert(alert_type: str, message: str, severity: str = 'info'):
    """Broadcast system alert to all connected clients"""
    socketio.emit('system_alert', {
        'type': alert_type,
        'message': message,
        'severity': severity,
        'timestamp': time.time()
    }, broadcast=True)

def get_connection_stats() -> Dict[str, Any]:
    """Get current connection statistics"""
    return {
        'connected_clients': len(connected_clients),
        'active_routes': len(active_routes),
        'rooms': {
            'dashboard': len([c for c in connected_clients.values() if 'dashboard' in c['rooms']]),
            'route_tracking': len([c for c in connected_clients.values() if any(r.startswith('route_') for r in c['rooms'])])
        }
    }

# Background task to send periodic updates
def background_thread():
    """Background thread for periodic updates"""
    import threading
    import time
    
    def update_loop():
        while True:
            try:
                # Wait for SocketIO to be initialized
                if not hasattr(socketio, 'server') or socketio.server is None:
                    time.sleep(5)
                    continue
                    
                # Send metrics update every 10 seconds
                broadcast_metrics_update()
                
                # Check for stale routes (cleanup after 1 hour)
                current_time = time.time()
                stale_routes = [
                    route_id for route_id, route_data in active_routes.items()
                    if current_time - route_data.get('last_update', route_data['created_at']) > 3600
                ]
                
                for route_id in stale_routes:
                    del active_routes[route_id]
                    logger.info(f"Cleaned up stale route: {route_id}")
                
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in background thread: {e}")
                time.sleep(5)
    
    # Start background thread
    thread = threading.Thread(target=update_loop, daemon=True)
    thread.start()

def start_background_thread():
    """Start the background thread after SocketIO is initialized"""
    background_thread()

# Don't start background thread immediately - wait for explicit call
# background_thread()
