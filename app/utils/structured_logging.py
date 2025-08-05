"""
Enhanced Structured Logging for RouteForce - AUTO-PILOT ENHANCEMENT
Provides comprehensive logging with context including user ID, request ID, and stack traces
"""

import logging
import json
import traceback
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from flask import request, g
import threading
from contextlib import contextmanager


class StructuredLogger:
    """Enhanced structured logger with context tracking"""

    def __init__(self, name: str = "routeforce"):
        self.logger = logging.getLogger(name)
        self.setup_handler()

    def setup_handler(self):
        """Setup structured logging handler"""
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredFormatter())
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def get_context(self) -> Dict[str, Any]:
        """Extract comprehensive request context"""
        context = {
            "timestamp": datetime.utcnow().isoformat(),
            "thread_id": threading.get_ident(),
            "process_id": os.getpid() if 'os' in globals() else None,
        }

        # Add Flask request context if available
        try:
            if request:
                context.update({
                    "request_id": getattr(g, 'request_id', str(uuid.uuid4())),
                    "user_id": getattr(g, 'user_id', 'anonymous'),
                    "ip_address": request.remote_addr,
                    "method": request.method,
                    "endpoint": request.endpoint,
                    "path": request.path,
                    "user_agent": request.headers.get('User-Agent', ''),
                    "referrer": request.headers.get('Referer', ''),
                })
        except RuntimeError:
            # Outside request context
            context.update({
                "request_id": str(uuid.uuid4()),
                "user_id": "system",
                "context": "background_task",
            })

        return context

    def log_with_context(self, level: str, message: str, extra: Dict[str, Any] = None,
                        include_stack: bool = False, exception: Exception = None):
        """Log message with full context"""
        context = self.get_context()
        
        if extra:
            context.update(extra)

        if include_stack or exception:
            if exception:
                context["exception"] = {
                    "type": type(exception).__name__,
                    "message": str(exception),
                    "traceback": traceback.format_exc(),
                }
            else:
                context["stack_trace"] = traceback.format_stack()

        log_entry = {
            "message": message,
            "level": level.upper(),
            "context": context,
        }

        getattr(self.logger, level.lower())(json.dumps(log_entry, indent=2))

    def info(self, message: str, **kwargs):
        """Log info message with context"""
        self.log_with_context("info", message, kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with context"""
        self.log_with_context("warning", message, kwargs)

    def error(self, message: str, exception: Exception = None, **kwargs):
        """Log error message with context and stack trace"""
        self.log_with_context("error", message, kwargs, 
                            include_stack=True, exception=exception)

    def debug(self, message: str, **kwargs):
        """Log debug message with context"""
        self.log_with_context("debug", message, kwargs)

    def critical(self, message: str, exception: Exception = None, **kwargs):
        """Log critical message with full context"""
        self.log_with_context("critical", message, kwargs, 
                            include_stack=True, exception=exception)


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logs"""

    def format(self, record):
        """Format log record as structured JSON"""
        try:
            # If the message is already JSON, parse and re-format
            if record.getMessage().startswith('{'):
                log_data = json.loads(record.getMessage())
                return json.dumps(log_data, indent=None, separators=(',', ':'))
            else:
                # Simple message, wrap in structured format
                return json.dumps({
                    "message": record.getMessage(),
                    "level": record.levelname,
                    "timestamp": datetime.utcnow().isoformat(),
                    "logger": record.name,
                })
        except Exception:
            # Fallback to standard formatting
            return super().format(record)


@contextmanager
def log_operation(operation_name: str, logger: StructuredLogger = None, **context):
    """Context manager for logging operation duration and outcome"""
    if logger is None:
        logger = get_structured_logger()
        
    start_time = datetime.utcnow()
    operation_id = str(uuid.uuid4())
    
    logger.info(f"Starting operation: {operation_name}", 
               operation_id=operation_id, operation_name=operation_name, **context)
    
    try:
        yield operation_id
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Completed operation: {operation_name}", 
                   operation_id=operation_id, duration_seconds=duration, 
                   status="success", **context)
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"Failed operation: {operation_name}", 
                    exception=e, operation_id=operation_id, 
                    duration_seconds=duration, status="failed", **context)
        raise


def setup_request_logging(app):
    """Setup request-level logging middleware"""
    
    @app.before_request
    def before_request():
        """Setup request context for logging"""
        g.request_id = str(uuid.uuid4())
        g.start_time = datetime.utcnow()
        
        # Log request start
        logger = get_structured_logger()
        logger.info("Request started", 
                   request_size=request.content_length,
                   query_params=dict(request.args))

    @app.after_request
    def after_request(response):
        """Log request completion"""
        if hasattr(g, 'start_time'):
            duration = (datetime.utcnow() - g.start_time).total_seconds()
            
            logger = get_structured_logger()
            logger.info("Request completed",
                       status_code=response.status_code,
                       duration_seconds=duration,
                       response_size=response.content_length)
        
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Log unhandled exceptions with full context"""
        logger = get_structured_logger()
        logger.error("Unhandled exception in request", exception=e,
                    request_data=request.get_data(as_text=True)[:1000])  # First 1KB
        
        # Re-raise the exception
        raise


# Global logger instance
_structured_logger = None


def get_structured_logger(name: str = "routeforce") -> StructuredLogger:
    """Get or create global structured logger instance"""
    global _structured_logger
    if _structured_logger is None:
        _structured_logger = StructuredLogger(name)
    return _structured_logger


# Performance monitoring decorator
def log_performance(operation_name: str = None):
    """Decorator to log function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            with log_operation(op_name, 
                             function_name=func.__name__,
                             module=func.__module__):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Import os for process ID
import os