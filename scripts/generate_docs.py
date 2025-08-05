#!/usr/bin/env python3
"""
API Documentation Generator
Generates static API documentation from Flask-RESTX configuration
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def generate_api_docs():
    """Generate static API documentation"""
    try:
        # Import Flask app and API documentation
        from app import create_app
        from app.api_docs import get_api_documentation
        
        # Create app instance
        app = create_app('development')
        
        with app.app_context():
            # Get API documentation instance
            api = get_api_documentation()
            
            # Generate OpenAPI spec
            openapi_spec = api.__schema__
            
            # Create docs directory
            docs_dir = project_root / "docs" / "api"
            docs_dir.mkdir(parents=True, exist_ok=True)
            
            # Save OpenAPI specification
            openapi_file = docs_dir / "openapi.json"
            with open(openapi_file, 'w') as f:
                json.dump(openapi_spec, f, indent=2, default=str)
            
            print(f"✅ OpenAPI specification generated: {openapi_file}")
            
            # Generate Swagger UI HTML
            swagger_html = generate_swagger_ui_html()
            
            swagger_file = docs_dir / "index.html"
            with open(swagger_file, 'w') as f:
                f.write(swagger_html)
            
            print(f"✅ Swagger UI generated: {swagger_file}")
            
            # Generate README for documentation
            readme_content = generate_docs_readme()
            
            readme_file = docs_dir / "README.md"
            with open(readme_file, 'w') as f:
                f.write(readme_content)
            
            print(f"✅ Documentation README generated: {readme_file}")
            
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure to install dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error generating documentation: {e}")
        return False

def generate_swagger_ui_html():
    """Generate standalone Swagger UI HTML"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RouteForce API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
    <style>
        html {
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }
        *, *:before, *:after {
            box-sizing: inherit;
        }
        body {
            margin:0;
            background: #fafafa;
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
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
            });
        };
    </script>
</body>
</html>"""

def generate_docs_readme():
    """Generate README for API documentation"""
    return """# RouteForce API Documentation

This directory contains the automatically generated API documentation for the RouteForce Routing application.

## Files

- `openapi.json` - OpenAPI 3.0 specification in JSON format
- `index.html` - Interactive Swagger UI documentation
- `README.md` - This file

## Usage

### Local Development

To view the documentation locally:

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000/api/docs/
   ```

### Static Documentation

To view the static documentation:

1. Open `index.html` in a web browser
2. Or serve it using a simple HTTP server:
   ```bash
   python -m http.server 8080
   # Then visit http://localhost:8080
   ```

## API Endpoints

The RouteForce API provides the following main endpoints:

### Routes
- `POST /api/routes` - Create a new optimized route
- `GET /api/routes` - Get route history with pagination
- `GET /api/routes/{id}` - Get specific route by ID

### Analytics
- `GET /api/analytics/usage` - Get usage statistics and analytics

### Health
- `GET /api/health` - Health check endpoint

### Mobile
- Mobile-specific endpoints for field execution teams

### Traffic
- Traffic-aware routing endpoints

## Authentication

The API supports multiple authentication methods:
- **Bearer Token**: JWT-based authentication
- **API Key**: Header-based API key authentication

## Rate Limiting

Most endpoints are rate-limited to ensure fair usage:
- Standard endpoints: 100 requests per minute
- Analytics endpoints: 50 requests per minute

## Error Handling

The API uses standard HTTP status codes and provides detailed error messages:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Support

For API support and questions:
- Check the interactive documentation at `/api/docs/`
- Review the OpenAPI specification
- Contact the development team

---

*This documentation is automatically generated. Do not edit manually.*
"""

if __name__ == "__main__":
    print("🚀 Generating RouteForce API Documentation...")
    success = generate_api_docs()
    if success:
        print("✅ Documentation generation completed successfully!")
        sys.exit(0)
    else:
        print("❌ Documentation generation failed!")
        sys.exit(1)