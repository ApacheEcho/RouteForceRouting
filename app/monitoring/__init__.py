"""
Sentry Integration for Flask Application
Initialize and configure Sentry monitoring in the main Flask app
"""

from app.monitoring.sentry_config import init_sentry, SentryHelper, monitor_performance, SentryContext
import logging

# Make Sentry utilities available at package level
__all__ = ['init_sentry', 'SentryHelper', 'monitor_performance', 'SentryContext']

# Configure module logger
logger = logging.getLogger(__name__)

def setup_monitoring(app):
    """Set up comprehensive monitoring for the Flask application"""
    try:
        # Initialize Sentry
        sentry_enabled = init_sentry(app)
        
        if sentry_enabled:
            logger.info("✅ Sentry monitoring enabled")
            
            # Add Sentry helper to app context
            app.sentry = SentryHelper()
            
            # Add monitoring utilities to app config
            app.config['MONITORING_ENABLED'] = True
            
            # Set up custom error handlers with Sentry integration
            setup_error_handlers(app)
            
        else:
            logger.warning("⚠️ Sentry monitoring disabled - check configuration")
            app.config['MONITORING_ENABLED'] = False
            
    except Exception as e:
        logger.error(f"❌ Failed to setup monitoring: {e}")
        app.config['MONITORING_ENABLED'] = False


def setup_error_handlers(app):
    """Set up custom error handlers with Sentry integration"""
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Global exception handler with Sentry integration"""
        import traceback
        from flask import request, jsonify
        
        # Log the full traceback
        logger.error(f"Unhandled exception: {e}")
        logger.error(traceback.format_exc())
        
        # Capture with Sentry if available
        if app.config.get('MONITORING_ENABLED'):
            app.sentry.add_breadcrumb(
                message=f"Unhandled exception in {request.endpoint}",
                category="error",
                level="error",
                data={
                    "url": request.url,
                    "method": request.method,
                    "endpoint": request.endpoint
                }
            )
        
        # Return appropriate error response
        if request.is_json:
            return jsonify({
                "error": "Internal server error",
                "message": "An unexpected error occurred"
            }), 500
        else:
            return "Internal Server Error", 500
