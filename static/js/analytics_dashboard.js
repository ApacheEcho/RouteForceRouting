// Analytics Dashboard JavaScript Component
class AnalyticsDashboard {
    constructor() {
        this.apiBaseUrl = '/api/analytics';
        this.refreshInterval = 30000; // 30 seconds
        this.charts = {};
        this.currentTimeframe = '24h';
        this.refreshTimer = null;
    }

    async init() {
        console.log('Initializing Analytics Dashboard...');
        
        try {
            await this.initializeAnalyticsContainer();
            await this.loadAnalyticsData();
            this.setupEventListeners();
            this.startAutoRefresh();
            console.log('Analytics Dashboard initialized successfully');
        } catch (error) {
            console.error('Failed to initialize Analytics Dashboard:', error);
        }
    }

    initializeAnalyticsContainer() {
        // Get the analytics container that already exists in the dashboard
        let analyticsContainer = document.getElementById('analytics-container');
        if (!analyticsContainer) {
            console.error('Analytics container not found in dashboard');
            return;
        }
        
        // Initialize analytics HTML structure
        analyticsContainer.innerHTML = `
            <div class="analytics-grid">
                <!-- System Health Card -->
                <div class="analytics-card health-card">
                    <div class="card-header">
                        <h4><i class="fas fa-heartbeat"></i> System Health</h4>
                    </div>
                    <div class="card-body">
                        <div class="health-score">
                            <div id="health-score-circle" class="health-circle">
                                <span id="health-score-value">--</span>
                            </div>
                            <div class="health-status">
                                <span id="health-status">Checking...</span>
                            </div>
                        </div>
                        <div class="health-metrics">
                            <div class="metric">
                                <span class="label">Uptime:</span>
                                <span id="system-uptime">--</span>
                            </div>
                            <div class="metric">
                                <span class="label">Active Sessions:</span>
                                <span id="active-sessions">--</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Mobile Analytics Card -->
                <div class="analytics-card mobile-card">
                    <div class="card-header">
                        <h4><i class="fas fa-mobile-alt"></i> Mobile Usage</h4>
                    </div>
                    <div class="card-body">
                        <div class="metrics-grid">
                            <div class="metric-item">
                                <div class="metric-value" id="mobile-sessions">--</div>
                                <div class="metric-label">Active Sessions</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-value" id="mobile-devices">--</div>
                                <div class="metric-label">Unique Devices</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-value" id="mobile-api-calls">--</div>
                                <div class="metric-label">API Calls</div>
                            </div>
                        </div>
                        <canvas id="mobile-usage-chart" width="300" height="150"></canvas>
                    </div>
                </div>

                <!-- Route Analytics Card -->
                <div class="analytics-card route-card">
                    <div class="card-header">
                        <h4><i class="fas fa-route"></i> Route Performance</h4>
                    </div>
                    <div class="card-body">
                        <div class="metrics-grid">
                            <div class="metric-item">
                                <div class="metric-value" id="total-routes">--</div>
                                <div class="metric-label">Routes Generated</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-value" id="success-rate">--%</div>
                                <div class="metric-label">Success Rate</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-value" id="avg-optimization-time">--s</div>
                                <div class="metric-label">Avg Optimization</div>
                            </div>
                        </div>
                        <canvas id="route-performance-chart" width="300" height="150"></canvas>
                    </div>
                </div>

                <!-- Driver Analytics Card -->
                <div class="analytics-card driver-card">
                    <div class="card-header">
                        <h4><i class="fas fa-users"></i> Driver Performance</h4>
                    </div>
                    <div class="card-body">
                        <div class="metrics-grid">
                            <div class="metric-item">
                                <div class="metric-value" id="total-drivers">--</div>
                                <div class="metric-label">Active Drivers</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-value" id="avg-rating">--</div>
                                <div class="metric-label">Avg Rating</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-value" id="location-updates">--</div>
                                <div class="metric-label">Location Updates</div>
                            </div>
                        </div>
                        <div id="top-drivers" class="top-performers">
                            <!-- Top drivers will be populated here -->
                        </div>
                    </div>
                </div>

                <!-- API Analytics Card -->
                <div class="analytics-card api-card">
                    <div class="card-header">
                        <h4><i class="fas fa-plug"></i> API Performance</h4>
                    </div>
                    <div class="card-body">
                        <div class="metrics-grid">
                            <div class="metric-item">
                                <div class="metric-value" id="total-requests">--</div>
                                <div class="metric-label">Total Requests</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-value" id="error-rate">--%</div>
                                <div class="metric-label">Error Rate</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-value" id="avg-response-time">--ms</div>
                                <div class="metric-label">Avg Response</div>
                            </div>
                        </div>
                        <canvas id="api-performance-chart" width="300" height="150"></canvas>
                    </div>
                </div>

                <!-- Real-time Activity Feed -->
                <div class="analytics-card activity-card">
                    <div class="card-header">
                        <h4><i class="fas fa-stream"></i> Real-time Activity</h4>
                    </div>
                    <div class="card-body">
                        <div id="activity-feed" class="activity-feed">
                            <!-- Real-time activities will be populated here -->
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    createAnalyticsTab() {
        // This method is no longer needed since we're integrating directly into the dashboard
        // Analytics section is now part of the main dashboard layout
        console.log('Analytics integrated directly into dashboard layout');
    }

    setupEventListeners() {
        // Timeframe selector
        const timeframeSelect = document.getElementById('analytics-timeframe');
        if (timeframeSelect) {
            timeframeSelect.addEventListener('change', (e) => {
                this.currentTimeframe = e.target.value;
                this.loadAnalyticsData();
            });
        }

        // Refresh button
        const refreshButton = document.getElementById('refresh-analytics');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => {
                this.loadAnalyticsData();
            });
        }
    }

    async loadAnalyticsData() {
        try {
            console.log(`Loading analytics data for timeframe: ${this.currentTimeframe}`);
            
            // Load all analytics data concurrently
            const [systemHealth, mobileAnalytics, routeAnalytics, driverAnalytics, apiAnalytics] = await Promise.all([
                this.fetchSystemHealth(),
                this.fetchMobileAnalytics(),
                this.fetchRouteAnalytics(),
                this.fetchDriverAnalytics(),
                this.fetchAPIAnalytics()
            ]);

            // Update UI with fetched data
            this.updateSystemHealthUI(systemHealth);
            this.updateMobileAnalyticsUI(mobileAnalytics);
            this.updateRouteAnalyticsUI(routeAnalytics);
            this.updateDriverAnalyticsUI(driverAnalytics);
            this.updateAPIAnalyticsUI(apiAnalytics);

            // Add activity to feed
            this.addActivity('Analytics data refreshed', 'info');

        } catch (error) {
            console.error('Failed to load analytics data:', error);
            this.addActivity('Failed to load analytics data', 'error');
        }
    }

    async fetchSystemHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/system-health`, {
                headers: { 'X-API-Key': 'test-api-key' }
            });
            
