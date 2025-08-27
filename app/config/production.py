import os
from datetime import timedelta

class ProductionConfig:
    """Production configuration with enterprise-grade settings"""
    
    # Redis Configuration for 1000+ jobs/day
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_POOL_SIZE = 50
    REDIS_MAX_CONNECTIONS = 100
    
    # Celery Configuration for Async Processing
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'UTC'
    CELERY_TASK_TRACK_STARTED = True
    CELERY_TASK_TIME_LIMIT = 300
    CELERY_TASK_SOFT_TIME_LIMIT = 240
    CELERY_TASK_ACKS_LATE = True
    CELERY_WORKER_PREFETCH_MULTIPLIER = 1
    CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 20
    SQLALCHEMY_MAX_OVERFLOW = 40
    SQLALCHEMY_POOL_RECYCLE = 3600
    SQLALCHEMY_POOL_PRE_PING = True
    
    # Database Sharding Configuration
    SQLALCHEMY_BINDS = {
        'routes_shard_1': os.getenv('DB_SHARD_1_URL'),
        'routes_shard_2': os.getenv('DB_SHARD_2_URL'),
        'routes_shard_3': os.getenv('DB_SHARD_3_URL'),
    }
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Session Configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SESSION_COOKIE_NAME = '__Host-session'
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
    
    # File Upload
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    UPLOAD_FOLDER = '/tmp/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'csv', 'xlsx'}
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "100/hour"
    
    # Monitoring
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    
    # ERP Integration
    ERP_SYNC_ENABLED = True
    ERP_SYNC_INTERVAL = 300  # 5 minutes
    
    # Telematics
    TELEMATICS_PROVIDER = os.getenv('TELEMATICS_PROVIDER', 'samsara')
    SAMSARA_API_TOKEN = os.getenv('SAMSARA_API_TOKEN')
    
    # ML/AI Features
    ML_MODELS_PATH = '/app/models'
    ENABLE_DEMAND_FORECASTING = True
    ENABLE_ML_OPTIMIZATION = True
