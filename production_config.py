"""
Production Configuration for Render Deployment
Optimized settings for production environment
"""

import os
from datetime import timedelta

class ProductionConfig:
    """Production configuration with security and performance optimizations"""
    
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'prod-secret-key-change-this'
    DEBUG = False
    TESTING = False
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://routeforce:password@localhost/routeforce_prod'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'max_overflow': 0
    }
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Session Configuration
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'routeforce:'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    CORS_ALLOW_CREDENTIALS = True
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = '/tmp/uploads'
    
    # API Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/1'
    RATELIMIT_DEFAULT = "1000 per hour"
    
    # Feature Flags
    FEATURES = {
        'AUTO_COMMIT_ENABLED': False,  # Disable auto-commit in production
        'DEBUG_TOOLBAR': False,
        'PROFILER': False,
        'ANALYTICS_ENABLED': True,
        'CACHING_ENABLED': True,
        'ML_PREDICTIONS_ENABLED': True,
        'WEBSOCKETS_ENABLED': True,
        'API_DOCS_ENABLED': True
    }
    
    # Logging Configuration
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
    
    # Performance Settings
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year cache for static files
    
    # External Services
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY')
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    
    # Machine Learning Settings
    ML_MODEL_CACHE_TTL = 3600  # 1 hour
    ML_PREDICTION_TIMEOUT = 30  # 30 seconds
    
    # Routing Algorithm Settings
    GENETIC_ALGORITHM_POPULATION_SIZE = 100
    GENETIC_ALGORITHM_GENERATIONS = 50
    SIMULATED_ANNEALING_ITERATIONS = 1000
    
    @staticmethod
    def init_app(app):
        """Initialize application with production settings"""
        # Disable auto-commit service in production
        app.config.update({
            'AUTO_COMMIT_ENABLED': False,
            'GIT_AUTO_BACKUP': False
        })
        
        # Set up error reporting
        if app.config.get('SENTRY_DSN'):
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            
            sentry_sdk.init(
                dsn=app.config['SENTRY_DSN'],
                integrations=[
                    FlaskIntegration(),
                    SqlalchemyIntegration()
                ],
                traces_sample_rate=0.1
            )
        
        # Configure logging for production
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            file_handler = RotatingFileHandler(
                'logs/routeforce.log', 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('RouteForce startup - Production Mode')

# Export the configuration
config = ProductionConfig
