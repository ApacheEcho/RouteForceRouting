//
//  RouteOptimizationViewController.swift
//  RouteForce iOS App
//
//  Main view controller for route optimization and real-time tracking
//

import UIKit
import MapKit
import CoreLocation

class RouteOptimizationViewController: UIViewController {
    
    // MARK: - IBOutlets
    @IBOutlet weak var mapView: MKMapView!
    @IBOutlet weak var storeTableView: UITableView!
    @IBOutlet weak var optimizeButton: UIButton!
    @IBOutlet weak var statusLabel: UILabel!
    @IBOutlet weak var algorithmSegmentedControl: UISegmentedControl!
    @IBOutlet weak var trafficToggle: UISwitch!
    @IBOutlet weak var activityIndicator: UIActivityIndicatorView!
    
    // MARK: - Properties
    private let routeForceAPI = RouteForceAPI()
    private let locationManager = CLLocationManager()
    private var stores: [Store] = []
    private var currentRoute: OptimizedRoute?
    private var routeOverlay: MKPolyline?
    private var driverId = "driver_\(UUID().uuidString)"
    
    // MARK: - View Lifecycle
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupMapView()
        setupLocationManager()
        setupTableView()
        loadSampleStores()
        
        // Monitor API connection status
        routeForceAPI.$connectionStatus
            .receive(on: DispatchQueue.main)
            .sink { [weak self] status in
                self?.updateConnectionStatus(status)
            }
            .store(in: &cancellables)
    }
    
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        requestLocationPermission()
    }
    
    // MARK: - UI Setup
    private func setupUI() {
        title = "RouteForce Optimization"
        
        // Configure optimize button
        optimizeButton.layer.cornerRadius = 8
        optimizeButton.backgroundColor = .systemBlue
        optimizeButton.setTitleColor(.white, for: .normal)
        
        // Configure algorithm selector
        algorithmSegmentedControl.removeAllSegments()
        for (index, algorithm) in OptimizationAlgorithm.allCases.enumerated() {
            algorithmSegmentedControl.insertSegment(withTitle: algorithm.rawValue.capitalized, at: index, animated: false)
        }
        algorithmSegmentedControl.selectedSegmentIndex = 0
        
        // Configure status label
        statusLabel.text = "Connecting to RouteForce..."
        statusLabel.textColor = .systemGray
    }
    
    private func setupMapView() {
        mapView.delegate = self
        mapView.showsUserLocation = true
        mapView.userTrackingMode = .none
        
        // Set initial region (San Francisco Bay Area)
        let initialRegion = MKCoordinateRegion(
            center: CLLocationCoordinate2D(latitude: 37.7749, longitude: -122.4194),
            latitudinalMeters: 50000,
            longitudinalMeters: 50000
        )
        mapView.setRegion(initialRegion, animated: false)
    }
    
    private func setupLocationManager() {
        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        locationManager.distanceFilter = 10 // Update every 10 meters
    }
    
    private func setupTableView() {
        storeTableView.delegate = self
        storeTableView.dataSource = self
        storeTableView.register(UITableViewCell.self, forCellReuseIdentifier: "StoreCell")
    }
    
    // MARK: - Sample Data
    private func loadSampleStores() {
        stores = [
            Store(id: "1", name: "Downtown Store", address: "123 Market St, San Francisco, CA", 
                  coordinate: CLLocationCoordinate2D(latitude: 37.7749, longitude: -122.4194), priority: 1),
            Store(id: "2", name: "Mission Store", address: "456 Mission St, San Francisco, CA", 
                  coordinate: CLLocationCoordinate2D(latitude: 37.7849, longitude: -122.4094), priority: 2),
            Store(id: "3", name: "Castro Store", address: "789 Castro St, San Francisco, CA", 
                  coordinate: CLLocationCoordinate2D(latitude: 37.7649, longitude: -122.4294), priority: 1),
            Store(id: "4", name: "Richmond Store", address: "321 Geary Blvd, San Francisco, CA", 
                  coordinate: CLLocationCoordinate2D(latitude: 37.7849, longitude: -122.4594), priority: 3),
            Store(id: "5", name: "Sunset Store", address: "654 Irving St, San Francisco, CA", 
                  coordinate: CLLocationCoordinate2D(latitude: 37.7449, longitude: -122.4594), priority: 2)
        ]
        
        addStoreAnnotations()
        storeTableView.reloadData()
    }
    
    private func addStoreAnnotations() {
        mapView.removeAnnotations(mapView.annotations.filter { !($0 is MKUserLocation) })
        
        for store in stores {
            let annotation = StoreAnnotation(store: store)
            mapView.addAnnotation(annotation)
        }
    }
    
    // MARK: - Actions
    @IBAction func optimizeButtonTapped(_ sender: UIButton) {
        guard !stores.isEmpty else {
            showAlert(title: "No Stores", message: "Please add stores to optimize a route.")
            return
        }
        
        startOptimization()
    }
    
    @IBAction func addStoreButtonTapped(_ sender: UIButton) {
        showAddStoreDialog()
    }
    
    @IBAction func trafficToggleChanged(_ sender: UISwitch) {
        if sender.isOn && currentRoute != nil {
            // If traffic is enabled and we have a route, get traffic-aware directions
            generateTrafficAwareRoute()
        }
    }
    
    // MARK: - Route Optimization
    private func startOptimization() {
        setOptimizationInProgress(true)
        
        let selectedAlgorithm = OptimizationAlgorithm.allCases[algorithmSegmentedControl.selectedSegmentIndex]
        let preferences = RoutePreferences(algorithm: selectedAlgorithm, useProximity: true)
        
        routeForceAPI.optimizeRoute(stores: stores, preferences: preferences) { [weak self] result in
            DispatchQueue.main.async {
                self?.setOptimizationInProgress(false)
                
                switch result {
                case .success(let optimizedRoute):
                    self?.handleOptimizedRoute(optimizedRoute)
                case .failure(let error):
                    self?.showAlert(title: "Optimization Failed", message: error.localizedDescription)
                }
            }
        }
    }
    
    private func handleOptimizedRoute(_ route: OptimizedRoute) {
        currentRoute = route
        statusLabel.text = "Route optimized: \(route.stops.count) stops, \(String(format: "%.1f", route.totalDistance))km, \(String(format: "%.0f", route.totalTime))min"
        statusLabel.textColor = .systemGreen
        
        // Update map with optimized route
        updateMapWithRoute(route)
        
        // Update table view with ordered stops
        updateTableViewWithRoute(route)
        
        // Generate traffic-aware route if enabled
        if trafficToggle.isOn {
            generateTrafficAwareRoute()
        }
    }
    
    private func generateTrafficAwareRoute() {
        guard let route = currentRoute, route.stops.count >= 2 else { return }
        
        let origin = CLLocationCoordinate2D(latitude: route.stops[0].lat, longitude: route.stops[0].lng)
        let destination = CLLocationCoordinate2D(latitude: route.stops.last!.lat, longitude: route.stops.last!.lng)
        
        let waypoints = route.stops.dropFirst().dropLast().map { 
            CLLocationCoordinate2D(latitude: $0.lat, longitude: $0.lng) 
        }
        
        let preferences = TrafficPreferences(trafficModel: .bestGuess)
        
        routeForceAPI.getTrafficRoute(from: origin, to: destination, waypoints: waypoints, preferences: preferences) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let trafficRoute):
                    self?.handleTrafficRoute(trafficRoute)
                case .failure(let error):
                    print("Traffic route failed: \(error)")
                }
            }
        }
    }
    
    private func handleTrafficRoute(_ trafficRoute: TrafficRoute) {
        // Update status with traffic information
        let totalDuration = trafficRoute.legs.reduce(0) { $0 + ($1.durationInTraffic?.value ?? $1.duration?.value ?? 0) }
        statusLabel.text = "Traffic-aware route: \(String(format: "%.0f", Double(totalDuration) / 60))min with current traffic"
        statusLabel.textColor = .systemOrange
        
        // Draw traffic-aware route on map
        drawTrafficRoute(trafficRoute)
    }
    
    // MARK: - Map Updates
    private func updateMapWithRoute(_ route: OptimizedRoute) {
        // Remove existing route overlay
        if let overlay = routeOverlay {
            mapView.removeOverlay(overlay)
        }
        
        // Create coordinates array from route stops
        let coordinates = route.stops.map { CLLocationCoordinate2D(latitude: $0.lat, longitude: $0.lng) }
        
        // Create polyline
        routeOverlay = MKPolyline(coordinates: coordinates, count: coordinates.count)
        mapView.addOverlay(routeOverlay!)
        
        // Update annotations with order numbers
        updateAnnotationsWithOrder(route)
        
        // Fit map to show all stops
        fitMapToRoute(coordinates)
    }
    
    private func updateAnnotationsWithOrder(_ route: OptimizedRoute) {
        for (index, stop) in route.stops.enumerated() {
            if let annotation = mapView.annotations.first(where: { ann in
                if let storeAnn = ann as? StoreAnnotation {
                    return storeAnn.store.id == stop.id
                }
                return false
            }) as? StoreAnnotation {
                annotation.orderNumber = index + 1
            }
        }
        
        // Refresh annotation views
        for annotation in mapView.annotations {
            if let view = mapView.view(for: annotation) {
                view.setNeedsDisplay()
            }
        }
    }
    
    private func drawTrafficRoute(_ trafficRoute: TrafficRoute) {
        // This would require decoding the polyline from Google Maps
        // For now, we'll show a simplified representation
        statusLabel.text += " (Traffic data loaded)"
    }
    
    private func fitMapToRoute(_ coordinates: [CLLocationCoordinate2D]) {
        guard !coordinates.isEmpty else { return }
        
        let mapRect = coordinates.reduce(MKMapRect.null) { rect, coordinate in
            let point = MKMapPoint(coordinate)
            let pointRect = MKMapRect(x: point.x, y: point.y, width: 0, height: 0)
            return rect.union(pointRect)
        }
        
        let padding = UIEdgeInsets(top: 50, left: 50, bottom: 50, right: 50)
        mapView.setVisibleMapRect(mapRect, edgePadding: padding, animated: true)
    }
    
    // MARK: - Table View Updates
    private func updateTableViewWithRoute(_ route: OptimizedRoute) {
        // Reorder stores based on optimized route
        let orderedStores = route.stops.compactMap { stop in
            stores.first { $0.id == stop.id }
        }
        stores = orderedStores
        storeTableView.reloadData()
    }
    
    // MARK: - Location Tracking
    private func requestLocationPermission() {
        switch locationManager.authorizationStatus {
        case .notDetermined:
            locationManager.requestWhenInUseAuthorization()
        case .authorizedWhenInUse, .authorizedAlways:
            startLocationTracking()
        case .denied, .restricted:
            showLocationPermissionAlert()
        @unknown default:
            break
        }
    }
    
    private func startLocationTracking() {
        guard CLLocationManager.locationServicesEnabled() else { return }
        locationManager.startUpdatingLocation()
    }
    
    // MARK: - Helper Methods
    private func setOptimizationInProgress(_ inProgress: Bool) {
        optimizeButton.isEnabled = !inProgress
        if inProgress {
            activityIndicator.startAnimating()
            statusLabel.text = "Optimizing route..."
            statusLabel.textColor = .systemBlue
        } else {
            activityIndicator.stopAnimating()
        }
    }
    
    private func updateConnectionStatus(_ status: RouteForceAPI.ConnectionStatus) {
        switch status {
        case .connected:
            statusLabel.text = "Connected to RouteForce"
            statusLabel.textColor = .systemGreen
        case .connecting:
            statusLabel.text = "Connecting to RouteForce..."
            statusLabel.textColor = .systemBlue
        case .disconnected:
            statusLabel.text = "Disconnected from RouteForce"
            statusLabel.textColor = .systemRed
        }
    }
    
    private func showAddStoreDialog() {
        let alert = UIAlertController(title: "Add Store", message: "Enter store details", preferredStyle: .alert)
        
        alert.addTextField { textField in
            textField.placeholder = "Store Name"
        }
        alert.addTextField { textField in
            textField.placeholder = "Address"
        }
        alert.addTextField { textField in
            textField.placeholder = "Priority (1-5)"
            textField.keyboardType = .numberPad
        }
        
        let addAction = UIAlertAction(title: "Add", style: .default) { [weak self] _ in
            guard let nameField = alert.textFields?[0],
                  let addressField = alert.textFields?[1],
                  let priorityField = alert.textFields?[2],
                  let name = nameField.text, !name.isEmpty,
                  let address = addressField.text, !address.isEmpty,
                  let priorityText = priorityField.text,
                  let priority = Int(priorityText) else {
                self?.showAlert(title: "Invalid Input", message: "Please fill all fields correctly.")
                return
            }
            
            self?.geocodeAndAddStore(name: name, address: address, priority: priority)
        }
        
        alert.addAction(addAction)
        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel))
        
        present(alert, animated: true)
    }
    
    private func geocodeAndAddStore(name: String, address: String, priority: Int) {
        let geocoder = CLGeocoder()
        geocoder.geocodeAddressString(address) { [weak self] placemarks, error in
            DispatchQueue.main.async {
                guard let placemark = placemarks?.first,
                      let location = placemark.location else {
                    self?.showAlert(title: "Geocoding Failed", message: "Could not find location for address.")
                    return
                }
                
                let store = Store(
                    id: UUID().uuidString,
                    name: name,
                    address: address,
                    coordinate: location.coordinate,
                    priority: priority
                )
                
                self?.stores.append(store)
                self?.addStoreAnnotations()
                self?.storeTableView.reloadData()
            }
        }
    }
    
    private func showAlert(title: String, message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
    
    private func showLocationPermissionAlert() {
        let alert = UIAlertController(
            title: "Location Permission Required",
            message: "This app needs location access to provide optimal routing. Please enable location access in Settings.",
            preferredStyle: .alert
        )
        
        alert.addAction(UIAlertAction(title: "Settings", style: .default) { _ in
            if let settingsURL = URL(string: UIApplication.openSettingsURLString) {
                UIApplication.shared.open(settingsURL)
            }
        })
        
        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel))
        present(alert, animated: true)
    }
    
    // MARK: - Properties for Combine
    private var cancellables = Set<AnyCancellable>()
}

// MARK: - UITableViewDataSource
extension RouteOptimizationViewController: UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return stores.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "StoreCell", for: indexPath)
        let store = stores[indexPath.row]
        
        cell.textLabel?.text = "\(indexPath.row + 1). \(store.name)"
        cell.detailTextLabel?.text = store.address
        cell.accessoryType = .detailDisclosureButton
        
        return cell
    }
}

// MARK: - UITableViewDelegate
extension RouteOptimizationViewController: UITableViewDelegate {
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        
        let store = stores[indexPath.row]
        let coordinate = store.coordinate
        let region = MKCoordinateRegion(center: coordinate, latitudinalMeters: 1000, longitudinalMeters: 1000)
        mapView.setRegion(region, animated: true)
    }
    
    func tableView(_ tableView: UITableView, commit editingStyle: UITableViewCell.EditingStyle, forRowAt indexPath: IndexPath) {
        if editingStyle == .delete {
            stores.remove(at: indexPath.row)
            tableView.deleteRows(at: [indexPath], with: .fade)
            addStoreAnnotations()
        }
    }
}

// MARK: - MKMapViewDelegate
extension RouteOptimizationViewController: MKMapViewDelegate {
    func mapView(_ mapView: MKMapView, viewFor annotation: MKAnnotation) -> MKAnnotationView? {
        guard let storeAnnotation = annotation as? StoreAnnotation else {
            return nil
        }
        
        let identifier = "StoreAnnotation"
        var annotationView = mapView.dequeueReusableAnnotationView(withIdentifier: identifier)
        
        if annotationView == nil {
            annotationView = MKMarkerAnnotationView(annotation: annotation, reuseIdentifier: identifier)
            annotationView?.canShowCallout = true
            annotationView?.rightCalloutAccessoryView = UIButton(type: .detailDisclosure)
        } else {
            annotationView?.annotation = annotation
        }
        
        if let markerView = annotationView as? MKMarkerAnnotationView {
            markerView.markerTintColor = storeAnnotation.markerColor
            markerView.glyphText = storeAnnotation.orderNumber > 0 ? "\(storeAnnotation.orderNumber)" : nil
        }
        
        return annotationView
    }
    
