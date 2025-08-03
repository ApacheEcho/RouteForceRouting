
import os
print("Loaded DATABASE_URI:", os.getenv('DATABASE_URI'))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    # Sentry DSN for error tracking
    SENTRY_DSN = os.getenv('SENTRY_DSN')            
    # Additional configuration settings can be added here
    # For example, you can add settings for logging, caching, etc.
    # Example:
    # LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')            
    # CACHING_TYPE = os.getenv('CACHING_TYPE', 'simple')    
    # You can also define methods to load environment variables or perform other setup tasks
    @staticmethod
    def init_app(app):
        pass                            
# T