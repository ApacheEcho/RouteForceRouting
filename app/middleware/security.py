"""
Security Middleware for RouteForce Routing
Enterprise-grade security with rate limiting, input validation, and XSS prevention
"""

import time
import json
import re
import hashlib
import ipaddress
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional, Any
from collections import defaultdict
import bleach
from flask import Flask, request, jsonify, current_app, g, abort
from werkzeug.exceptions import TooManyRequests, BadRequest, Forbidden
import redis


class SecurityConfig:
    """Security configuration constants"""
    
    # Rate limiting (requests per minute)
    DEFAULT_RATE_LIMIT = 100
    API_RATE_LIMIT = 200
    AUTH_RATE_LIMIT = 10
    
    # Input validation
    MAX_PAYLOAD_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_URL_LENGTH = 2048
    MAX_HEADER_LENGTH = 8192
    
    # XSS Protection
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
    ]
    ALLOWED_ATTRIBUTES = {
        '*': ['class', 'id'],
        'a': ['href', 'title']
    }
    
    # SQL Injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(or|and)\s+\d+\s*=\s*\d+)",
        r"(\bor\s+[\'\"]?\w+[\'\"]?\s*=\s*[\'\"]?\w+[\'\"]?)",
        r"(\bunion\s+select)",
        r"(\bselect\s+.*\bfrom\b)",
    ]


class RateLimiter:
    """Redis-based rate limiter with sliding window"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    def is_rate_limited(self, key: str, limit: int, window: int = 60) -> bool:
        """Check if request should be rate limited"""
        try:
            current_time = int(time.time())
            pipeline = self.redis.pipeline()
            
            # Remove old entries
            pipeline.zremrangebyscore(key, 0, current_time - window)
            
            # Count current requests
            pipeline.zcard(key)
            
            # Add current request
            pipeline.zadd(key, {str(current_time): current_time})
            
            # Set expiration
            pipeline.expire(key, window)
            
            results = pipeline.execute()
            request_count = results[1]
            
            return request_count >= limit
            
        except Exception as e:
            current_app.logger.error(f"Rate limiter error: {e}")
            return False  # Fail open for availability
    
    def get_rate_limit_info(self, key: str, window: int = 60) -> Dict[str, int]:
        """Get rate limit information for a key"""
        try:
            current_time = int(time.time())
            count = self.redis.zcount(key, current_time - window, current_time)
            return {
                'requests': count,
                'window': window,
                'reset_time': current_time + window
            }
        except Exception:
            return {'requests': 0, 'window': window, 'reset_time': 0}


class InputValidator:
    """Input validation and sanitization"""
    
    @staticmethod
    def validate_json_payload(data: Any, max_size: int = SecurityConfig.MAX_PAYLOAD_SIZE) -> bool:
        """Validate JSON payload size and structure"""
        try:
            if isinstance(data, str):
                if len(data.encode('utf-8')) > max_size:
                    return False
                json.loads(data)
            elif isinstance(data, dict):
                if len(json.dumps(data).encode('utf-8')) > max_size:
                    return False
            return True
        except (json.JSONDecodeError, TypeError):
            return False
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Sanitize HTML to prevent XSS"""
        if not isinstance(text, str):
            return str(text)
        
        return bleach.clean(
            text,
            tags=SecurityConfig.ALLOWED_TAGS,
            attributes=SecurityConfig.ALLOWED_ATTRIBUTES,
            strip=True
        )
    
    @staticmethod
    def detect_sql_injection(input_string: str) -> bool:
        """Detect potential SQL injection patterns"""
        if not isinstance(input_string, str):
            return False
        
        input_lower = input_string.lower()
        for pattern in SecurityConfig.SQL_INJECTION_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> bool:
        """Validate geographic coordinates"""
        try:
            lat_f = float(lat)
            lon_f = float(lon)
            return -90 <= lat_f <= 90 and -180 <= lon_f <= 180
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_route_id(route_id: str) -> bool:
        """Validate route ID format"""
        if not isinstance(route_id, str):
            return False
        
        # Allow alphanumeric, hyphens, underscores
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, route_id)) and len(route_id) <= 50


