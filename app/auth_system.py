"""
Authentication and Authorization System for RouteForce
JWT-based authentication with role-based access control
"""

from flask import Blueprint, request, jsonify, current_app, session
import os
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    verify_jwt_in_request,
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import json
from typing import Dict, List, Optional, Any
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Initialize JWT Manager
jwt = JWTManager()


def init_jwt(app):
    # JWT Blocklist integration
    from app.jwt_blocklist import is_token_revoked
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return is_token_revoked(jwt_header, jwt_payload)
    """Initialize JWT with app"""
    jwt.init_app(app)

    # Configure JWT settings
    app.config["JWT_SECRET_KEY"] = app.config.get(
        "JWT_SECRET_KEY", secrets.token_hex(32)
    )
    # Enforce JWT algorithm verification
    app.config["JWT_ALGORITHM"] = os.environ.get("JWT_ALGORITHM", "HS256")
    app.config["JWT_DECODE_ALGORITHMS"] = [os.environ.get("JWT_ALGORITHM", "HS256")]
    # Short-lived access token (15 minutes), refresh token (7 days)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Invalid token"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        # Align with tests expecting Flask-JWT-Extended default message key
        return jsonify({"msg": "Missing Authorization Header"}), 401


# Auth Blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# User roles and permissions
ROLES = {
    "admin": {"permissions": ["all"], "description": "Full system access"},
    "dispatcher": {
        "permissions": [
            "view_analytics",
            "manage_routes",
            "view_drivers",
            "send_notifications",
        ],
        "description": "Route management and analytics access",
    },
    "driver": {
        "permissions": [
            "view_own_routes",
            "update_location",
            "view_basic_analytics",
        ],
        "description": "Limited access to own routes and updates",
    },
    "viewer": {
        "permissions": ["view_analytics", "view_reports"],
        "description": "Read-only access to analytics and reports",
    },
}

# In-memory user store (replace with database in production)
users_db = {
    "admin@routeforce.com": {
        "id": "user_001",
        "email": "admin@routeforce.com",
        "name": "System Administrator",
        "password_hash": generate_password_hash("admin123"),
        "role": "admin",
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "is_active": True,
    },
    "dispatcher@routeforce.com": {
        "id": "user_002",
        "email": "dispatcher@routeforce.com",
        "name": "Route Dispatcher",
        "password_hash": generate_password_hash("dispatcher123"),
        "role": "dispatcher",
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "is_active": True,
    },
    "driver@routeforce.com": {
        "id": "user_003",
        "email": "driver@routeforce.com",
        "name": "Test Driver",
        "password_hash": generate_password_hash("driver123"),
        "role": "driver",
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "is_active": True,
    },
}


