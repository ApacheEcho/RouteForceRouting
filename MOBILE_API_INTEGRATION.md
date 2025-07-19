# 📱 Mobile App Integration Guide

## Overview

The RouteForce Routing platform now includes a comprehensive Mobile API designed for iOS and Android app integration. This API provides mobile-optimized endpoints for route optimization, real-time tracking, traffic-aware routing, and offline synchronization.

## 🚀 Mobile API Features

### Core Capabilities
- **Mobile-Optimized Route Optimization** - Compressed data for mobile consumption
- **Real-Time Driver Tracking** - GPS location updates and status management
- **Traffic-Aware Navigation** - Integration with traffic data for optimal routing
- **Offline Data Synchronization** - Sync data when devices come back online
- **Device Authentication** - Secure token-based authentication
- **WebSocket Integration** - Real-time updates and notifications

### Performance Optimizations
- **Data Compression** - Reduced payload sizes for mobile networks
- **Rate Limiting** - Appropriate limits for mobile usage patterns
- **Caching** - Intelligent caching for improved responsiveness
- **Batch Operations** - Efficient bulk data processing

## 📡 API Endpoints

### Base URL
```
https://your-domain.com/api/mobile
```

### Authentication
```http
POST /api/mobile/auth/token
Content-Type: application/json

{
    "device_id": "unique-device-identifier",
    "app_version": "1.0.0",
    "device_type": "iOS"
}
```

**Response:**
```json
{
    "success": true,
    "session_token": "uuid-session-token",
    "expires_at": "2025-07-20T12:00:00Z",
    "device_capabilities": {
        "gps_tracking": true,
        "real_time_updates": true,
        "offline_mode": true,
        "camera_integration": true
    }
}
```

### Route Optimization
```http
POST /api/mobile/routes/optimize
Content-Type: application/json
X-API-Key: your-api-key

{
    "stores": [
        {
            "id": "store_1",
            "name": "Store Name",
            "address": "123 Main St",
            "lat": 37.7749,
            "lng": -122.4194,
            "priority": 1
        }
    ],
    "preferences": {
        "algorithm": "genetic",
        "proximity": true
    },
    "compress_response": true,
    "max_waypoints": 23
}
```

### Traffic-Aware Routing
```http
POST /api/mobile/routes/traffic
Content-Type: application/json
X-API-Key: your-api-key

{
    "origin": "San Francisco, CA",
    "destination": "San Jose, CA",
    "waypoints": ["Palo Alto, CA"],
    "avoid_tolls": true,
    "traffic_model": "best_guess",
    "departure_time": "now",
    "include_steps": true
}
```

### Driver Location Updates
```http
POST /api/mobile/driver/location
Content-Type: application/json
X-API-Key: your-api-key

{
    "driver_id": "driver_123",
    "lat": 37.7749,
    "lng": -122.4194,
    "heading": 45,
    "speed": 25,
    "accuracy": 5.0,
    "timestamp": "2025-07-19T12:00:00Z"
}
```

### Driver Status Updates
```http
POST /api/mobile/driver/status
Content-Type: application/json
X-API-Key: your-api-key

{
    "driver_id": "driver_123",
    "status": "en_route",
    "metadata": {
        "route_id": "route_456",
        "next_stop": "store_789"
    }
}
```

**Valid Status Values:**
- `available` - Driver is available for assignments
- `busy` - Driver is occupied but not driving
- `en_route` - Driver is traveling to destination
- `delivering` - Driver is making delivery
- `break` - Driver is on break
- `offline` - Driver is offline

### Offline Data Sync
```http
POST /api/mobile/sync/offline
Content-Type: application/json
X-API-Key: your-api-key

{
    "device_id": "device_123",
    "offline_data": [
        {
            "type": "location_update",
            "data": {
                "driver_id": "driver_123",
                "lat": 37.7749,
                "lng": -122.4194,
                "timestamp": "2025-07-19T11:30:00Z"
            }
        }
    ]
}
```

