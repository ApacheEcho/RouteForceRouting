#!/usr/bin/env python3
"""
Standalone API Documentation Demo
Demonstrates the API documentation system without full app dependencies
"""

from flask import Flask
from flask_restx import Api, Resource, fields, Namespace
import json
from pathlib import Path

# Create a minimal Flask app for demonstration
app = Flask(__name__)

# Configure API documentation
api = Api(
    app,
    version='1.0.0',
    title='RouteForce Routing API',
    description='Enterprise-grade route optimization and field execution API',
    doc='/docs/',
    prefix='/api',
    contact_email='dev@routeforce.com',
    license='MIT'
)

# Define namespaces
route_ns = Namespace('routes', description='Route optimization operations')
health_ns = Namespace('health', description='Health check operations')

api.add_namespace(route_ns, path='/routes')
api.add_namespace(health_ns, path='/health')

# Define data models
store_model = api.model('Store', {
    'name': fields.String(required=True, description='Store name', example='Store A'),
    'address': fields.String(required=True, description='Store address', example='123 Main St, New York, NY 10001'),
    'latitude': fields.Float(description='Store latitude', example=40.7128),
    'longitude': fields.Float(description='Store longitude', example=-74.0060),
    'priority': fields.Integer(description='Store priority (1-10)', example=5)
})

route_request_model = api.model('RouteRequest', {
    'stores': fields.List(fields.Nested(store_model), required=True, description='List of stores to visit'),
    'algorithm': fields.String(description='Optimization algorithm', enum=['default', 'genetic', 'simulated_annealing'], example='genetic')
})

route_response_model = api.model('RouteResponse', {
    'route_id': fields.String(required=True, description='Unique route identifier'),
    'optimized_route': fields.List(fields.Nested(store_model), description='Optimized store sequence'),
    'total_distance': fields.Float(description='Total route distance in kilometers'),
    'total_duration': fields.Integer(description='Total route duration in minutes'),
    'google_maps_url': fields.String(description='Google Maps URL for the route')
})

health_model = api.model('HealthCheck', {
    'status': fields.String(required=True, description='Service health status', example='healthy'),
    'version': fields.String(required=True, description='API version', example='1.0.0'),
    'timestamp': fields.DateTime(required=True, description='Health check timestamp')
})

# Define API endpoints
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
            'timestamp': datetime.utcnow()
        }

@route_ns.route('')
class RouteCollection(Resource):
    @route_ns.doc('create_route',
                 description='Create a new optimized route for field execution teams',
                 responses={
                     201: 'Route created successfully',
                     400: 'Bad request - invalid input data',
                     500: 'Internal server error'
                 })
    @route_ns.expect(route_request_model, validate=True)
    @route_ns.marshal_with(route_response_model, code=201)
    def post(self):
        """
        Create a new route via API
        
        This endpoint accepts a list of stores and generates an optimized route
        using various algorithms including genetic algorithm and simulated annealing.
        """
        from datetime import datetime
        import uuid
        
        # Mock response for demonstration
        data = api.payload
        return {
            'route_id': str(uuid.uuid4()),
            'optimized_route': data.get('stores', []),
            'total_distance': 45.5,
            'total_duration': 120,
            'google_maps_url': 'https://maps.google.com/...'
        }, 201

    @route_ns.doc('get_routes',
                 description='Get route history with pagination',
                 params={
                     'page': 'Page number (default: 1)',
                     'per_page': 'Items per page (default: 10)'
                 })
    @route_ns.marshal_list_with(route_response_model)
    def get(self):
        """Get route history for current user with pagination"""
        # Mock response for demonstration
        return []

def create_manual_schema():
    """Create manual OpenAPI schema as fallback"""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "RouteForce Routing API",
            "version": "1.0.0",
            "description": "Enterprise-grade route optimization and field execution API",
            "contact": {"email": "dev@routeforce.com"},
            "license": {"name": "MIT"}
        },
        "servers": [{"url": "/api", "description": "API Server"}],
        "paths": {
            "/health": {
                "get": {
                    "tags": ["health"],
                    "summary": "Get API health status",
                    "description": "Returns the current health status of the API service",
                    "responses": {
                        "200": {
                            "description": "Service is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "healthy"},
                                            "version": {"type": "string", "example": "1.0.0"},
                                            "timestamp": {"type": "string", "format": "date-time"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/routes": {
                "post": {
                    "tags": ["routes"],
                    "summary": "Create a new optimized route",
                    "description": "Creates an optimized route for field execution teams using various algorithms",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["stores"],
                                    "properties": {
                                        "stores": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "name": {"type": "string", "example": "Store A"},
                                                    "address": {"type": "string", "example": "123 Main St, NY"},
                                                    "latitude": {"type": "number", "example": 40.7128},
                                                    "longitude": {"type": "number", "example": -74.0060}
                                                }
                                            }
                                        },
                                        "algorithm": {
                                            "type": "string",
                                            "enum": ["default", "genetic", "simulated_annealing"],
                                            "example": "genetic"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Route created successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "route_id": {"type": "string"},
                                            "optimized_route": {"type": "array"},
                                            "total_distance": {"type": "number"},
                                            "total_duration": {"type": "integer"},
                                            "google_maps_url": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "get": {
                    "tags": ["routes"],
                    "summary": "Get route history",
                    "description": "Returns paginated list of previously generated routes",
                    "parameters": [
                        {
                            "name": "page",
                            "in": "query",
                            "description": "Page number",
                            "schema": {"type": "integer", "default": 1}
                        },
                        {
                            "name": "per_page",
                            "in": "query",
                            "description": "Items per page",
                            "schema": {"type": "integer", "default": 10}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Routes retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"type": "object"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        }
    }

def generate_docs():
    """Generate OpenAPI documentation"""
    try:
        # Create docs directory
        docs_dir = Path(__file__).parent / "docs" / "api"
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure app for schema generation
        app.config['SERVER_NAME'] = 'localhost:5000'
        app.config['PREFERRED_URL_SCHEME'] = 'http'
        
        # Generate OpenAPI spec
        with app.app_context():
            try:
                openapi_spec = api.__schema__
            except Exception as e:
                print(f"⚠️  Schema generation issue: {e}")
                # Fallback to manual schema
                openapi_spec = create_manual_schema()
        
        # Save OpenAPI specification
        openapi_file = docs_dir / "openapi.json"
        with open(openapi_file, 'w') as f:
            json.dump(openapi_spec, f, indent=2, default=str)
        
        print(f"✅ OpenAPI specification generated: {openapi_file}")
        
        # Generate Swagger UI HTML
        swagger_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RouteForce API Documentation - Demo</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
    <style>
        .demo-banner {{
            background: #007acc;
            color: white;
            padding: 10px;
            text-align: center;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="demo-banner">
        🚀 RouteForce API Documentation Demo - Generated Automatically
    </div>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: './openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            }});
        }};
    </script>
</body>
</html>"""
        
        swagger_file = docs_dir / "index.html"
        with open(swagger_file, 'w') as f:
            f.write(swagger_html)
        
        print(f"✅ Swagger UI generated: {swagger_file}")
        print(f"🌐 To view: python -m http.server 8080 (from {docs_dir})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating documentation: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'generate':
        print("📚 Generating standalone API documentation...")
        success = generate_docs()
        sys.exit(0 if success else 1)
    else:
        print("🚀 Starting RouteForce API Documentation Demo...")
        print("📚 Interactive documentation available at: http://localhost:5000/docs/")
        print("🔧 To generate static docs: python demo_api_docs.py generate")
        app.run(debug=True, port=5000)