class AuthManager:
    """Authentication and authorization manager"""

    def __init__(self, app=None):
        self.jwt = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize JWT with Flask app"""
        app.config["JWT_SECRET_KEY"] = app.config.get(
            "JWT_SECRET_KEY", secrets.token_hex(32)
        )
        app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

        self.jwt = JWTManager(app)

        @self.jwt.user_identity_loader
        def user_identity_lookup(user):
            return user["id"]

        @self.jwt.user_lookup_loader
        def user_lookup_callback(_jwt_header, jwt_data):
            identity = jwt_data["sub"]
            return self.get_user_by_id(identity)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        return users_db.get(email)

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        for user in users_db.values():
            if user["id"] == user_id:
                return user
        return None

    def authenticate_user(
        self, email: str, password: str
    ) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        user = self.get_user_by_email(email)
        if (
            user
            and user["is_active"]
            and check_password_hash(user["password_hash"], password)
        ):
            # Update last login
            user["last_login"] = datetime.now().isoformat()
            return user
        return None

    def create_user(
        self, email: str, name: str, password: str, role: str = "viewer"
    ) -> Dict[str, Any]:
        """Create new user"""
        if email in users_db:
            raise ValueError("User already exists")

        if role not in ROLES:
            raise ValueError("Invalid role")

        user = {
            "id": f"user_{len(users_db) + 1:03d}",
            "email": email,
            "name": name,
            "password_hash": generate_password_hash(password),
            "role": role,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "is_active": True,
        }

        users_db[email] = user
        return user

    def has_permission(self, user: Dict[str, Any], permission: str) -> bool:
        """Check if user has specific permission"""
        if not user or not user.get("is_active"):
            return False

        user_role = user.get("role")
        if not user_role or user_role not in ROLES:
            return False

        permissions = ROLES[user_role]["permissions"]
        return "all" in permissions or permission in permissions


# Global auth manager instance
auth_manager = AuthManager()


def requires_permission(permission: str):
    """Decorator to require specific permission"""

    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()
            user = auth_manager.get_user_by_id(current_user)

            if not auth_manager.has_permission(user, permission):
                return jsonify({"error": "Insufficient permissions"}), 403

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def requires_role(role: str):
    """Decorator to require specific role"""

    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_identity = get_jwt_identity()
            # Identity may be an email or a user id; resolve accordingly
            if isinstance(current_identity, str) and "@" in current_identity:
                user = auth_manager.get_user_by_email(current_identity)
                # Fallback to DB lookup if not found in in-memory store
                if not user:
                    try:
                        from app.models.database import User as DbUser
                        db_user = DbUser.query.filter_by(email=current_identity).first()
                        if db_user:
                            user = {"id": db_user.id, "email": db_user.email, "role": db_user.role}
                    except Exception:
                        user = user or None
            else:
                user = auth_manager.get_user_by_id(current_identity)

            if not user or user.get("role") != role:
                return jsonify({"error": "Insufficient permissions"}), 403

            return f(*args, **kwargs)

        return decorated_function

    return decorator


@auth_bp.route("/login", methods=["POST"])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        user = auth_manager.authenticate_user(email, password)
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        # Create access token with user email as identity
        access_token = create_access_token(identity=user["email"])

        # Return user info and token
        return jsonify(
            {
                "success": True,
                "access_token": access_token,
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"],
                    "role": user["role"],
                    "permissions": ROLES[user["role"]]["permissions"],
                },
            }
        )

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Login failed"}), 500


@auth_bp.route("/register", methods=["POST"])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        email = data.get("email")
        name = data.get("name")
        password = data.get("password")
        role = data.get("role", "viewer")

        if not email or not name or not password:
            return (
                jsonify({"error": "Email, name, and password required"}),
                400,
            )

        # Create user
        user = auth_manager.create_user(email, name, password, role)

        return jsonify(
            {
                "success": True,
                "message": "User created successfully",
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"],
                    "role": user["role"],
                },
            }
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({"error": "Registration failed"}), 500


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_manager.get_user_by_id(current_user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify(
            {
                "success": True,
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"],
                    "role": user["role"],
                    "permissions": ROLES[user["role"]]["permissions"],
                    "created_at": user["created_at"],
                    "last_login": user["last_login"],
                },
            }
        )

    except Exception as e:
        logger.error(f"Profile error: {e}")
        return jsonify({"error": "Failed to get profile"}), 500


@auth_bp.route("/users", methods=["GET"])
@requires_permission("all")
def list_users():
    """List all users (admin only)"""
    try:
        users_list = []
        for user in users_db.values():
            users_list.append(
                {
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"],
                    "role": user["role"],
                    "is_active": user["is_active"],
                    "created_at": user["created_at"],
                    "last_login": user["last_login"],
                }
            )

        return jsonify(
            {"success": True, "users": users_list, "total": len(users_list)}
        )

    except Exception as e:
        logger.error(f"List users error: {e}")
        return jsonify({"error": "Failed to list users"}), 500


@auth_bp.route("/users/<user_id>/role", methods=["PUT"])
@requires_permission("all")
def update_user_role():
    """Update user role (admin only)"""
    try:
        user_id = request.view_args["user_id"]
        data = request.get_json()
        new_role = data.get("role")

        if new_role not in ROLES:
            return jsonify({"error": "Invalid role"}), 400

        user = auth_manager.get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Update role
        for stored_user in users_db.values():
            if stored_user["id"] == user_id:
                stored_user["role"] = new_role
                break

        return jsonify(
            {"success": True, "message": "User role updated successfully"}
        )

    except Exception as e:
        logger.error(f"Update role error: {e}")
        return jsonify({"error": "Failed to update role"}), 500


@auth_bp.route("/permissions", methods=["GET"])
@jwt_required()
def get_permissions():
    """Get available permissions and roles"""
    return jsonify({"success": True, "roles": ROLES})


@auth_bp.route("/validate", methods=["POST"])
@jwt_required()
def validate_token():
    """Validate JWT token"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_manager.get_user_by_id(current_user_id)

        if not user or not user["is_active"]:
            return (
                jsonify({"valid": False, "error": "Invalid or inactive user"}),
                401,
            )

        return jsonify(
            {
                "valid": True,
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"],
                    "role": user["role"],
                },
            }
        )

    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 401


# Login page route
@auth_bp.route("/login-page")
def login_page():
    """Serve login page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RouteForce Login</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    </head>
    <body class="bg-gray-100 min-h-screen flex items-center justify-center">
        <div class="max-w-md w-full bg-white rounded-lg shadow-md p-6">
            <h2 class="text-2xl font-bold text-center mb-6">RouteForce Login</h2>
            <form id="loginForm">
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2">Email</label>
                    <input type="email" id="email" class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500" required>
                </div>
                <div class="mb-6">
                    <label class="block text-gray-700 text-sm font-bold mb-2">Password</label>
                    <input type="password" id="password" class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500" required>
                </div>
                <button type="submit" class="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600">Login</button>
            </form>
            <div id="message" class="mt-4 text-center"></div>
            <div class="mt-6 text-sm text-gray-600">
                <p><strong>Demo Accounts:</strong></p>
                <p>Admin: admin@routeforce.com / admin123</p>
                <p>Dispatcher: dispatcher@routeforce.com / dispatcher123</p>
                <p>Driver: driver@routeforce.com / driver123</p>
            </div>
        </div>
        
        <script>
            document.getElementById('loginForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                const messageDiv = document.getElementById('message');
                
                try {
                    const response = await fetch('/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ email, password })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        localStorage.setItem('access_token', data.access_token);
                        localStorage.setItem('user', JSON.stringify(data.user));
                        messageDiv.innerHTML = '<p class="text-green-600">Login successful! Redirecting...</p>';
                        setTimeout(() => {
                            window.location.href = '/dashboard/analytics';
                        }, 1000);
                    } else {
                        messageDiv.innerHTML = '<p class="text-red-600">' + data.error + '</p>';
                    }
                } catch (error) {
                    messageDiv.innerHTML = '<p class="text-red-600">Login failed. Please try again.</p>';
                }
            });
        </script>
    </body>
    </html>
    """


def init_auth(app):
    """Initialize authentication system"""
    auth_manager.init_app(app)
    app.register_blueprint(auth_bp)
    init_jwt(app)
    return auth_manager
