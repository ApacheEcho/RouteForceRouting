//
//  RouteForceAPI.swift
//  RouteForce iOS App
//
//  Core API client for RouteForce Routing platform
//  Provides mobile-optimized route optimization and real-time tracking
//

import Foundation
import CoreLocation

class RouteForceAPI: ObservableObject {
    
    // MARK: - Configuration
    private let baseURL = "https://your-domain.com/api/mobile"
    private let apiKey = "your-api-key"
    private var sessionToken: String?
    private let deviceId = UIDevice.current.identifierForVendor?.uuidString ?? UUID().uuidString
    
    // MARK: - Session Management
    @Published var isAuthenticated = false
    @Published var connectionStatus: ConnectionStatus = .disconnected
    
    enum ConnectionStatus {
        case connected, disconnected, connecting
    }
    
    // MARK: - Initialization
    init() {
        authenticate()
    }
    
    // MARK: - Authentication
    func authenticate(completion: @escaping (Bool) -> Void = { _ in }) {
        connectionStatus = .connecting
        
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
        
        URLSession.shared.dataTask(with: request) { [weak self] data, response, error in
            DispatchQueue.main.async {
                guard let data = data,
                      let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                      let success = json["success"] as? Bool,
                      success,
                      let token = json["session_token"] as? String else {
                    self?.connectionStatus = .disconnected
                    self?.isAuthenticated = false
                    completion(false)
                    return
                }
                
                self?.sessionToken = token
                self?.isAuthenticated = true
                self?.connectionStatus = .connected
                completion(true)
            }
        }.resume()
    }
    
    // MARK: - Route Optimization
    func optimizeRoute(stores: [Store], 
                      preferences: RoutePreferences = RoutePreferences(),
                      completion: @escaping (Result<OptimizedRoute, APIError>) -> Void) {
        
        guard isAuthenticated else {
            completion(.failure(.notAuthenticated))
            return
        }
        
        let url = URL(string: "\(baseURL)/routes/optimize")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
        request.setValue(deviceId, forHTTPHeaderField: "X-Device-ID")
        
        let storeData = stores.map { store in
            [
                "id": store.id,
                "name": store.name,
                "address": store.address,
                "lat": store.coordinate.latitude,
                "lng": store.coordinate.longitude,
                "priority": store.priority
            ]
        }
        
        let body: [String: Any] = [
            "stores": storeData,
            "preferences": [
                "algorithm": preferences.algorithm.rawValue,
                "proximity": preferences.useProximity
            ],
            "compress_response": true,
            "include_directions": true,
            "max_waypoints": 23,
            "device_id": deviceId,
            "app_version": Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0.0",
            "device_type": "iOS"
        ]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                guard let data = data else {
                    completion(.failure(.networkError))
                    return
                }
                
                do {
                    let result = try JSONDecoder().decode(RouteOptimizationResponse.self, from: data)
                    if result.success {
                        completion(.success(result.route))
                    } else {
                        completion(.failure(.serverError(result.error ?? "Unknown error")))
                    }
                } catch {
                    completion(.failure(.decodingError))
                }
            }
        }.resume()
    }
    
    // MARK: - Traffic-Aware Routing
    func getTrafficRoute(from origin: CLLocationCoordinate2D,
                        to destination: CLLocationCoordinate2D,
                        waypoints: [CLLocationCoordinate2D] = [],
                        preferences: TrafficPreferences = TrafficPreferences(),
                        completion: @escaping (Result<TrafficRoute, APIError>) -> Void) {
        
        guard isAuthenticated else {
            completion(.failure(.notAuthenticated))
            return
        }
        
        let url = URL(string: "\(baseURL)/routes/traffic")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
        
        let body: [String: Any] = [
            "origin": "\(origin.latitude),\(origin.longitude)",
            "destination": "\(destination.latitude),\(destination.longitude)",
            "waypoints": waypoints.map { "\($0.latitude),\($0.longitude)" },
            "avoid_tolls": preferences.avoidTolls,
            "avoid_highways": preferences.avoidHighways,
            "traffic_model": preferences.trafficModel.rawValue,
            "departure_time": preferences.departureTime,
            "include_steps": true
        ]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                guard let data = data else {
                    completion(.failure(.networkError))
                    return
                }
                
                do {
                    let result = try JSONDecoder().decode(TrafficRouteResponse.self, from: data)
                    if result.success {
                        completion(.success(result.directions))
                    } else {
                        completion(.failure(.serverError(result.error ?? "Unknown error")))
                    }
                } catch {
                    completion(.failure(.decodingError))
                }
            }
        }.resume()
    }
    
    // MARK: - Driver Location Updates
    func updateDriverLocation(_ location: CLLocation, driverId: String) {
        guard isAuthenticated else { return }
        
        let url = URL(string: "\(baseURL)/driver/location")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
        
        let body: [String: Any] = [
            "driver_id": driverId,
            "lat": location.coordinate.latitude,
            "lng": location.coordinate.longitude,
            "heading": location.course >= 0 ? location.course : 0,
            "speed": location.speed >= 0 ? location.speed : 0,
            "accuracy": location.horizontalAccuracy,
            "timestamp": ISO8601DateFormatter().string(from: location.timestamp)
        ]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            // Handle response silently for location updates
            if let error = error {
                print("Location update failed: \(error)")
            }
        }.resume()
    }
    
    // MARK: - Driver Status Updates
    func updateDriverStatus(_ status: DriverStatus, driverId: String, metadata: [String: Any] = [:]) {
        guard isAuthenticated else { return }
        
        let url = URL(string: "\(baseURL)/driver/status")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
        
        let body: [String: Any] = [
            "driver_id": driverId,
            "status": status.rawValue,
            "metadata": metadata
        ]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request).resume()
    }
    
    // MARK: - Offline Data Sync
    func syncOfflineData(_ offlineData: [OfflineDataItem], completion: @escaping (Bool) -> Void) {
        guard isAuthenticated else {
            completion(false)
            return
        }
        
        let url = URL(string: "\(baseURL)/sync/offline")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
        
        let body: [String: Any] = [
            "device_id": deviceId,
            "offline_data": offlineData.map { $0.toDictionary() }
        ]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                guard let data = data,
                      let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                      let success = json["success"] as? Bool else {
                    completion(false)
                    return
                }
                
                completion(success)
            }
        }.resume()
    }
    
    // MARK: - Health Check
    func checkHealth(completion: @escaping (Bool) -> Void) {
        let url = URL(string: "\(baseURL)/health")!
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                guard let data = data,
                      let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                      json["status"] as? String == "healthy" else {
                    completion(false)
                    return
                }
                
                completion(true)
            }
        }.resume()
    }
}