    func mapView(_ mapView: MKMapView, rendererFor overlay: MKOverlay) -> MKOverlayRenderer {
        if let polyline = overlay as? MKPolyline {
            let renderer = MKPolylineRenderer(polyline: polyline)
            renderer.strokeColor = .systemBlue
            renderer.lineWidth = 3.0
            return renderer
        }
        return MKOverlayRenderer(overlay: overlay)
    }
    
    func mapView(_ mapView: MKMapView, annotationView view: MKAnnotationView, calloutAccessoryControlTapped control: UIControl) {
        guard let storeAnnotation = view.annotation as? StoreAnnotation else { return }
        
        let alert = UIAlertController(title: storeAnnotation.store.name, message: storeAnnotation.store.address, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}

// MARK: - CLLocationManagerDelegate
extension RouteOptimizationViewController: CLLocationManagerDelegate {
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.last else { return }
        
        // Update driver location via API
        routeForceAPI.updateDriverLocation(location, driverId: driverId)
    }
    
    func locationManager(_ manager: CLLocationManager, didChangeAuthorization status: CLAuthorizationStatus) {
        switch status {
        case .authorizedWhenInUse, .authorizedAlways:
            startLocationTracking()
        case .denied, .restricted:
            showLocationPermissionAlert()
        default:
            break
        }
    }
    
    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        print("Location error: \(error)")
    }
}

// MARK: - Custom Annotation
class StoreAnnotation: NSObject, MKAnnotation {
    let store: Store
    var orderNumber: Int = 0
    
    var coordinate: CLLocationCoordinate2D {
        return store.coordinate
    }
    
    var title: String? {
        return store.name
    }
    
    var subtitle: String? {
        return store.address
    }
    
    var markerColor: UIColor {
        switch store.priority {
        case 1: return .systemRed
        case 2: return .systemOrange
        case 3: return .systemYellow
        default: return .systemBlue
        }
    }
    
    init(store: Store) {
        self.store = store
        super.init()
    }
}
