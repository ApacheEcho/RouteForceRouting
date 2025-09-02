"""Main application entry point."""
import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/routeforce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app, origins=['http://localhost:3000'])

# Simple models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)

class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='pending')

# Routes
@app.route('/')
def home():
    return jsonify({
        'message': 'RouteForce API is running!',
        'version': '1.0.0'
    })

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/api/dashboard/stats')
def dashboard_stats():
    return jsonify({
        'total_routes': 42,
        'active_routes': 5,
        'total_drivers': 12,
        'available_drivers': 8,
        'total_vehicles': 15,
        'deliveries_today': 23,
        'on_time_rate': 95
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