// MARK: - Data Models

struct Store: Identifiable, Codable {
    let id: String
    let name: String
    let address: String
    let coordinate: CLLocationCoordinate2D
    let priority: Int
    
    enum CodingKeys: String, CodingKey {
        case id, name, address, priority
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        name = try container.decode(String.self, forKey: .name)
        address = try container.decode(String.self, forKey: .address)
        priority = try container.decode(Int.self, forKey: .priority)
        
        // Note: CLLocationCoordinate2D needs special handling
        coordinate = CLLocationCoordinate2D(latitude: 0, longitude: 0)
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(id, forKey: .id)
        try container.encode(name, forKey: .name)
        try container.encode(address, forKey: .address)
        try container.encode(priority, forKey: .priority)
    }
}

struct RoutePreferences {
    let algorithm: OptimizationAlgorithm
    let useProximity: Bool
    
    init(algorithm: OptimizationAlgorithm = .genetic, useProximity: Bool = true) {
        self.algorithm = algorithm
        self.useProximity = useProximity
    }
}

enum OptimizationAlgorithm: String, CaseIterable {
    case genetic = "genetic"
    case simulatedAnnealing = "simulated_annealing"
    case nearestNeighbor = "nearest_neighbor"
}

struct TrafficPreferences {
    let avoidTolls: Bool
    let avoidHighways: Bool
    let trafficModel: TrafficModel
    let departureTime: String
    
    init(avoidTolls: Bool = false, 
         avoidHighways: Bool = false, 
         trafficModel: TrafficModel = .bestGuess, 
         departureTime: String = "now") {
        self.avoidTolls = avoidTolls
        self.avoidHighways = avoidHighways
        self.trafficModel = trafficModel
        self.departureTime = departureTime
    }
}

enum TrafficModel: String, CaseIterable {
    case bestGuess = "best_guess"
    case pessimistic = "pessimistic"
    case optimistic = "optimistic"
}

enum DriverStatus: String, CaseIterable {
    case available = "available"
    case busy = "busy"
    case enRoute = "en_route"
    case delivering = "delivering"
    case onBreak = "break"
    case offline = "offline"
}

struct OptimizedRoute: Codable {
    let id: String
    let stops: [RouteStop]
    let totalDistance: Double
    let totalTime: Double
    let optimized: Bool
    
    enum CodingKeys: String, CodingKey {
        case id, stops
        case totalDistance = "total_distance"
        case totalTime = "total_time"
        case optimized
    }
}

struct RouteStop: Codable, Identifiable {
    let id: String
    let name: String
    let address: String
    let lat: Double
    let lng: Double
    let order: Int
}

struct TrafficRoute: Codable {
    let overviewPolyline: String?
    let bounds: RouteBounds?
    let legs: [RouteLeg]
    let warnings: [String]
    
    enum CodingKeys: String, CodingKey {
        case overviewPolyline = "overview_polyline"
        case bounds, legs, warnings
    }
}

struct RouteBounds: Codable {
    let northeast: Coordinate
    let southwest: Coordinate
}

struct Coordinate: Codable {
    let lat: Double
    let lng: Double
}

struct RouteLeg: Codable {
    let distance: RouteDistance?
    let duration: RouteDuration?
    let durationInTraffic: RouteDuration?
    let startLocation: Coordinate
    let endLocation: Coordinate
    let steps: [RouteStep]
    
    enum CodingKeys: String, CodingKey {
        case distance, duration
        case durationInTraffic = "duration_in_traffic"
        case startLocation = "start_location"
        case endLocation = "end_location"
        case steps
    }
}

struct RouteDistance: Codable {
    let text: String
    let value: Int
}

struct RouteDuration: Codable {
    let text: String
    let value: Int
}

struct RouteStep: Codable {
    let distance: RouteDistance?
    let duration: RouteDuration?
    let htmlInstructions: String
    let maneuver: String?
    let startLocation: Coordinate
    let endLocation: Coordinate
    let polyline: String?
    
    enum CodingKeys: String, CodingKey {
        case distance, duration, maneuver, polyline
        case htmlInstructions = "html_instructions"
        case startLocation = "start_location"
        case endLocation = "end_location"
    }
}

struct RouteOptimizationResponse: Codable {
    let success: Bool
    let route: OptimizedRoute
    let optimizationTime: Double?
    let mobileOptimized: Bool
    let error: String?
    
    enum CodingKeys: String, CodingKey {
        case success, route, error
        case optimizationTime = "optimization_time"
        case mobileOptimized = "mobile_optimized"
    }
}

struct TrafficRouteResponse: Codable {
    let success: Bool
    let directions: TrafficRoute
    let trafficInfo: [String: Any]?
    let alternatives: [TrafficRoute]
    let mobileFormatted: Bool
    let error: String?
    
    enum CodingKeys: String, CodingKey {
        case success, directions, alternatives, error
        case mobileFormatted = "mobile_formatted"
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        success = try container.decode(Bool.self, forKey: .success)
        directions = try container.decode(TrafficRoute.self, forKey: .directions)
        alternatives = try container.decode([TrafficRoute].self, forKey: .alternatives)
        mobileFormatted = try container.decode(Bool.self, forKey: .mobileFormatted)
        error = try container.decodeIfPresent(String.self, forKey: .error)
        
        // trafficInfo contains Any, so we'll skip it for now
        trafficInfo = nil
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(success, forKey: .success)
        try container.encode(directions, forKey: .directions)
        try container.encode(alternatives, forKey: .alternatives)
        try container.encode(mobileFormatted, forKey: .mobileFormatted)
        try container.encodeIfPresent(error, forKey: .error)
    }
}

struct OfflineDataItem {
    let type: String
    let data: [String: Any]
    let timestamp: Date
    
    func toDictionary() -> [String: Any] {
        return [
            "type": type,
            "data": data,
            "timestamp": ISO8601DateFormatter().string(from: timestamp)
        ]
    }
}

enum APIError: Error, LocalizedError {
    case notAuthenticated
    case networkError
    case serverError(String)
    case decodingError
    
    var errorDescription: String? {
        switch self {
        case .notAuthenticated:
            return "Not authenticated with RouteForce API"
        case .networkError:
            return "Network connection error"
        case .serverError(let message):
            return "Server error: \(message)"
        case .decodingError:
            return "Failed to decode server response"
        }
    }
}
