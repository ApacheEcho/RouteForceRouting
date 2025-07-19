// Enhanced Dashboard JavaScript - Real-time Route Optimization with API Integration
class RouteOptimizationDashboard {
    constructor() {
        this.map = null;
        this.markers = [];
        this.routeLines = [];
        this.clusters = [];
        this.clusterLayers = [];
        this.socket = null;
        this.performanceChart = null;
        this.clusterChart = null;
        this.currentStores = [];
        this.currentRoutes = [];
        this.optimizationInProgress = false;
        this.apiBaseUrl = '/api/v1';
        this.activityFeed = [];
        this.routeColors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#dda0dd'];
        
        this.init();
    }

    init() {
        this.initializeMap();
        this.initializeCharts();
        this.initializeEventListeners();
        this.initializeWebSocket();
        this.updateConnectionStatus('connected');
        this.addActivity('Dashboard initialized and ready');
    }

    // Initialize Leaflet Map with enhanced features
    initializeMap() {
        // Initialize map centered on New York City
        this.map = L.map('routeMap').setView([40.7128, -74.0060], 11);
        
        // Add multiple tile layer options
        const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        });
        
        const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Tiles © Esri'
        });
        
        // Add default layer
        osmLayer.addTo(this.map);
        
        // Add layer control
        const baseLayers = {
            "Street Map": osmLayer,
            "Satellite": satelliteLayer
        };
        
        L.control.layers(baseLayers).addTo(this.map);
        
        // Add scale control
        L.control.scale().addTo(this.map);
        
        // Add map click handler for adding manual points
        this.map.on('click', (e) => {
            this.onMapClick(e);
        });
        
        // Add zoom event listener
        this.map.on('zoomend', () => {
            this.updateMapMarkers();
        });
    }

    // Initialize Charts with enhanced styling
    initializeCharts() {
        // Performance Chart
        const performanceCtx = document.getElementById('performanceChart').getContext('2d');
        this.performanceChart = new Chart(performanceCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Optimization Score (%)',
                    data: [],
                    borderColor: '#4f46e5',
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    fill: true,
                    tension: 0.4
                }, {
                    label: 'Processing Time (s)',
                    data: [],
                    borderColor: '#06b6d4',
                    backgroundColor: 'rgba(6, 182, 212, 0.1)',
                    fill: true,
                    tension: 0.4,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Optimization Score (%)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Processing Time (s)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        }
                    }
                }
            }
        });

        // Cluster Chart
        const clusterCtx = document.getElementById('clusterChart').getContext('2d');
        this.clusterChart = new Chart(clusterCtx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7',
                        '#dda0dd', '#98d8c8', '#fdcb6e', '#6c5ce7', '#fd79a8'
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Initialize Event Listeners
    initializeEventListeners() {
        // File upload form
        document.getElementById('uploadForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFileUpload();
        });

        // Radius slider
        document.getElementById('clusterRadius').addEventListener('input', (e) => {
            document.getElementById('radiusValue').textContent = `${e.target.value} km`;
        });

        // Map control buttons
        document.getElementById('clearMapBtn').addEventListener('click', () => {
            this.clearMap();
        });

        document.getElementById('centerMapBtn').addEventListener('click', () => {
            this.centerMap();
        });

        document.getElementById('toggleClustersBtn').addEventListener('click', () => {
            this.toggleClusters();
        });

        // File input change
        document.getElementById('storeFile').addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                document.querySelector('.file-text').textContent = file.name;
                this.addActivity(`File selected: ${file.name}`);
            }
        });
    }

    // Initialize WebSocket for real-time updates
    initializeWebSocket() {
        try {
            // For now, simulate WebSocket connection
            this.simulateWebSocketConnection();
        } catch (error) {
            console.error('WebSocket connection failed:', error);
            this.updateConnectionStatus('disconnected');
        }
    }

    simulateWebSocketConnection() {
        // Simulate connection status updates
        setInterval(() => {
            const isConnected = Math.random() > 0.1; // 90% uptime simulation
            this.updateConnectionStatus(isConnected ? 'connected' : 'disconnected');
        }, 10000);
    }

    // Update connection status
    updateConnectionStatus(status) {
        const statusIndicator = document.querySelector('#connectionStatus .w-3');
        const statusText = document.getElementById('statusText');
        
        if (status === 'connected') {
            statusIndicator.className = 'w-3 h-3 bg-green-400 rounded-full animate-pulse';
            statusText.textContent = 'Connected';
        } else {
            statusIndicator.className = 'w-3 h-3 bg-red-400 rounded-full';
            statusText.textContent = 'Disconnected';
        }
    }

    // Handle file upload and optimization with enhanced API integration
    async handleFileUpload() {
        if (this.optimizationInProgress) {
            this.addActivity('Optimization already in progress', 'warning');
            return;
        }
        
        const fileInput = document.getElementById('storeFile');
        const file = fileInput.files[0];
        
        if (!file) {
            this.addActivity('No file selected', 'error');
            return;
        }
        
        this.optimizationInProgress = true;
        this.showLoadingOverlay();
        this.addActivity(`Processing file: ${file.name}`, 'info');
        
        try {
            // Update UI to show processing state
            const optimizeBtn = document.getElementById('optimizeBtn');
            const originalText = optimizeBtn.innerHTML;
            optimizeBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
            optimizeBtn.disabled = true;
            
            // Get optimization parameters
            const formData = new FormData();
            formData.append('file', file);
            formData.append('use_proximity', document.getElementById('proximityToggle').checked);
            formData.append('radius_km', document.getElementById('clusterRadius').value);
            formData.append('start_time', document.getElementById('startTime').value);
            formData.append('end_time', document.getElementById('endTime').value);
            
            const startTime = performance.now();
            
            // First, try to create clusters if proximity is enabled
            if (document.getElementById('proximityToggle').checked) {
                await this.performProximityClustering(file);
            }
            
            // Then generate the optimized routes
            const routeResponse = await this.generateOptimizedRoutes(formData);
            
            const endTime = performance.now();
            const processingTime = ((endTime - startTime) / 1000).toFixed(2);
            
            // Update the map with results
            this.updateMapWithResults(routeResponse);
            
            // Update metrics
            this.updateMetrics({
                totalStores: routeResponse.total_stores || this.currentStores.length,
                clusterCount: routeResponse.cluster_count || 0,
                optimizationScore: routeResponse.optimization_score || 85,
                processingTime: processingTime
            });
            
            // Update charts
            this.updateCharts(routeResponse);
            
            this.addActivity(`Route optimization completed in ${processingTime}s`, 'success');
            
            // Reset button
            optimizeBtn.innerHTML = originalText;
            optimizeBtn.disabled = false;
            
        } catch (error) {
            console.error('Optimization failed:', error);
            this.addActivity(`Optimization failed: ${error.message}`, 'error');
            
            // Reset button
            const optimizeBtn = document.getElementById('optimizeBtn');
            optimizeBtn.innerHTML = '<i class="fas fa-magic mr-2"></i>Optimize Route';
            optimizeBtn.disabled = false;
        } finally {
            this.optimizationInProgress = false;
            this.hideLoadingOverlay();
        }
    }
    
    // Perform proximity clustering via API
    async performProximityClustering(file) {
        try {
            // First, extract stores from file
            const stores = await this.extractStoresFromFile(file);
            
            const response = await fetch(`${this.apiBaseUrl}/clusters`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    stores: stores,
                    radius_km: parseFloat(document.getElementById('clusterRadius').value)
                })
            });
            
            if (!response.ok) {
                throw new Error(`Clustering failed: ${response.statusText}`);
            }
            
            const clusterData = await response.json();
            this.displayClusters(clusterData);
            this.addActivity(`Created ${clusterData.cluster_count} proximity clusters`, 'success');
            
            return clusterData;
            
        } catch (error) {
            console.error('Clustering error:', error);
            this.addActivity(`Clustering failed: ${error.message}`, 'error');
            throw error;
        }
    }
    
    // Generate optimized routes via API
    async generateOptimizedRoutes(formData) {
        try {
            const response = await fetch('/generate_route', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Route generation failed: ${response.statusText}`);
            }
            
            const result = await response.json();
            return result;
            
        } catch (error) {
            console.error('Route generation error:', error);
            throw error;
        }
    }
    
    // Extract stores from uploaded file
    async extractStoresFromFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const text = e.target.result;
                    const stores = this.parseCSVData(text);
                    resolve(stores);
                } catch (error) {
                    reject(error);
                }
            };
            reader.onerror = () => reject(new Error('Failed to read file'));
            reader.readAsText(file);
        });
    }
    
    // Parse CSV data into stores array
    parseCSVData(csvText) {
        const lines = csvText.split('\n');
        const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
        const stores = [];
        
        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',');
            if (values.length >= headers.length) {
                const store = {};
                headers.forEach((header, index) => {
                    store[header] = values[index]?.trim();
                });
                
                // Convert coordinates if present
                if (store.latitude && store.longitude) {
                    store.latitude = parseFloat(store.latitude);
                    store.longitude = parseFloat(store.longitude);
                    stores.push(store);
                }
            }
        }
        
        return stores;
    }

    // Display clusters on map
    displayClusters(clusterData) {
        // Clear existing clusters
        this.clearClusters();
        
        clusterData.clusters.forEach((cluster, index) => {
            const color = this.routeColors[index % this.routeColors.length];
            
            cluster.forEach(store => {
                const marker = L.marker([store.latitude, store.longitude], {
                    icon: L.divIcon({
                        className: 'cluster-marker',
                        html: `<div style="background-color: ${color}; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-weight: bold;">${index + 1}</div>`,
                        iconSize: [30, 30]
                    })
                }).addTo(this.map);
                
                marker.bindPopup(`
                    <div>
                        <h3 class="font-semibold">${store.name}</h3>
                        <p class="text-sm text-gray-600">Cluster ${index + 1}</p>
                        <p class="text-xs text-gray-500">Lat: ${store.latitude.toFixed(4)}, Lng: ${store.longitude.toFixed(4)}</p>
                    </div>
                `);
                
                this.clusterLayers.push(marker);
            });
        });
        
        // Fit map to show all clusters
        if (this.clusterLayers.length > 0) {
            const group = new L.featureGroup(this.clusterLayers);
            this.map.fitBounds(group.getBounds().pad(0.1));
        }
    }

    // Update map with route results
    updateMapWithResults(routeResponse) {
        this.clearMap();
        
        if (routeResponse.stores && routeResponse.stores.length > 0) {
            this.currentStores = routeResponse.stores;
            this.visualizeStores(routeResponse.stores);
        }
        
        if (routeResponse.route && routeResponse.route.length > 0) {
            this.currentRoutes = routeResponse.route;
            this.visualizeRoutes(routeResponse.route);
        }
    }

    // Visualize stores on map
    visualizeStores(stores) {
        stores.forEach((store, index) => {
            const marker = L.marker([store.latitude, store.longitude], {
                icon: L.divIcon({
                    className: 'store-marker',
                    html: `<div style="background-color: #4f46e5; color: white; border-radius: 50%; width: 25px; height: 25px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold;">${index + 1}</div>`,
                    iconSize: [25, 25]
                })
            }).addTo(this.map);
            
            marker.bindPopup(`
                <div>
                    <h3 class="font-semibold">${store.name || 'Store ' + (index + 1)}</h3>
                    <p class="text-sm text-gray-600">${store.address || 'Address not available'}</p>
                    <p class="text-xs text-gray-500">Lat: ${store.latitude.toFixed(4)}, Lng: ${store.longitude.toFixed(4)}</p>
                </div>
            `);
            
            this.markers.push(marker);
        });
    }

    // Visualize routes on map
    visualizeRoutes(routes) {
        if (routes.length < 2) return;
        
        const routeCoordinates = routes.map(store => [store.latitude, store.longitude]);
        
        const routeLine = L.polyline(routeCoordinates, {
            color: '#4f46e5',
            weight: 3,
            opacity: 0.8,
            smoothFactor: 1
        }).addTo(this.map);
        
        this.routeLines.push(routeLine);
        
        // Fit map to show entire route
        this.map.fitBounds(routeLine.getBounds().pad(0.1));
    }

    // Update metrics display
    updateMetrics(metrics) {
        this.animateCounter('totalStores', metrics.totalStores);
        this.animateCounter('clusterCount', metrics.clusterCount);
        this.animateCounter('optimizationScore', metrics.optimizationScore, '%');
        document.getElementById('processingTime').textContent = metrics.processingTime + 's';
    }

    // Animate counter with smooth transition
    animateCounter(elementId, targetValue, suffix = '') {
        const element = document.getElementById(elementId);
        const startValue = parseInt(element.textContent) || 0;
        const duration = 1000; // 1 second
        const increment = (targetValue - startValue) / (duration / 16); // 60fps
        
        let currentValue = startValue;
        const counter = setInterval(() => {
            currentValue += increment;
            if ((increment > 0 && currentValue >= targetValue) || (increment < 0 && currentValue <= targetValue)) {
                currentValue = targetValue;
                clearInterval(counter);
            }
            element.textContent = Math.round(currentValue) + suffix;
        }, 16);
    }

    // Update charts with new data
    updateCharts(routeResponse) {
        const now = new Date().toLocaleTimeString();
        
        // Update performance chart
        this.performanceChart.data.labels.push(now);
        this.performanceChart.data.datasets[0].data.push(routeResponse.optimization_score || 85);
        this.performanceChart.data.datasets[1].data.push(routeResponse.processing_time || 2.5);
        
        // Keep only last 10 data points
        if (this.performanceChart.data.labels.length > 10) {
            this.performanceChart.data.labels.shift();
            this.performanceChart.data.datasets[0].data.shift();
            this.performanceChart.data.datasets[1].data.shift();
        }
        
        this.performanceChart.update();
        
        // Update cluster chart
        if (routeResponse.clusters) {
            this.clusterChart.data.labels = routeResponse.clusters.map((cluster, index) => `Cluster ${index + 1}`);
            this.clusterChart.data.datasets[0].data = routeResponse.clusters.map(cluster => cluster.length);
            this.clusterChart.update();
        }
    }

    // Map interaction handlers
    onMapClick(e) {
        const lat = e.latlng.lat.toFixed(4);
        const lng = e.latlng.lng.toFixed(4);
        this.addActivity(`Map clicked at: ${lat}, ${lng}`, 'info');
    }

    updateMapMarkers() {
        // Update marker visibility based on zoom level
        const zoom = this.map.getZoom();
        this.markers.forEach(marker => {
            if (zoom < 10) {
                marker.setOpacity(0.7);
            } else {
                marker.setOpacity(1);
            }
        });
    }

    // Map control functions
    clearMap() {
        this.markers.forEach(marker => this.map.removeLayer(marker));
        this.routeLines.forEach(line => this.map.removeLayer(line));
        this.clearClusters();
        this.markers = [];
        this.routeLines = [];
        this.addActivity('Map cleared', 'info');
    }

    clearClusters() {
        this.clusterLayers.forEach(layer => this.map.removeLayer(layer));
        this.clusterLayers = [];
    }

    centerMap() {
        if (this.markers.length > 0) {
            const group = new L.featureGroup(this.markers);
            this.map.fitBounds(group.getBounds().pad(0.1));
        } else {
            this.map.setView([40.7128, -74.0060], 11);
        }
        this.addActivity('Map centered', 'info');
    }

    toggleClusters() {
        const isVisible = this.clusterLayers.length > 0 && this.map.hasLayer(this.clusterLayers[0]);
        
        this.clusterLayers.forEach(layer => {
            if (isVisible) {
                this.map.removeLayer(layer);
            } else {
                this.map.addLayer(layer);
            }
        });
        
        this.addActivity(isVisible ? 'Clusters hidden' : 'Clusters shown', 'info');
    }

    // UI utility functions
    showLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.classList.remove('hidden');
        overlay.classList.add('flex');
    }

    hideLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.classList.add('hidden');
        overlay.classList.remove('flex');
    }

    // Activity feed management
    addActivity(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const activity = { timestamp, message, type };
        
        this.activityFeed.unshift(activity);
        
        // Keep only last 20 activities
        if (this.activityFeed.length > 20) {
            this.activityFeed.pop();
        }
        
        this.updateActivityFeed();
    }

    updateActivityFeed() {
        const feedContainer = document.getElementById('activityFeed');
        feedContainer.innerHTML = '';
        
        this.activityFeed.forEach(activity => {
            const activityElement = document.createElement('div');
            activityElement.className = 'text-sm p-2 bg-gray-50 rounded mb-1';
            
            let iconClass = 'fas fa-info-circle text-blue-500';
            if (activity.type === 'success') iconClass = 'fas fa-check-circle text-green-500';
            if (activity.type === 'error') iconClass = 'fas fa-exclamation-circle text-red-500';
            if (activity.type === 'warning') iconClass = 'fas fa-exclamation-triangle text-yellow-500';
            
            activityElement.innerHTML = `
                <div class="flex items-start space-x-2">
                    <i class="${iconClass} mt-0.5"></i>
                    <div class="flex-1">
                        <p class="text-gray-800">${activity.message}</p>
                        <p class="text-xs text-gray-500">${activity.timestamp}</p>
                    </div>
                </div>
            `;
            
            feedContainer.appendChild(activityElement);
        });
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new RouteOptimizationDashboard();
});