## 📱 Mobile App Implementation

### iOS (Swift) Example

```swift
import Foundation
import CoreLocation

class RouteForceAPI {
    private let baseURL = "https://your-domain.com/api/mobile"
    private var sessionToken: String?
    private let apiKey = "your-api-key"
    
    // MARK: - Authentication
    func authenticate(deviceId: String, completion: @escaping (Bool) -> Void) {
        let url = URL(string: "\(baseURL)/auth/token")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = [
            "device_id": deviceId,
            "app_version": Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0.0",
            "device_type": "iOS"
        ]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            guard let data = data,
                  let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let token = json["session_token"] as? String else {
                completion(false)
                return
            }
            
            self.sessionToken = token
            completion(true)
        }.resume()
    }
    
    // MARK: - Location Updates
    func updateDriverLocation(driverId: String, location: CLLocation) {
        let url = URL(string: "\(baseURL)/driver/location")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
        
        let body = [
            "driver_id": driverId,
            "lat": location.coordinate.latitude,
            "lng": location.coordinate.longitude,
            "heading": location.course,
            "speed": location.speed,
            "accuracy": location.horizontalAccuracy,
            "timestamp": ISO8601DateFormatter().string(from: location.timestamp)
        ] as [String : Any]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request).resume()
    }
    
    // MARK: - Route Optimization
    func optimizeRoute(stores: [[String: Any]], completion: @escaping ([String: Any]?) -> Void) {
        let url = URL(string: "\(baseURL)/routes/optimize")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
        
        let body = [
            "stores": stores,
            "compress_response": true,
            "include_directions": true,
            "max_waypoints": 23
        ] as [String : Any]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            guard let data = data,
                  let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
                completion(nil)
                return
            }
            
            completion(json)
        }.resume()
    }
}
```

### Android (Kotlin) Example

```kotlin
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import org.json.JSONArray

class RouteForceAPI {
    private val baseUrl = "https://your-domain.com/api/mobile"
    private val client = OkHttpClient()
    private var sessionToken: String? = null
    private val apiKey = "your-api-key"
    
    // Authentication
    fun authenticate(deviceId: String, callback: (Boolean) -> Unit) {
        val json = JSONObject().apply {
            put("device_id", deviceId)
            put("app_version", "1.0.0")
            put("device_type", "Android")
        }
        
        val requestBody = json.toString().toRequestBody("application/json".toMediaType())
        val request = Request.Builder()
            .url("$baseUrl/auth/token")
            .post(requestBody)
            .build()
        
        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                callback(false)
            }
            
            override fun onResponse(call: Call, response: Response) {
                response.body?.string()?.let { responseBody ->
                    try {
                        val jsonResponse = JSONObject(responseBody)
                        sessionToken = jsonResponse.getString("session_token")
                        callback(true)
                    } catch (e: Exception) {
                        callback(false)
                    }
                } ?: callback(false)
            }
        })
    }
    
    // Location Updates
    fun updateDriverLocation(driverId: String, lat: Double, lng: Double, 
                           heading: Float, speed: Float) {
        val json = JSONObject().apply {
            put("driver_id", driverId)
            put("lat", lat)
            put("lng", lng)
            put("heading", heading)
            put("speed", speed)
            put("timestamp", System.currentTimeMillis())
        }
        
        val requestBody = json.toString().toRequestBody("application/json".toMediaType())
        val request = Request.Builder()
            .url("$baseUrl/driver/location")
            .addHeader("X-API-Key", apiKey)
            .post(requestBody)
            .build()
        
        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                // Handle error
            }
            
            override fun onResponse(call: Call, response: Response) {
                // Handle success
            }
        })
    }
    
    // Route Optimization
    fun optimizeRoute(stores: JSONArray, callback: (JSONObject?) -> Unit) {
        val json = JSONObject().apply {
            put("stores", stores)
            put("compress_response", true)
            put("include_directions", true)
            put("max_waypoints", 23)
        }
        
        val requestBody = json.toString().toRequestBody("application/json".toMediaType())
        val request = Request.Builder()
            .url("$baseUrl/routes/optimize")
            .addHeader("X-API-Key", apiKey)
            .post(requestBody)
            .build()
        
        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                callback(null)
            }
            
            override fun onResponse(call: Call, response: Response) {
                response.body?.string()?.let { responseBody ->
                    try {
                        callback(JSONObject(responseBody))
                    } catch (e: Exception) {
                        callback(null)
                    }
                } ?: callback(null)
            }
        })
    }
}
```

