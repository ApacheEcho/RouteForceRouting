"""
RouteForce Routing Application Factory
"""
from flask import Flask
from flask_cors import CORS
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
import logging
import os
import warnings
from typing import Optional

# Initialize extensions
cache = Cache()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
socketio = SocketIO(cors_allowed_origins="*", logger=True, engineio_logger=True)

def create_app(config_name: str = 'development') -> Flask:
    """
    Application factory pattern for creating Flask app instances
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    from app.config import config
    app.config.from_object(config[config_name])
    
    # Initialize database
    from app.models.database import db, migrate
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize extensions
    CORS(app)
    cache.init_app(app)
    
    # Initialize security middleware
    from app.security import SecurityMiddleware
    SecurityMiddleware(app)
    
    # Initialize WebSocket support
    socketio.init_app(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
    
    # Initialize WebSocket handlers
    from app.websocket_handlers import init_websocket
    init_websocket(app, socketio)
    
    # Configure limiter with storage URI
    if app.config.get('RATELIMIT_STORAGE_URI'):
        limiter.storage_uri = app.config['RATELIMIT_STORAGE_URI']
    limiter.init_app(app)
    
    # Configure logging
    configure_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

def configure_logging(app: Flask) -> None:
    """Configure application logging"""
    # Suppress specific warnings for production readiness
    if not app.debug:
        warnings.filterwarnings('ignore', message='Flask-Caching.*deprecated')
        warnings.filterwarnings('ignore', message='Using the in-memory storage.*not recommended')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
    else:
        logging.basicConfig(level=logging.DEBUG)

def register_blueprints(app: Flask) -> None:
    """Register application blueprints"""
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    from app.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

def register_error_handlers(app: Flask) -> None:
    """Register application error handlers"""
    from app.routes.errors import errors_bp
    app.register_blueprint(errors_bp)
