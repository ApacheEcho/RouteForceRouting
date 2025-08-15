"""
API Documentation Routes
Provides convenient access to API documentation
"""

from flask import Blueprint, redirect, render_template_string

docs_bp = Blueprint("docs", __name__)


@docs_bp.route("/docs")
def api_docs():
    """
    Redirect to Swagger UI documentation
    """
    return redirect("/api/docs")


@docs_bp.route("/docs/info")
def docs_info():
    """
    API documentation information page
    """
    info_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RouteForce API Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
            .content { margin-top: 20px; }
            .link-box { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; }
            a { color: #3498db; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>RouteForce Routing API Documentation</h1>
            <p>Comprehensive route optimization platform for field execution teams</p>
        </div>
        
        <div class="content">
            <h2>Available Documentation</h2>
            
            <div class="link-box">
                <h3><a href="/api/docs">🔗 Interactive API Documentation (Swagger UI)</a></h3>
                <p>Browse and test all API endpoints with an interactive interface</p>
            </div>
            
            <div class="link-box">
                <h3><a href="/api/swagger.json">📄 OpenAPI Specification (JSON)</a></h3>
                <p>Raw OpenAPI/Swagger specification for integration with other tools</p>
            </div>
            
            <h2>API Categories</h2>
            <ul>
                <li><strong>Analytics</strong> - Analytics and monitoring endpoints</li>
                <li><strong>Mobile</strong> - Mobile app specific endpoints</li>
                <li><strong>Routes</strong> - Route optimization and management</li>
                <li><strong>Traffic</strong> - Traffic data and routing</li>
            </ul>
            
            <h2>Authentication</h2>
            <p>Most endpoints require API key authentication via the <code>X-API-Key</code> header.</p>
            
            <h2>Getting Started</h2>
            <ol>
                <li>Visit the <a href="/api/docs">Interactive API Documentation</a></li>
                <li>Explore the available endpoints by category</li>
                <li>Test endpoints directly in the browser</li>
                <li>Use the JSON specification for integration with your tools</li>
            </ol>
        </div>
    </body>
    </html>
    """
    return info_html