## 🔄 Real-Time Updates with WebSocket

### JavaScript Example
```javascript
// Connect to WebSocket for real-time updates
const socket = io('https://your-domain.com');

// Join driver room for location updates
socket.emit('join_room', { room: 'driver_123' });

// Listen for route updates
socket.on('route_update', (data) => {
    console.log('Route updated:', data);
    updateRouteDisplay(data);
});

// Listen for driver location updates
socket.on('driver_location_update', (data) => {
    console.log('Driver location updated:', data);
    updateDriverMarker(data);
});

// Send location update
function sendLocationUpdate(driverId, lat, lng) {
    socket.emit('driver_location', {
        driver_id: driverId,
        lat: lat,
        lng: lng,
        timestamp: new Date().toISOString()
    });
}
```

## 📊 Error Handling

### Standard Error Response
```json
{
    "success": false,
    "error": "Error description",
    "mobile_friendly": true,
    "error_code": "INVALID_REQUEST",
    "retry_after": "60 seconds"
}
```

### Common Error Codes
- `INVALID_REQUEST` - Malformed request data
- `UNAUTHORIZED` - Invalid or missing API key
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `DEVICE_NOT_FOUND` - Device not registered
- `ROUTE_OPTIMIZATION_FAILED` - Route generation failed
- `TRAFFIC_SERVICE_UNAVAILABLE` - Traffic API unavailable

## 🔐 Security Considerations

### API Key Management
- Use environment variables for API keys
- Implement key rotation mechanism
- Monitor API usage and quota

### Data Privacy
- Encrypt sensitive data in transit
- Implement proper data retention policies
- Follow GDPR/CCPA compliance requirements

### Device Authentication
- Implement device fingerprinting
- Use secure token storage
- Implement session timeout

## 📈 Performance Guidelines

### Best Practices
- **Batch Location Updates** - Send multiple locations in one request when possible
- **Compress Responses** - Use `compress_response: true` for large datasets
- **Cache Responses** - Implement client-side caching for static data
- **Offline Support** - Store data locally and sync when online

### Rate Limits
- Authentication: 10 requests/minute
- Location Updates: 60 requests/minute
- Route Optimization: 20 requests/minute
- Traffic Routing: 15 requests/minute
- General Endpoints: 30 requests/minute

## 🧪 Testing

### Running Tests
```bash
# Test mobile API endpoints
python test_mobile_api.py

# Expected output: All endpoints validated
```

### Integration Testing
```bash
# Start development server
python run_app.py

# Test from mobile simulator/device
curl -X POST http://localhost:5003/api/mobile/health
```

## 🚀 Deployment

### Production Considerations
- Configure proper SSL/TLS certificates
- Set up API rate limiting and monitoring
- Implement proper logging and analytics
- Configure CDN for static assets

### Environment Variables
```bash
# Required for mobile API
GOOGLE_MAPS_API_KEY=your-maps-api-key
MOBILE_API_KEY=your-mobile-api-key
WEBSOCKET_ORIGINS=your-mobile-app-domains
REDIS_URL=redis://localhost:6379
```

## 📚 Next Steps

1. **Set up API keys** and configure authentication
2. **Implement mobile app** using provided examples
3. **Test real-time features** with WebSocket integration
4. **Deploy to production** with proper monitoring
5. **Add analytics** to track mobile app usage

---

The Mobile API is now ready for integration with iOS and Android applications, providing a complete solution for mobile route optimization and driver tracking.
