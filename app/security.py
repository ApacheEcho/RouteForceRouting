"""
Enterprise Security Middleware for RouteForce Routing
"""
from functools import wraps
from flask import request, jsonify, current_app, g
import hashlib
import hmac
import time
import logging
from typing import Optional, Dict, Any
import re
import bleach
from werkzeug.security import check_password_hash, generate_password_hash
import secrets

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """Comprehensive security middleware for enterprise applications"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Security headers
        @app.after_request
        def set_security_headers(response):
            # Prevent clickjacking
            response.headers['X-Frame-Options'] = 'DENY'
            
            # Prevent MIME sniffing
            response.headers['X-Content-Type-Options'] = 'nosniff'
            
            # XSS protection
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # HTTPS enforcement (in production)
            if not app.debug:
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            # Content Security Policy
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://fonts.gstatic.com; "
                "connect-src 'self'"
            )
            
            # Remove server header
            response.headers.pop('Server', None)
            
            return response
    
    def before_request(self):
        """Security checks before each request"""
        # Check for suspicious patterns
        if self._is_suspicious_request():
            logger.warning(f"Suspicious request from {request.remote_addr}: {request.url}")
            return jsonify({'error': 'Request blocked by security policy'}), 403
        
        # API key validation for protected endpoints
        if request.endpoint and request.endpoint.startswith('api.'):
            if not self._validate_api_access():
                return jsonify({'error': 'Invalid or missing API credentials'}), 401
        
        # Request size validation
        if request.content_length and request.content_length > current_app.config.get('MAX_CONTENT_LENGTH', 16*1024*1024):
            return jsonify({'error': 'Request too large'}), 413
    
    def after_request(self, response):
        """Security processing after each request"""
        # Log security events
        if response.status_code >= 400:
            logger.warning(f"Security event: {response.status_code} from {request.remote_addr}")
        
        return response
    
    def _is_suspicious_request(self) -> bool:
        """Check for suspicious request patterns"""
        # SQL injection patterns
        sql_patterns = [
            r"(\s*(union|select|insert|delete|update|drop|create|alter)\s+)",
            r"(\s*(or|and)\s+\d+\s*=\s*\d+)",
            r"(\s*;\s*(drop|delete)\s+)"
        ]
        
        # XSS patterns
        xss_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe.*?>"
        ]
        
        # Check query parameters and form data
        for param_dict in [request.args, request.form]:
            for value in param_dict.values():
                for pattern in sql_patterns + xss_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        return True
        
        # Check for path traversal
        if '../' in request.path or '..\\' in request.path:
            return True
        
        return False
    
    def _validate_api_access(self) -> bool:
        """Validate API access credentials"""
        # For development, allow all requests
        if current_app.debug:
            return True
        
        # Check for API key in headers
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return False
        
        # Validate API key (simplified - in production use proper key management)
        expected_key = current_app.config.get('API_KEY')
        if not expected_key:
            return True  # No API key configured
        
        return secrets.compare_digest(api_key, expected_key)

def require_auth(f):
    """Decorator for endpoints requiring authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check session or token
        auth_token = request.headers.get('Authorization')
        if not auth_token and not current_app.debug:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Validate token (simplified implementation)
        if auth_token and not _validate_token(auth_token):
            return jsonify({'error': 'Invalid authentication token'}), 401
        
        return f(*args, **kwargs)
    return decorated

def sanitize_input(data: Any) -> Any:
    """Sanitize user input to prevent XSS attacks"""
    if isinstance(data, str):
        # Remove potentially dangerous HTML/JS
        return bleach.clean(data, tags=[], strip=True)
    elif isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    else:
        return data

