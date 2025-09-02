from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Mock data, mirror frontend mock shapes
ROUTES = [
    {"id": 1, "origin": "A", "destination": "B", "status": "active", "name": "Route A→B", "stops": 5, "distance": 12},
    {"id": 2, "origin": "B", "destination": "C", "status": "planned", "name": "Route B→C", "stops": 8, "distance": 25}
]

VEHICLES = [
    {"id": 1, "number": "RF-1001", "type": "Van", "status": "active", "mileage": 12000, "fuel": 78},
    {"id": 2, "number": "RF-1002", "type": "Truck", "status": "maintenance", "mileage": 54000, "fuel": 34}
]

DRIVERS = [
    {"id": 1, "name": "Alice Johnson", "status": "on-duty", "routes": 2, "rating": 4.9, "phone": "555-0101"},
    {"id": 2, "name": "Bob Smith", "status": "on-break", "routes": 1, "rating": 4.6, "phone": "555-0102"}
]

ANALYTICS = {
    "totalRoutes": 2,
    "activeVehicles": 1,
    "completedDeliveries": 10,
    "onTimeRate": 95,
    "avgDeliveryTime": 28,
    "costPerMile": 2.34,
    "fuelEfficiency": 8.6,
    "totalDeliveries": 120
}

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/api/routes")
def get_routes():
    return jsonify(ROUTES)

@app.route("/api/vehicles")
def get_vehicles():
    return jsonify(VEHICLES)

@app.route("/api/drivers")
def get_drivers():
    return jsonify(DRIVERS)

@app.route("/api/analytics")
def get_analytics():
    return jsonify(ANALYTICS)

# Single development login endpoint: returns a mock token and the selected role.
@app.route('/api/login', methods=['POST'])
def login():
    payload = request.get_json() or {}
    username = payload.get('username', 'dev')
    role = payload.get('role', 'manager')
    # NOTE: Development-only mock auth. Replace with real auth/JWT in production.
    token = f'dev-token:{username}'
    return jsonify({'token': token, 'role': role}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
