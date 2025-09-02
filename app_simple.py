from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({'message': 'RouteForce API is running!'})

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/api/dashboard/stats')
def stats():
    return jsonify({
        'total_routes': 42,
        'active_routes': 5,
        'total_drivers': 12,
        'available_drivers': 8,
        'total_vehicles': 15,
        'deliveries_today': 23,
        'on_time_rate': 95
    })

@app.route('/api/routes')
def routes():
    return jsonify([
        {'id': 1, 'name': 'Route A', 'status': 'active', 'stops': 5},
        {'id': 2, 'name': 'Route B', 'status': 'completed', 'stops': 8},
        {'id': 3, 'name': 'Route C', 'status': 'pending', 'stops': 6}
    ])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
