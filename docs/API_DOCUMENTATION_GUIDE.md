# API Documentation Guide for Contributors

This document explains how to maintain and use the automated API documentation system in the RouteForce Routing project.

## Overview

The RouteForce project uses **Flask-RESTX** to automatically generate comprehensive API documentation from code comments and decorators. This system provides:

- 📚 **Interactive Swagger UI** - Live API exploration and testing
- 🔄 **Automated Generation** - Documentation updates with code changes
- 🚀 **CI/CD Integration** - Automatic deployment to GitHub Pages
- 📝 **OpenAPI Specification** - Standard API description format

## For Contributors: Adding Documentation to APIs

### 1. Basic Route Documentation

When creating or updating API endpoints, use Flask-RESTX decorators to add documentation:

```python
from flask_restx import Resource, Namespace, fields
from app.api_docs import api, route_ns, route_request_model, route_response_model

@route_ns.route('/example')
class ExampleAPI(Resource):
    @route_ns.doc('create_example',
                 description='Create a new example resource',
                 responses={
                     201: 'Example created successfully',
                     400: 'Bad request - invalid input data',
                     401: 'Authentication required'
                 })
    @route_ns.expect(route_request_model)
    @route_ns.marshal_with(route_response_model, code=201)
    def post(self):
        """
        Create a new example resource
        
        This endpoint accepts example data and creates a new resource.
        Include detailed description of what the endpoint does,
        expected behavior, and any important notes.
        """
        # Your implementation here
        pass
```

### 2. Adding New Data Models

Define data models in `app/api_docs.py` for consistent documentation:

```python
# Add to app/api_docs.py
example_model = api.model('Example', {
    'id': fields.Integer(required=True, description='Unique identifier'),
    'name': fields.String(required=True, description='Example name', example='My Example'),
    'status': fields.String(description='Status', enum=['active', 'inactive'], example='active'),
    'created_at': fields.DateTime(description='Creation timestamp')
})
```

### 3. Documenting Request Parameters

Use the `@route_ns.doc()` decorator to document query parameters:

```python
@route_ns.doc('get_examples',
             description='Get list of examples with filtering',
             params={
                 'page': 'Page number (default: 1)',
                 'per_page': 'Items per page (default: 10, max: 100)',
                 'status': 'Filter by status (active, inactive)',
                 'search': 'Search in name field'
             })
```

### 4. Error Response Documentation

Always document possible error responses:

```python
@route_ns.doc('example_endpoint',
             responses={
                 200: 'Success',
                 400: 'Bad request - validation failed',
                 401: 'Authentication required',
                 403: 'Permission denied',
                 404: 'Resource not found',
                 429: 'Rate limit exceeded',
                 500: 'Internal server error'
             })
```

### 5. Authentication Documentation

For endpoints requiring authentication, specify the security requirements:

```python
@route_ns.doc(security=['Bearer Token'])  # or ['API Key']
def protected_endpoint(self):
    """Endpoint requiring authentication"""
    pass
```

## Development Workflow

### Local Development

1. **Start the application:**
   ```bash
   python app.py
   ```

2. **Access interactive documentation:**
   ```
   http://localhost:8000/api/docs/
   ```

3. **Test your changes:**
   - Make API calls directly from Swagger UI
   - Verify documentation accuracy
   - Check response models

### Manual Documentation Generation

Generate static documentation locally:

```bash
# Generate docs
python scripts/generate_docs.py

# Serve locally for testing
cd docs/api
python -m http.server 8080
# Visit http://localhost:8080
```

### CI/CD Integration

The documentation system is automatically triggered by:

#### Push Events
- **Branches:** `main`, `develop`
- **Paths:** Any changes to `app/**/*.py`, `scripts/generate_docs.py`, or `requirements.txt`

#### Pull Requests
- Automatically validates documentation
- Comments on PR with status update
- Creates downloadable documentation artifacts

#### Manual Trigger
- Use GitHub Actions "Generate API Documentation" workflow
- Can be triggered from the Actions tab

## File Structure

```
├── app/
│   ├── api_docs.py              # Main documentation configuration
│   ├── documented_api.py        # Example documented API routes
│   └── routes/                  # Existing API routes
├── docs/
│   └── api/                     # Generated documentation
│       ├── openapi.json         # OpenAPI specification
│       ├── index.html           # Swagger UI
│       └── README.md            # Documentation README
├── scripts/
│   └── generate_docs.py         # Documentation generator
└── .github/workflows/
    └── api-docs.yml             # CI/CD workflow
```

## Best Practices

### 1. Write Clear Descriptions
- Use descriptive summaries for endpoints
- Explain business logic and use cases
- Include examples for complex parameters

### 2. Keep Models Consistent
- Reuse existing models where possible
- Use consistent naming conventions
- Include validation examples

### 3. Document Edge Cases
- Specify rate limiting behavior
- Document pagination details
- Explain error scenarios

### 4. Update Documentation with Code
- Document new endpoints immediately
- Update existing docs when changing APIs
- Remove docs for deprecated endpoints

### 5. Test Documentation
- Verify examples work in Swagger UI
- Check that all parameters are documented
- Ensure response models match actual responses

## Troubleshooting

### Common Issues

1. **Documentation not generating:**
   ```bash
   # Check for import errors
   python -c "from app.api_docs import get_api_documentation; print('✅ Import successful')"
   ```

2. **Invalid OpenAPI spec:**
   ```bash
   # Validate generated spec
   pip install swagger-cli
   swagger-cli validate docs/api/openapi.json
   ```

3. **Missing models in Swagger UI:**
   - Ensure models are imported in `documented_api.py`
   - Check that `@marshal_with` decorators reference correct models

### Getting Help

1. Check the generated documentation at `/api/docs/`
2. Review example implementations in `app/documented_api.py`
3. Consult Flask-RESTX documentation: https://flask-restx.readthedocs.io/
4. Create an issue in the repository for persistent problems

## Examples

### Complete Endpoint Example

```python
from flask_restx import Resource, fields
from app.api_docs import api, route_ns

# Define request model
create_request = api.model('CreateRequest', {
    'name': fields.String(required=True, description='Resource name'),
    'description': fields.String(description='Optional description'),
    'tags': fields.List(fields.String, description='Resource tags')
})

# Define response model
create_response = api.model('CreateResponse', {
    'id': fields.Integer(description='Resource ID'),
    'name': fields.String(description='Resource name'),
    'status': fields.String(description='Resource status'),
    'created_at': fields.DateTime(description='Creation timestamp')
})

@route_ns.route('/resources')
class ResourceCollection(Resource):
    @route_ns.doc('create_resource',
                 description='Create a new resource with validation',
                 responses={
                     201: 'Resource created successfully',
                     400: 'Validation error',
                     409: 'Resource already exists'
                 })
    @route_ns.expect(create_request, validate=True)
    @route_ns.marshal_with(create_response, code=201)
    def post(self):
        """
        Create a new resource
        
        Creates a new resource with the provided data.
        Resource names must be unique within the system.
        """
        data = request.json
        # Implementation here
        return created_resource, 201
```

This comprehensive system ensures that API documentation stays up-to-date automatically and provides an excellent developer experience for both internal development and external API consumers.