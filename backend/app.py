from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import jwt
import datetime
from functools import wraps

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

# Load secret from env or fallback
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')

# Helper to create token
def create_token(username, role, expires_minutes=60):
    payload = {
        'sub': username,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_minutes)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

# Helper to decode token
def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except Exception:
        return None

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

# Update login endpoint to issue JWT
@app.route('/api/login', methods=['POST'])
def login():
    payload = request.get_json() or {}
    username = payload.get('username', 'dev')
    role = payload.get('role', 'manager')
    # Issue JWT for development
    token = create_token(username, role)
    return jsonify({'token': token, 'role': role}), 200

# Middleware helper to require auth for certain endpoints
def require_auth(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized'}), 401
        token = auth.split(' ', 1)[1]
        decoded = decode_token(token)
        if not decoded:
            return jsonify({'error': 'Invalid or expired token'}), 401
        # attach user info to request context (simple)
        request.user = decoded
        return f(*args, **kwargs)
    return wrapped

# Protect analytics endpoint
@app.route('/api/analytics')
@require_auth
def get_analytics():
    return jsonify(ANALYTICS)

# example protected endpoint (dev) that requires Authorization header
@app.route('/api/protected')
def protected():
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return jsonify({'error': 'missing token'}), 401
    token = auth.split(' ', 1)[1]
    data = decode_token(token)
    if not data:
        return jsonify({'error': 'invalid token'}), 401
    return jsonify({'user': data.get('sub'), 'role': data.get('role')})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
