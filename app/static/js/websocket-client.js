/**
 * Real-time WebSocket Client for RouteForce Routing
 * Handles live route updates, notifications, and collaborative features
 */

class RouteForceWebSocket {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.currentRouteId = null;
        this.eventHandlers = {};
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        
        this.init();
    }
    
    init() {
        try {
            // Initialize Socket.IO connection
            this.socket = io({
                transports: ['websocket', 'polling'],
                upgrade: true,
                rememberUpgrade: true
            });
            
            this.registerEventHandlers();
            this.startHeartbeat();
            
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
        }
    }
    
    registerEventHandlers() {
        // Connection events
        this.socket.on('connect', () => {
            console.log('✅ Connected to RouteForce WebSocket');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.showNotification('Connected to real-time updates', 'success');
            this.trigger('connected');
        });
        
        this.socket.on('disconnect', (reason) => {
            console.log('❌ Disconnected from WebSocket:', reason);
            this.isConnected = false;
            this.showNotification('Lost connection to real-time updates', 'warning');
            this.trigger('disconnected', reason);
            
            // Attempt reconnection for client-side disconnects
            if (reason === 'io client disconnect') {
                this.attemptReconnection();
            }
        });
        
        this.socket.on('connect_error', (error) => {
            console.error('WebSocket connection error:', error);
            this.showNotification('Connection error - retrying...', 'error');
            this.attemptReconnection();
        });
        
        // Welcome message
        this.socket.on('connected', (data) => {
            console.log('Welcome message:', data.message);
            this.updateUserCount(data.active_users);
        });
        
        // User count updates
        this.socket.on('user_count_update', (data) => {
            this.updateUserCount(data.active_users);
        });
        
        // Route updates
        this.socket.on('route_update', (data) => {
            console.log('Route update received:', data);
            this.handleRouteUpdate(data);
        });
        
        // Optimization progress
        this.socket.on('optimization_progress', (data) => {
            console.log('Optimization progress:', data);
            this.handleOptimizationProgress(data);
        });
        
        // Route progress from drivers
        this.socket.on('route_progress', (data) => {
            console.log('Route progress update:', data);
            this.handleRouteProgress(data);
        });
        
        // Route status
        this.socket.on('route_status', (data) => {
            console.log('Route status:', data);
            this.handleRouteStatus(data);
        });
        
        // Notifications
        this.socket.on('notification', (data) => {
            console.log('Notification received:', data);
            this.showNotification(data.message, data.type || 'info');
        });
        
        // Route room events
        this.socket.on('joined_route', (data) => {
            console.log(`Joined route ${data.route_id} for real-time updates`);
            this.showNotification(`Watching route ${data.route_id} for live updates`, 'info');
        });
        
        this.socket.on('user_joined_route', (data) => {
            this.showNotification(`${data.username} joined route ${data.route_id}`, 'info');
        });
        
        this.socket.on('user_left_route', (data) => {
            this.showNotification(`${data.username} left route ${data.route_id}`, 'info');
        });
        
        // Heartbeat
        this.socket.on('pong', (data) => {
            // Connection is alive
        });
        
        // Error handling
        this.socket.on('error', (data) => {
            console.error('WebSocket error:', data);
            this.showNotification(data.message || 'WebSocket error occurred', 'error');
        });
    }
    
    // Public API methods
    joinRoute(routeId) {
        if (this.isConnected && routeId) {
            this.currentRouteId = routeId;
            this.socket.emit('join_route', { route_id: routeId });
            console.log(`Joining route ${routeId} for real-time updates`);
        }
    }
    
    leaveRoute(routeId) {
        if (this.isConnected && routeId) {
            this.socket.emit('leave_route', { route_id: routeId });
            if (this.currentRouteId === routeId) {
                this.currentRouteId = null;
            }
            console.log(`Left route ${routeId}`);
        }
    }
    
    updateRouteProgress(routeId, progress) {
        if (this.isConnected) {
            this.socket.emit('route_progress_update', {
                route_id: routeId,
                progress: progress
            });
        }
    }
    
    requestRouteStatus(routeId) {
        if (this.isConnected) {
            this.socket.emit('request_route_status', { route_id: routeId });
        }
    }
    
    // Event handling
    on(event, handler) {
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(handler);
    }
    
    off(event, handler) {
        if (this.eventHandlers[event]) {
            const index = this.eventHandlers[event].indexOf(handler);
            if (index > -1) {
                this.eventHandlers[event].splice(index, 1);
            }
        }
    }
    
    trigger(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Error in event handler for ${event}:`, error);
                }
            });
        }
    }
    
    // Internal methods
    attemptReconnection() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting reconnection ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            
            setTimeout(() => {
                this.socket.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.error('Max reconnection attempts reached');
            this.showNotification('Unable to reconnect to real-time updates', 'error');
        }
    }
    
    startHeartbeat() {
        setInterval(() => {
            if (this.isConnected) {
                this.socket.emit('ping');
            }
        }, 30000); // 30 seconds
    }
    
    handleRouteUpdate(data) {
        const status = data.status;
        const routeData = data.data;
        
        switch (status) {
            case 'generation_started':
                this.showRouteProgress('Route generation started...', 0);
                this.updateRouteStatus('Generating route...', 'info');
                break;
                
            case 'generation_completed':
                this.showRouteProgress('Route generation completed!', 100);
                this.updateRouteStatus('Route ready', 'success');
                this.displayRoute(routeData.route);
                this.updateMetrics(routeData);
                break;
                
            case 'generation_failed':
                this.showRouteProgress('Route generation failed', 0);
                this.updateRouteStatus('Generation failed', 'error');
                break;
                
            case 'generation_error':
                this.showRouteProgress('Error occurred', 0);
                this.updateRouteStatus(`Error: ${routeData.error}`, 'error');
                break;
        }
        
        this.trigger('route_update', data);
    }
    
    handleOptimizationProgress(data) {
        const progress = data.optimization_progress;
        this.showRouteProgress(`Optimizing... ${progress.status}`, progress.percentage || 0);
        this.trigger('optimization_progress', data);
    }
    
    handleRouteProgress(data) {
        const progress = data.progress;
        this.showNotification(`Route progress: ${progress.message || 'Updated'}`, 'info');
        this.trigger('route_progress', data);
    }
    
    handleRouteStatus(data) {
        this.updateRouteStatus(data.status.status, 'info');
        this.trigger('route_status', data);
    }
    
    // UI update methods
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    updateUserCount(count) {
        const userCountElement = document.getElementById('active-users-count');
        if (userCountElement) {
            userCountElement.textContent = count;
        }
        
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.innerHTML = `
                <i class="bi bi-circle-fill text-success"></i> 
                Connected (${count} active users)
            `;
        }
    }
    
    showRouteProgress(message, percentage) {
        const progressElement = document.getElementById('route-progress');
        if (progressElement) {
            progressElement.innerHTML = `
                <div class="progress mb-2">
                    <div class="progress-bar" role="progressbar" style="width: ${percentage}%" 
                         aria-valuenow="${percentage}" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                <small class="text-muted">${message}</small>
            `;
        }
    }
    
    updateRouteStatus(status, type) {
        const statusElement = document.getElementById('route-status');
        if (statusElement) {
            const badgeClass = type === 'success' ? 'bg-success' : 
                              type === 'error' ? 'bg-danger' : 'bg-primary';
            statusElement.innerHTML = `<span class="badge ${badgeClass}">${status}</span>`;
        }
    }
    
    updateMetrics(data) {
        // Update processing time
        const timeElement = document.getElementById('processing-time');
        if (timeElement && data.processing_time) {
            timeElement.textContent = `${data.processing_time.toFixed(2)}s`;
        }
        
        // Update optimization score
        const scoreElement = document.getElementById('optimization-score');
        if (scoreElement && data.optimization_score) {
            scoreElement.textContent = data.optimization_score.toFixed(1);
        }
        
        // Update algorithm used
        const algoElement = document.getElementById('algorithm-used');
        if (algoElement && data.algorithm_used) {
            algoElement.textContent = data.algorithm_used;
        }
    }
    
    displayRoute(route) {
        // Trigger custom event for route display
        this.trigger('route_ready', route);
        
        // Update route list if element exists
        const routeListElement = document.getElementById('route-list');
        if (routeListElement && Array.isArray(route)) {
            routeListElement.innerHTML = route.map((stop, index) => `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${index + 1}. ${stop.name || stop.id}</strong>
                        <br>
                        <small class="text-muted">${stop.lat?.toFixed(6)}, ${stop.lon?.toFixed(6)}</small>
                    </div>
                    <span class="badge bg-primary rounded-pill">${stop.priority || 1}</span>
                </li>
            `).join('');
        }
    }
}

// Initialize WebSocket when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if not already done
    if (typeof window.routeForceWS === 'undefined') {
        window.routeForceWS = new RouteForceWebSocket();
        console.log('🚀 RouteForce WebSocket client initialized');
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RouteForceWebSocket;
}