class SecurityMiddleware:
    """Main security middleware class"""
    
    def __init__(self, app: Flask, redis_client: redis.Redis):
        self.app = app
        self.rate_limiter = RateLimiter(redis_client)
        self.blocked_ips = set()
        self.failed_attempts = defaultdict(int)
        
        # Initialize middleware
        self._setup_middleware()
    
    def _setup_middleware(self):
        """Setup Flask middleware handlers"""
        
        @self.app.before_request
        def security_check():
            """Run security checks before each request"""
            
            # Check content length
            if request.content_length and request.content_length > SecurityConfig.MAX_PAYLOAD_SIZE:
                abort(413, description="Payload too large")
            
            # Check URL length
            if len(request.url) > SecurityConfig.MAX_URL_LENGTH:
                abort(414, description="URL too long")
            
            # Check for blocked IPs
            client_ip = self._get_client_ip()
            if client_ip in self.blocked_ips:
                abort(403, description="IP blocked")
            
            # Validate headers
            for header_name, header_value in request.headers:
                if len(header_value) > SecurityConfig.MAX_HEADER_LENGTH:
                    abort(400, description="Header too long")
            
            # Store client info in request context
            g.client_ip = client_ip
            g.user_agent = request.headers.get('User-Agent', '')
        
        @self.app.after_request
        def add_security_headers(response):
            """Add security headers to all responses"""
            
            # Prevent XSS
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # HTTPS enforcement
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            # Content Security Policy
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' wss: ws:;"
            )
            
            # Remove server information
            response.headers.pop('Server', None)
            
            return response
    
    def _get_client_ip(self) -> str:
        """Get client IP address handling proxies"""
        # Check for forwarded headers (proxy support)
        forwarded_ips = request.headers.get('X-Forwarded-For', '').split(',')
        if forwarded_ips and forwarded_ips[0].strip():
            return forwarded_ips[0].strip()
        
        return request.headers.get('X-Real-IP', request.remote_addr)
    
    def rate_limit(self, limit: int = SecurityConfig.DEFAULT_RATE_LIMIT, 
                   window: int = 60, key_func=None):
        """Rate limiting decorator"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Generate rate limit key
                if key_func:
                    key = key_func()
                else:
                    key = f"rate_limit:{g.client_ip}:{request.endpoint}"
                
                # Check rate limit
                if self.rate_limiter.is_rate_limited(key, limit, window):
                    # Get rate limit info for headers
                    info = self.rate_limiter.get_rate_limit_info(key, window)
                    
                    response = jsonify({
                        'error': 'Rate limit exceeded',
                        'limit': limit,
                        'window': window,
                        'reset_time': info['reset_time']
                    })
                    response.status_code = 429
                    response.headers['Retry-After'] = str(window)
                    response.headers['X-RateLimit-Limit'] = str(limit)
                    response.headers['X-RateLimit-Remaining'] = '0'
                    response.headers['X-RateLimit-Reset'] = str(info['reset_time'])
                    
                    return response
                
                # Add rate limit headers to successful responses
                info = self.rate_limiter.get_rate_limit_info(key, window)
                response = f(*args, **kwargs)
                
                if hasattr(response, 'headers'):
                    response.headers['X-RateLimit-Limit'] = str(limit)
                    response.headers['X-RateLimit-Remaining'] = str(max(0, limit - info['requests']))
                    response.headers['X-RateLimit-Reset'] = str(info['reset_time'])
                
                return response
            
            return decorated_function
        return decorator
    
    def validate_input(self, schemas: Dict[str, Any] = None):
        """Input validation decorator"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Validate JSON payload
                if request.is_json:
                    try:
                        data = request.get_json()
                        if not InputValidator.validate_json_payload(data):
                            abort(400, description="Invalid JSON payload")
                        
                        # Check for SQL injection in string values
                        def check_sql_injection(obj, path=""):
                            if isinstance(obj, str):
                                if InputValidator.detect_sql_injection(obj):
                                    current_app.logger.warning(
                                        f"SQL injection attempt detected from {g.client_ip}: {path}"
                                    )
                                    abort(400, description="Invalid input detected")
                            elif isinstance(obj, dict):
                                for key, value in obj.items():
                                    check_sql_injection(value, f"{path}.{key}")
                            elif isinstance(obj, list):
                                for i, item in enumerate(obj):
                                    check_sql_injection(item, f"{path}[{i}]")
                        
                        check_sql_injection(data)
                        
                    except Exception as e:
                        current_app.logger.error(f"Input validation error: {e}")
                        abort(400, description="Invalid request data")
                
                # Validate URL parameters
                for param, value in request.args.items():
                    if InputValidator.detect_sql_injection(value):
                        current_app.logger.warning(
                            f"SQL injection attempt in URL param from {g.client_ip}: {param}={value}"
                        )
                        abort(400, description="Invalid URL parameter")
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def require_api_key(self, f):
        """API key authentication decorator"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            
            if not api_key:
                abort(401, description="API key required")
            
            # Hash the API key for comparison
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            # Check against configured API keys (should be in environment)
            valid_keys = current_app.config.get('API_KEYS', set())
            
            if key_hash not in valid_keys:
                # Track failed attempts
                self.failed_attempts[g.client_ip] += 1
                
                # Block IP after too many failed attempts
                if self.failed_attempts[g.client_ip] > 5:
                    self.blocked_ips.add(g.client_ip)
                    current_app.logger.warning(f"Blocked IP {g.client_ip} for repeated invalid API key attempts")
                
                abort(401, description="Invalid API key")
            
            # Reset failed attempts on successful auth
            self.failed_attempts[g.client_ip] = 0
            
            return f(*args, **kwargs)
        
        return decorated_function


def create_security_middleware(app: Flask, redis_client: redis.Redis) -> SecurityMiddleware:
    """Factory function to create and configure security middleware"""
    
    # Configure security settings
    app.config.setdefault('MAX_CONTENT_LENGTH', SecurityConfig.MAX_PAYLOAD_SIZE)
    
    # Create middleware instance
    security = SecurityMiddleware(app, redis_client)
    
    # Add convenience decorators to app
    app.rate_limit = security.rate_limit
    app.validate_input = security.validate_input
    app.require_api_key = security.require_api_key
    
    current_app.logger.info("Security middleware initialized with enterprise-grade protection")
    
    return security


# Export commonly used decorators
__all__ = [
    'SecurityMiddleware',
    'RateLimiter', 
    'InputValidator',
    'SecurityConfig',
    'create_security_middleware'
]