def validate_file_upload(file) -> tuple[bool, str]:
    """Validate uploaded files for security"""
    if not file:
        return False, "No file provided"
    
    # Check file size
    if hasattr(file, 'content_length') and file.content_length > 16*1024*1024:
        return False, "File too large"
    
    # Check file extension
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', set())
    if not file.filename or '.' not in file.filename:
        return False, "Invalid filename"
    
    extension = file.filename.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        return False, f"File type .{extension} not allowed"
    
    # Check for suspicious filenames
    suspicious_patterns = ['..', '/', '\\', '<', '>', '|', '*', '?', '"']
    if any(pattern in file.filename for pattern in suspicious_patterns):
        return False, "Suspicious filename detected"
    
    return True, "File is valid"

def _validate_token(token: str) -> bool:
    """Validate authentication token"""
    try:
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Simple validation - in production use JWT or similar
        secret_key = current_app.config.get('SECRET_KEY', '')
        expected_hash = hmac.new(
            secret_key.encode(),
            'valid_user'.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return secrets.compare_digest(token, expected_hash)
    except Exception:
        return False

def generate_csrf_token() -> str:
    """Generate CSRF token for forms"""
    import secrets
    token = secrets.token_hex(16)
    # Store in session (simplified)
    g.csrf_token = token
    return token

def validate_csrf_token(token: str) -> bool:
    """Validate CSRF token"""
    expected_token = getattr(g, 'csrf_token', None)
    return expected_token and secrets.compare_digest(token, expected_token)

# Rate limiting decorator
def rate_limit_advanced(requests_per_minute: int = 60):
    """Advanced rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Get client identifier
            client_id = request.remote_addr
            
            # Check rate limit (simplified - use Redis in production)
            current_time = time.time()
            window_start = current_time - 60  # 1 minute window
            
            # In production, store this in Redis
            if not hasattr(g, 'rate_limit_storage'):
                g.rate_limit_storage = {}
            
            client_requests = g.rate_limit_storage.get(client_id, [])
            # Remove old requests
            client_requests = [req_time for req_time in client_requests if req_time > window_start]
            
            if len(client_requests) >= requests_per_minute:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # Add current request
            client_requests.append(current_time)
            g.rate_limit_storage[client_id] = client_requests
            
            return f(*args, **kwargs)
        return decorated
    return decorator

# Mobile API Security Decorators
def require_api_key(f):
    """Require API key for mobile endpoints"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key required',
                'mobile_friendly': True
            }), 401
        
        # In production, validate against database
        # For now, accept any non-empty key
        if api_key == 'test-api-key' or len(api_key) > 10:
            return f(*args, **kwargs)
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid API key',
                'mobile_friendly': True
            }), 401
    
    return decorated

def validate_request(required_fields):
    """Validate required fields in request JSON"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Content-Type must be application/json',
                    'mobile_friendly': True
                }), 400
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'Invalid JSON data',
                    'mobile_friendly': True
                }), 400
            
            missing_fields = []
            for field in required_fields:
                if field not in data or data[field] is None:
                    missing_fields.append(field)
            
            if missing_fields:
                return jsonify({
                    'success': False,
                    'error': f'Missing required fields: {", ".join(missing_fields)}',
                    'mobile_friendly': True
                }), 400
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator

def mobile_rate_limit(requests_per_minute: int = 30):
    """Mobile-specific rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Get client identifier (device ID or IP)
            device_id = request.headers.get('X-Device-ID') or request.remote_addr
            
            # Simple rate limiting (use Redis in production)
            current_time = time.time()
            window_start = current_time - 60
            
            if not hasattr(g, 'mobile_rate_storage'):
                g.mobile_rate_storage = {}
            
            client_requests = g.mobile_rate_storage.get(device_id, [])
            client_requests = [req_time for req_time in client_requests if req_time > window_start]
            
            if len(client_requests) >= requests_per_minute:
                return jsonify({
                    'success': False,
                    'error': 'Rate limit exceeded',
                    'mobile_friendly': True,
                    'retry_after': '60 seconds'
                }), 429
            
            client_requests.append(current_time)
            g.mobile_rate_storage[device_id] = client_requests
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator
