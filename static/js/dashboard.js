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

    // Initialize Charts
    initializeCharts() {
        // Performance Chart
        const performanceCtx = document.getElementById('performanceChart').getContext('2d');
        this.performanceChart = new Chart(performanceCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Optimization Score',
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
            }
        });
    }

    // Initialize WebSocket (for future real-time updates)
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
        }, 5000);
    }

    // Update connection status
    updateConnectionStatus(status) {
        const statusIndicator = document.getElementById('connectionStatus');
        const statusText = document.getElementById('statusText');
        
        if (status === 'connected') {
            statusIndicator.style.color = '#10b981';
            statusText.textContent = 'Connected';
        } else {
            statusIndicator.style.color = '#ef4444';
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
            // First, extract stores from file (simplified - in real app, would parse file)
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
    
    // Extract stores from uploaded file (simplified version)
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

    // Fix orphaned code: wrap in async function
    async handleFileUpload(file) {
        if (!file) {
            this.showError('Please select a file');
            return;
        }

        this.optimizationInProgress = true;
        this.showLoadingOverlay();
        this.updateProgress(0, 'Uploading file...');

        try {
            // Prepare form data
            const formData = new FormData();
            formData.append('file', file);
            formData.append('proximity', document.getElementById('proximityToggle').checked ? 'on' : '');
            formData.append('time_start', document.getElementById('timeStart').value);
            formData.append('time_end', document.getElementById('timeEnd').value);

            // Step 1: Upload and process file
            this.updateProgress(20, 'Processing store data...');
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.currentStores = result.stores || [];

            // Step 2: Visualize original stores
            this.updateProgress(40, 'Visualizing stores on map...');
            await this.visualizeStores(this.currentStores);

            // Step 3: Apply clustering if enabled
            if (document.getElementById('proximityToggle').checked) {
                this.updateProgress(60, 'Applying proximity clustering...');
                await this.applyClustering();
            }

            // Step 4: Optimize routes
            this.updateProgress(80, 'Optimizing routes...');
            await this.optimizeRoutes();

            // Step 5: Update metrics and charts
            this.updateProgress(100, 'Updating metrics...');
            this.updateMetrics(result);
            this.updateCharts(result);

            this.updateProgress(100, 'Optimization complete!');
            setTimeout(() => {
                this.hideLoadingOverlay();
                this.optimizationInProgress = false;
            }, 1000);

        } catch (error) {
            console.error('Optimization failed:', error);
            this.showError('Optimization failed: ' + error.message);
            this.hideLoadingOverlay();
            this.optimizationInProgress = false;
        }
    }

    // Visualize stores on map
    async visualizeStores(stores) {
        this.clearMap();
        
        if (!stores || stores.length === 0) return;

        // Add markers for each store
        stores.forEach((store, index) => {
            const lat = parseFloat(store.latitude || store.lat);
            const lon = parseFloat(store.longitude || store.lon);
            
            if (isNaN(lat) || isNaN(lon)) return;

            const marker = L.marker([lat, lon], {
                icon: L.divIcon({
                    className: 'store-marker',
                    html: `<div class="marker-content">${index + 1}</div>`,
                    iconSize: [30, 30],
                    iconAnchor: [15, 15]
                })
            }).addTo(this.map);

            marker.bindPopup(`
                <div class="store-popup">
                    <h4>${store.name || 'Store ' + (index + 1)}</h4>
                    <p><strong>Chain:</strong> ${store.chain || 'N/A'}</p>
                    <p><strong>Address:</strong> ${store.address || 'N/A'}</p>
                    <p><strong>Sales:</strong> ${store.sales || 'N/A'}</p>
                </div>
            `);

            this.markers.push(marker);
        });

        // Auto-fit map to show all markers
        if (this.markers.length > 0) {
            const group = new L.featureGroup(this.markers);
            this.map.fitBounds(group.getBounds().pad(0.1));
        }

        // Animate marker appearance
        this.animateMarkers();
    }

    // Apply clustering visualization
    async applyClustering() {
        if (!this.currentStores || this.currentStores.length === 0) return;

        const radius = parseFloat(document.getElementById('clusterRadius').value);
        
        try {
            const response = await fetch('/api/v1/clusters', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    stores: this.currentStores,
                    radius_km: radius
                })
            });

            if (!response.ok) {
                throw new Error(`Clustering failed: ${response.status}`);
            }

            const clusterData = await response.json();
            this.clusters = clusterData.clusters || [];
            
            // Visualize clusters with different colors
            this.visualizeClusters(this.clusters);
            
        } catch (error) {
            console.error('Clustering failed:', error);
            this.showError('Clustering failed: ' + error.message);
        }
    }

    // Visualize clusters with colors
    visualizeClusters(clusters) {
        const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#dda0dd', '#98d8c8', '#fdcb6e', '#6c5ce7', '#fd79a8'];
        
        clusters.forEach((cluster, clusterIndex) => {
            const color = colors[clusterIndex % colors.length];
            
            if (cluster.length > 1) {
                // Draw cluster boundary
                const clusterBounds = cluster.map(store => [
                    parseFloat(store.latitude || store.lat),
                    parseFloat(store.longitude || store.lon)
                ]).filter(coord => !isNaN(coord[0]) && !isNaN(coord[1]));
                
                if (clusterBounds.length > 0) {
                    const clusterCircle = L.polygon(clusterBounds, {
                        color: color,
                        fillColor: color,
                        fillOpacity: 0.1,
                        weight: 2
                    }).addTo(this.map);
                    
                    this.routeLines.push(clusterCircle);
                }
            }
        });
    }

    // Optimize routes visualization
    async optimizeRoutes() {
        if (!this.currentStores || this.currentStores.length === 0) return;

        // Simulate route optimization with lines between stores
        const storeCoords = this.currentStores
            .map(store => [parseFloat(store.latitude || store.lat), parseFloat(store.longitude || store.lon)])
            .filter(coord => !isNaN(coord[0]) && !isNaN(coord[1]));

        if (storeCoords.length > 1) {
            const routeLine = L.polyline(storeCoords, {
                color: '#45b7d1',
                weight: 3,
                opacity: 0.7
            }).addTo(this.map);

            this.routeLines.push(routeLine);
        }
    }

    // Update metrics display
    updateMetrics(result) {
        const metrics = result.metrics || {};
        
        document.getElementById('totalStores').textContent = this.currentStores.length;
        document.getElementById('clusterCount').textContent = this.clusters.length;
        document.getElementById('optimizationScore').textContent = 
            Math.round(metrics.optimization_score || 0) + '%';
        document.getElementById('processingTime').textContent = 
            (metrics.processing_time || 0).toFixed(2) + 's';
    }

    // Update charts with new data
    updateCharts(result) {
        const metrics = result.metrics || {};
        const timestamp = new Date().toLocaleTimeString();
        
        // Update performance chart
        this.performanceChart.data.labels.push(timestamp);
        this.performanceChart.data.datasets[0].data.push(metrics.optimization_score || 0);
        this.performanceChart.data.datasets[1].data.push(metrics.processing_time || 0);
        
        // Keep only last 10 data points
        if (this.performanceChart.data.labels.length > 10) {
            this.performanceChart.data.labels.shift();
            this.performanceChart.data.datasets[0].data.shift();
            this.performanceChart.data.datasets[1].data.shift();
        }
        
        this.performanceChart.update();
        
        // Update cluster chart
        if (this.clusters.length > 0) {
            this.clusterChart.data.labels = this.clusters.map((cluster, index) => 
                `Cluster ${index + 1} (${cluster.length} stores)`
            );
            this.clusterChart.data.datasets[0].data = this.clusters.map(cluster => cluster.length);
            this.clusterChart.update();
        }
    }

    // Map interaction handlers
    onMapClick(e) {
        console.log('Map clicked at:', e.latlng);
    }

    clearMap() {
        // Clear all markers
        this.markers.forEach(marker => this.map.removeLayer(marker));
        this.markers = [];
        
        // Clear all route lines
        this.routeLines.forEach(line => this.map.removeLayer(line));
        this.routeLines = [];
        
        // Clear clusters
        this.clusters = [];
        
        // Reset metrics
        this.updateMetrics({});
    }

    centerMap() {
        if (this.markers.length > 0) {
            const group = new L.featureGroup(this.markers);
            this.map.fitBounds(group.getBounds().pad(0.1));
        } else {
            this.map.setView([40.7128, -74.0060], 10);
        }
    }

    toggleClusters() {
        // Toggle cluster visibility
        this.routeLines.forEach(line => {
            if (line.options.fillOpacity !== undefined) {
                line.setStyle({
                    fillOpacity: line.options.fillOpacity === 0.1 ? 0 : 0.1
                });
            }
        });
    }

    // UI Helper Methods
    updateProgress(percentage, message) {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        progressFill.style.width = percentage + '%';
        progressText.textContent = message;
    }

    showLoadingOverlay() {
        document.getElementById('loadingOverlay').classList.add('show');
    }

    hideLoadingOverlay() {
        document.getElementById('loadingOverlay').classList.remove('show');
        this.updateProgress(0, 'Ready to optimize');
    }

    showError(message) {
        alert('Error: ' + message);
        console.error('Dashboard error:', message);
    }

    // Animate markers appearing
    animateMarkers() {
        this.markers.forEach((marker, index) => {
            setTimeout(() => {
                marker.getElement().style.animation = 'bounceIn 0.6s ease-out';
            }, index * 100);
        });
    }
}

// Custom CSS for markers
const markerStyles = `
    .store-marker {
        background: #4f46e5;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
        font-size: 12px;
        transition: all 0.3s ease;
    }
    
    .store-marker:hover {
        transform: scale(1.2);
        z-index: 1000;
    }
    
    .marker-content {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
    }
    
    .store-popup {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        min-width: 200px;
    }
    
    .store-popup h4 {
        margin: 0 0 10px 0;
        color: #1f2937;
        font-size: 16px;
    }
    
    .store-popup p {
        margin: 5px 0;
        color: #6b7280;
        font-size: 14px;
    }
    
    @keyframes bounceIn {
        0% { transform: scale(0); opacity: 0; }
        50% { transform: scale(1.2); opacity: 0.8; }
        100% { transform: scale(1); opacity: 1; }
    }
`;

// Add marker styles to document
const styleElement = document.createElement('style');
styleElement.textContent = markerStyles;
document.head.appendChild(styleElement);

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new RouteOptimizationDashboard();
    console.log('🚀 RouteForce Dashboard initialized successfully!');
});
