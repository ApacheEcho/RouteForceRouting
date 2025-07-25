"""
RouteForce Routing Application
Modern Flask application with enterprise-grade architecture and real-time features
"""

import os

# Import the app instance directly
from app import create_app

# Create application instance
app = create_app(os.getenv("FLASK_ENV", "production"))
