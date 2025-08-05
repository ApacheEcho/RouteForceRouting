"""
API Documentation Configuration using Flask-RESTX
Provides automated API documentation generation and Swagger UI
"""

from flask import Blueprint
from flask_restx import Api, Resource, fields, Namespace
from app.config import Config

# Create documentation blueprint
doc_bp = Blueprint('api_docs', __name__)

# Configure API documentation
api = Api(
    doc_bp,
    version='1.0.0',
    title='RouteForce Routing API',
    description='Enterprise-grade route optimization and field execution API',
    doc='/docs/',  # Swagger UI endpoint
    prefix='/api',
    contact_email='dev@routeforce.com',
    license='MIT',
    license_url='https://opensource.org/licenses/MIT',
    authorizations={
        'Bearer Token': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Bearer token. Format: Bearer <token>'
        },
        'API Key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-API-Key',
            'description': 'API key for authentication'
        }
    },
    security='Bearer Token'
)

# Define common data models for documentation
error_model = api.model('Error', {
    'error': fields.String(required=True, description='Error message'),
    'status_code': fields.Integer(required=True, description='HTTP status code'),
    'timestamp': fields.DateTime(required=True, description='Error timestamp')
})

success_model = api.model('Success', {
    'success': fields.Boolean(required=True, description='Operation success status'),
    'message': fields.String(required=True, description='Success message'),
    'data': fields.Raw(description='Response data')
})

# Store data model
store_model = api.model('Store', {
    'name': fields.String(required=True, description='Store name', example='Store A'),
    'address': fields.String(required=True, description='Store address', example='123 Main St, New York, NY 10001'),
    'latitude': fields.Float(description='Store latitude', example=40.7128),
    'longitude': fields.Float(description='Store longitude', example=-74.0060),
    'priority': fields.Integer(description='Store priority (1-10)', example=5),
    'time_window_start': fields.String(description='Opening time', example='09:00'),
    'time_window_end': fields.String(description='Closing time', example='17:00')
})

# Route constraints model
constraints_model = api.model('RouteConstraints', {
    'max_distance': fields.Float(description='Maximum route distance in kilometers', example=100.0),
    'max_duration': fields.Integer(description='Maximum route duration in minutes', example=480),
    'vehicle_capacity': fields.Integer(description='Vehicle capacity', example=1000),
    'start_location': fields.Nested(store_model, description='Starting location'),
    'end_location': fields.Nested(store_model, description='Ending location')
})

# Algorithm options model
algorithm_options_model = api.model('AlgorithmOptions', {
    'algorithm': fields.String(
        required=False, 
        description='Optimization algorithm to use',
        enum=['default', 'genetic', 'simulated_annealing', 'multi_objective'],
        default='default',
        example='genetic'
    ),
    'ga_population_size': fields.Integer(description='Genetic algorithm population size', example=100),
    'ga_generations': fields.Integer(description='Genetic algorithm generations', example=500),
    'ga_mutation_rate': fields.Float(description='Genetic algorithm mutation rate', example=0.02),
    'sa_initial_temperature': fields.Float(description='Simulated annealing initial temperature', example=1000.0),
    'sa_cooling_rate': fields.Float(description='Simulated annealing cooling rate', example=0.99)
})

# Route request model
route_request_model = api.model('RouteRequest', {
    'stores': fields.List(fields.Nested(store_model), required=True, description='List of stores to visit'),
    'constraints': fields.Nested(constraints_model, description='Route constraints'),
    'options': fields.Nested(algorithm_options_model, description='Algorithm options')
})

# Route response model
route_response_model = api.model('RouteResponse', {
    'route_id': fields.String(required=True, description='Unique route identifier'),
    'optimized_route': fields.List(fields.Nested(store_model), description='Optimized store sequence'),
    'total_distance': fields.Float(description='Total route distance in kilometers'),
    'total_duration': fields.Integer(description='Total route duration in minutes'),
    'algorithm_used': fields.String(description='Algorithm used for optimization'),
    'optimization_time': fields.Float(description='Time taken to optimize in seconds'),
    'google_maps_url': fields.String(description='Google Maps URL for the route'),
    'created_at': fields.DateTime(description='Route creation timestamp')
})

# Health check model
health_model = api.model('HealthCheck', {
    'status': fields.String(required=True, description='Service health status', example='healthy'),
    'version': fields.String(required=True, description='API version', example='1.0.0'),
    'timestamp': fields.DateTime(required=True, description='Health check timestamp'),
    'uptime': fields.Float(description='Service uptime in seconds'),
    'database_status': fields.String(description='Database connection status'),
    'cache_status': fields.String(description='Cache system status')
})

# Analytics data model
analytics_model = api.model('Analytics', {
    'total_routes': fields.Integer(description='Total routes generated'),
    'total_distance': fields.Float(description='Total distance optimized'),
    'avg_optimization_time': fields.Float(description='Average optimization time'),
    'algorithm_usage': fields.Raw(description='Algorithm usage statistics'),
    'time_period': fields.String(description='Analytics time period')
})

# Define namespaces for different API sections
route_ns = Namespace('routes', description='Route optimization operations')
analytics_ns = Namespace('analytics', description='Analytics and monitoring operations')
health_ns = Namespace('health', description='Health check operations')
mobile_ns = Namespace('mobile', description='Mobile API operations')
traffic_ns = Namespace('traffic', description='Traffic-aware routing operations')

# Add namespaces to API
api.add_namespace(route_ns, path='/routes')
api.add_namespace(analytics_ns, path='/analytics')
api.add_namespace(health_ns, path='/health')
api.add_namespace(mobile_ns, path='/mobile')
api.add_namespace(traffic_ns, path='/traffic')

@health_ns.route('')
class HealthCheck(Resource):
    @health_ns.doc('health_check')
    @health_ns.marshal_with(health_model)
    def get(self):
        """Get API health status"""
        from datetime import datetime
        return {
            'status': 'healthy',
            'version': '1.0.0',
            'timestamp': datetime.utcnow(),
            'uptime': 12345.67,
            'database_status': 'connected',
            'cache_status': 'available'
        }

def get_api_documentation():
    """
    Get the API documentation instance
    Returns the configured Flask-RESTX Api instance
    """
    return api

def get_documentation_blueprint():
    """
    Get the documentation blueprint
    Returns the blueprint containing Swagger UI and API docs
    """
    return doc_bp