            if (response.ok) {
                const result = await response.json();
                return result.data;
            }
        } catch (error) {
            console.error('Failed to fetch system health:', error);
        }
        return null;
    }

    async fetchMobileAnalytics() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/mobile?timeframe=${this.currentTimeframe}`, {
                headers: { 'X-API-Key': 'test-api-key' }
            });
            
            if (response.ok) {
                const result = await response.json();
                return result.data;
            }
        } catch (error) {
            console.error('Failed to fetch mobile analytics:', error);
        }
        return null;
    }

    async fetchRouteAnalytics() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/routes?timeframe=${this.currentTimeframe}`, {
                headers: { 'X-API-Key': 'test-api-key' }
            });
            
            if (response.ok) {
                const result = await response.json();
                return result.data;
            }
        } catch (error) {
            console.error('Failed to fetch route analytics:', error);
        }
        return null;
    }

    async fetchDriverAnalytics() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/drivers?timeframe=${this.currentTimeframe}`, {
                headers: { 'X-API-Key': 'test-api-key' }
            });
            
            if (response.ok) {
                const result = await response.json();
                return result.data;
            }
        } catch (error) {
            console.error('Failed to fetch driver analytics:', error);
        }
        return null;
    }

    async fetchAPIAnalytics() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api-usage?timeframe=${this.currentTimeframe}`, {
                headers: { 'X-API-Key': 'test-api-key' }
            });
            
            if (response.ok) {
                const result = await response.json();
                return result.data;
            }
        } catch (error) {
            console.error('Failed to fetch API analytics:', error);
        }
        return null;
    }

    updateSystemHealthUI(data) {
        if (!data) return;

        const healthScore = data.health_score || 0;
        const status = data.status || 'unknown';
        const uptime = data.uptime || '--';
        const activeSessions = data.active_sessions || 0;

        // Update health score circle
        document.getElementById('health-score-value').textContent = healthScore;
        document.getElementById('health-status').textContent = status.toUpperCase();
        document.getElementById('system-uptime').textContent = uptime;
        document.getElementById('active-sessions').textContent = activeSessions;

        // Color code health score
        const healthCircle = document.getElementById('health-score-circle');
        healthCircle.className = `health-circle ${this.getHealthColorClass(healthScore)}`;
    }

    updateMobileAnalyticsUI(data) {
        if (!data) return;

        document.getElementById('mobile-sessions').textContent = data.total_sessions || 0;
        document.getElementById('mobile-devices').textContent = data.unique_devices || 0;
        document.getElementById('mobile-api-calls').textContent = data.total_api_calls || 0;

        // Create mobile usage chart
        this.createMobileUsageChart(data);
    }

    updateRouteAnalyticsUI(data) {
        if (!data) return;

        document.getElementById('total-routes').textContent = data.total_routes || 0;
        document.getElementById('success-rate').textContent = `${data.success_rate || 0}%`;
        document.getElementById('avg-optimization-time').textContent = `${data.avg_optimization_time || 0}s`;

        // Create route performance chart
        this.createRoutePerformanceChart(data);
    }

    updateDriverAnalyticsUI(data) {
        if (!data) return;

        document.getElementById('total-drivers').textContent = data.total_drivers || 0;
        document.getElementById('avg-rating').textContent = data.avg_customer_rating || '--';
        document.getElementById('location-updates').textContent = data.total_location_updates || 0;

        // Update top drivers
        this.updateTopDrivers(data.top_performers || []);
    }

    updateAPIAnalyticsUI(data) {
        if (!data) return;

        document.getElementById('total-requests').textContent = data.total_requests || 0;
        document.getElementById('error-rate').textContent = `${data.error_rate || 0}%`;
        const avgResponseTime = data.performance?.avg_response_time || 0;
        document.getElementById('avg-response-time').textContent = `${(avgResponseTime * 1000).toFixed(0)}ms`;

        // Create API performance chart
        this.createAPIPerformanceChart(data);
    }

    createMobileUsageChart(data) {
        const canvas = document.getElementById('mobile-usage-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        // Simple chart showing device types
        const deviceTypes = data.device_types || {};
        const labels = Object.keys(deviceTypes);
        const values = Object.values(deviceTypes);

        if (this.charts.mobileUsage) {
            this.charts.mobileUsage.destroy();
        }

        this.charts.mobileUsage = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: ['#007bff', '#28a745', '#ffc107', '#dc3545']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                legend: { position: 'bottom' }
            }
        });
    }

    createRoutePerformanceChart(data) {
        const canvas = document.getElementById('route-performance-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        // Algorithm usage chart
        const algorithmUsage = data.algorithm_usage || {};
        const labels = Object.keys(algorithmUsage);
        const values = Object.values(algorithmUsage);

        if (this.charts.routePerformance) {
            this.charts.routePerformance.destroy();
        }

        this.charts.routePerformance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Routes Generated',
                    data: values,
                    backgroundColor: '#007bff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    createAPIPerformanceChart(data) {
        const canvas = document.getElementById('api-performance-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        // Response time performance over time (simplified)
        const performance = data.performance || {};
        
        if (this.charts.apiPerformance) {
            this.charts.apiPerformance.destroy();
        }

        this.charts.apiPerformance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Avg', 'Median', 'P95', 'Max'],
                datasets: [{
                    label: 'Response Time (ms)',
                    data: [
                        (performance.avg_response_time || 0) * 1000,
                        (performance.median_response_time || 0) * 1000,
                        (performance.p95_response_time || 0) * 1000,
                        (performance.max_response_time || 0) * 1000
                    ],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    updateTopDrivers(topDrivers) {
        const container = document.getElementById('top-drivers');
        if (!container) return;

        if (topDrivers.length === 0) {
            container.innerHTML = '<p class="text-muted">No driver data available</p>';
            return;
        }

        container.innerHTML = topDrivers.slice(0, 3).map((driver, index) => `
            <div class="top-driver">
                <span class="rank">#${index + 1}</span>
                <span class="driver-id">${driver.driver_id}</span>
                <span class="rating">⭐ ${driver.avg_rating}</span>
            </div>
        `).join('');
    }

    getHealthColorClass(score) {
        if (score >= 90) return 'excellent';
        if (score >= 75) return 'good';
        if (score >= 50) return 'fair';
        return 'poor';
    }

    addActivity(message, type = 'info') {
        const activityFeed = document.getElementById('activity-feed');
        if (!activityFeed) return;

        const timestamp = new Date().toLocaleTimeString();
        const icon = this.getActivityIcon(type);
        
        const activityItem = document.createElement('div');
        activityItem.className = `activity-item ${type}`;
        activityItem.innerHTML = `
            <i class="fas fa-${icon}"></i>
            <span class="timestamp">${timestamp}</span>
            <span class="message">${message}</span>
        `;

        activityFeed.insertBefore(activityItem, activityFeed.firstChild);

        // Keep only last 10 activities
        while (activityFeed.children.length > 10) {
            activityFeed.removeChild(activityFeed.lastChild);
        }
    }

    getActivityIcon(type) {
        const icons = {
            'info': 'info-circle',
            'success': 'check-circle',
            'warning': 'exclamation-triangle',
            'error': 'times-circle'
        };
        return icons[type] || 'info-circle';
    }

    startAutoRefresh() {
        this.stopAutoRefresh();
        this.refreshTimer = setInterval(() => {
            this.loadAnalyticsData();
        }, this.refreshInterval);
    }

    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    destroy() {
        this.stopAutoRefresh();
        
        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.destroy) {
                chart.destroy();
            }
        });
        
        this.charts = {};
    }
}

// CSS styles for analytics dashboard
const analyticsCSS = `
<style>
.analytics-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 15px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 8px;
}

.analytics-controls {
    display: flex;
    gap: 10px;
    align-items: center;
}

.analytics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
}

.analytics-card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    overflow: hidden;
    transition: transform 0.2s;
}

.analytics-card:hover {
    transform: translateY(-2px);
}

.analytics-card .card-header {
    background: #f8f9fa;
    padding: 15px;
    border-bottom: 1px solid #dee2e6;
}

.analytics-card .card-header h4 {
    margin: 0;
    color: #495057;
}

.analytics-card .card-body {
    padding: 20px;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin-bottom: 15px;
}

.metric-item {
    text-align: center;
}

.metric-value {
    font-size: 1.8em;
    font-weight: bold;
    color: #007bff;
}

.metric-label {
    font-size: 0.85em;
    color: #6c757d;
    margin-top: 5px;
}

.health-score {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 15px;
}

.health-circle {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2em;
    font-weight: bold;
    color: white;
}

.health-circle.excellent { background: #28a745; }
.health-circle.good { background: #17a2b8; }
.health-circle.fair { background: #ffc107; color: #212529; }
.health-circle.poor { background: #dc3545; }

.health-status {
    font-size: 1.1em;
    font-weight: bold;
}

.health-metrics .metric {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
}

.activity-feed {
    max-height: 200px;
    overflow-y: auto;
}

.activity-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px;
    margin-bottom: 5px;
    border-radius: 4px;
    font-size: 0.9em;
}

.activity-item.info { background: #e3f2fd; }
.activity-item.success { background: #e8f5e8; }
.activity-item.warning { background: #fff3cd; }
.activity-item.error { background: #f8d7da; }

.activity-item .timestamp {
    font-size: 0.8em;
    color: #6c757d;
    min-width: 60px;
}

.top-driver {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #dee2e6;
}

.top-driver:last-child {
    border-bottom: none;
}

.rank {
    font-weight: bold;
    color: #007bff;
}
</style>
`;

// Auto-initialize analytics dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Inject CSS
    document.head.insertAdjacentHTML('beforeend', analyticsCSS);
    
    // Initialize analytics dashboard
    window.analyticsDashboard = new AnalyticsDashboard();
});

// Export for global access
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AnalyticsDashboard;
}
