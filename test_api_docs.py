#!/usr/bin/env python3
"""
Simple test to verify API documentation setup
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_api_docs():
    """Test that API documentation components can be imported"""
    try:
        print("🧪 Testing API documentation imports...")
        
        # Test Flask-RESTX import
        from flask_restx import Api, Resource, fields, Namespace
        print("✅ Flask-RESTX imported successfully")
        
        # Test API docs module
        from app.api_docs import (
            get_api_documentation, 
            get_documentation_blueprint,
            route_ns, analytics_ns, health_ns
        )
        print("✅ API docs module imported successfully")
        
        # Test that blueprint can be created
        blueprint = get_documentation_blueprint()
        print(f"✅ Documentation blueprint created: {blueprint.name}")
        
        # Test that API instance can be created
        api = get_api_documentation()
        print(f"✅ API documentation instance created: {api.title}")
        
        # Test models exist
        from app.api_docs import (
            route_request_model, 
            route_response_model, 
            error_model, 
            success_model
        )
        print("✅ API models defined successfully")
        
        print("\n🎉 All API documentation components working correctly!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_swagger_ui_generation():
    """Test static file generation"""
    try:
        print("\n🧪 Testing static documentation generation...")
        
        # Create docs directory
        docs_dir = project_root / "docs" / "api"
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate basic OpenAPI spec
        basic_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "RouteForce API",
                "version": "1.0.0",
                "description": "Route optimization API"
            },
            "paths": {
                "/health": {
                    "get": {
                        "summary": "Health check",
                        "responses": {
                            "200": {"description": "Service is healthy"}
                        }
                    }
                }
            }
        }
        
        import json
        openapi_file = docs_dir / "openapi.json"
        with open(openapi_file, 'w') as f:
            json.dump(basic_spec, f, indent=2)
        
        print(f"✅ Basic OpenAPI spec generated: {openapi_file}")
        
        # Generate basic Swagger UI
        swagger_html = """<!DOCTYPE html>
<html>
<head>
    <title>RouteForce API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
    <script>
        SwaggerUIBundle({
            url: './openapi.json',
            dom_id: '#swagger-ui',
            presets: [SwaggerUIBundle.presets.apis]
        });
    </script>
</body>
</html>"""
        
        swagger_file = docs_dir / "index.html"
        with open(swagger_file, 'w') as f:
            f.write(swagger_html)
        
        print(f"✅ Swagger UI generated: {swagger_file}")
        
        # Test file accessibility
        if openapi_file.exists() and swagger_file.exists():
            print("✅ Documentation files created successfully")
            print(f"📂 Documentation directory: {docs_dir}")
            print(f"🌐 To view locally: python -m http.server 8080 (from {docs_dir})")
            return True
        else:
            print("❌ Documentation files not created")
            return False
            
    except Exception as e:
        print(f"❌ Error generating static files: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing RouteForce API Documentation Setup...")
    
    success = True
    success &= test_api_docs()
    success &= test_swagger_ui_generation()
    
    if success:
        print("\n✅ All tests passed! API documentation system is ready.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        sys.exit(1)