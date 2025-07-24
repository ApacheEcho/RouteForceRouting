"""
Advanced User Management with Role-Based Access Control
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import logging
import re

# Initialize blueprint
users_bp = Blueprint("users", __name__, url_prefix="/api/users")
logger = logging.getLogger(__name__)


@dataclass
class Permission:
    """Permission model"""

    name: str
    description: str
    category: str


@dataclass
class Role:
    """Role model with permissions"""

    name: str
    description: str
    permissions: List[str]
    is_system_role: bool = False


class RoleManager:
    """Role-based access control manager"""

    def __init__(self):
        self.roles = {}
        self.permissions = {}
        self._init_permissions()
        self._init_roles()

    def _init_permissions(self):
        """Initialize system permissions"""
        permissions = [
            # Route Management
            Permission("routes.view", "View routes", "routes"),
            Permission("routes.create", "Create routes", "routes"),
            Permission("routes.edit", "Edit routes", "routes"),
            Permission("routes.delete", "Delete routes", "routes"),
            Permission("routes.optimize", "Optimize routes", "routes"),
            Permission("routes.export", "Export route data", "routes"),
            # Analytics
            Permission("analytics.view", "View analytics", "analytics"),
            Permission("analytics.advanced", "Access advanced analytics", "analytics"),
            Permission("analytics.export", "Export analytics data", "analytics"),
            Permission("analytics.ml", "Access ML features", "analytics"),
            # User Management
            Permission("users.view", "View users", "users"),
            Permission("users.create", "Create users", "users"),
            Permission("users.edit", "Edit users", "users"),
            Permission("users.delete", "Delete users", "users"),
            Permission("users.manage_roles", "Manage user roles", "users"),
            # Organization Management
            Permission("org.view", "View organization", "organization"),
            Permission("org.edit", "Edit organization", "organization"),
            Permission("org.settings", "Manage organization settings", "organization"),
            Permission("org.billing", "Manage billing", "organization"),
            # System Administration
            Permission("system.monitor", "Monitor system", "system"),
            Permission("system.logs", "View system logs", "system"),
            Permission("system.maintenance", "Perform maintenance", "system"),
            Permission("system.admin", "Full system administration", "system"),
        ]

        for perm in permissions:
            self.permissions[perm.name] = perm

    def _init_roles(self):
        """Initialize default roles"""
        roles = [
            Role(
                name="viewer",
                description="Read-only access to routes and basic analytics",
                permissions=["routes.view", "analytics.view"],
                is_system_role=True,
            ),
            Role(
                name="user",
                description="Standard user with route management and basic analytics",
                permissions=[
                    "routes.view",
                    "routes.create",
                    "routes.edit",
                    "routes.optimize",
                    "analytics.view",
                ],
                is_system_role=True,
            ),
            Role(
                name="power_user",
                description="Advanced user with export and advanced analytics",
                permissions=[
                    "routes.view",
                    "routes.create",
                    "routes.edit",
                    "routes.optimize",
                    "routes.export",
                    "analytics.view",
                    "analytics.advanced",
                    "analytics.export",
                ],
                is_system_role=True,
            ),
            Role(
                name="admin",
                description="Organization administrator",
                permissions=[
                    "routes.*",
                    "analytics.*",
                    "users.view",
                    "users.create",
                    "users.edit",
                    "org.view",
                    "org.edit",
                    "org.settings",
                ],
                is_system_role=True,
            ),
            Role(
                name="org_admin",
                description="Full organization management",
                permissions=["routes.*", "analytics.*", "users.*", "org.*"],
                is_system_role=True,
            ),
            Role(
                name="super_admin",
                description="System-wide administration",
                permissions=["system.*"],
                is_system_role=True,
            ),
        ]

        for role in roles:
            self.roles[role.name] = role

    def get_role(self, role_name: str) -> Optional[Role]:
        """Get role by name"""
        return self.roles.get(role_name)

    def has_permission(self, user_role: str, permission: str) -> bool:
        """Check if role has specific permission"""
        role = self.get_role(user_role)
        if not role:
            return False

        # Check for wildcard permissions
        for perm in role.permissions:
            if perm == permission:
                return True
            if perm.endswith(".*") and permission.startswith(perm[:-1]):
                return True
            if perm == "system.*":  # Super admin
                return True

        return False


class UserManager:
    """Advanced user management system"""

    def __init__(self):
        self.users = {}
        self.sessions = {}
        self.role_manager = RoleManager()
        self._init_demo_users()

    def _init_demo_users(self):
        """Initialize demo users"""
        from app.enterprise.organizations import org_manager

        # Get demo organization
        demo_org = None
        for org in org_manager.list_organizations():
            if org.subdomain == "demo":
                demo_org = org
                break

        if demo_org:
            demo_users = [
                {
                    "email": "admin@demo.routeforce.com",
                    "username": "demo_admin",
                    "first_name": "Demo",
                    "last_name": "Administrator",
                    "role": "org_admin",
                    "organization_id": demo_org.id,
                },
                {
                    "email": "user@demo.routeforce.com",
                    "username": "demo_user",
                    "first_name": "Demo",
                    "last_name": "User",
                    "role": "user",
                    "organization_id": demo_org.id,
                },
                {
                    "email": "analyst@demo.routeforce.com",
                    "username": "demo_analyst",
                    "first_name": "Demo",
                    "last_name": "Analyst",
                    "role": "power_user",
                    "organization_id": demo_org.id,
                },
            ]

            for user_data in demo_users:
                self.create_user(user_data, password="demo123")

    def create_user(self, data: Dict, password: str) -> Dict:
        """Create new user"""
        user_id = str(uuid.uuid4())

        # Validate email format
        if not re.match(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", data["email"]
        ):
            raise ValueError("Invalid email format")

        # Check if email or username exists
        for user in self.users.values():
            if user["email"] == data["email"]:
                raise ValueError("Email already exists")
            if user["username"] == data["username"]:
                raise ValueError("Username already exists")

        user = {
            "id": user_id,
            "organization_id": data["organization_id"],
            "email": data["email"],
            "username": data["username"],
            "password_hash": generate_password_hash(password),
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "role": data.get("role", "user"),
            "is_active": data.get("is_active", True),
            "last_login": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "profile": {
                "phone": data.get("phone"),
                "department": data.get("department"),
                "preferences": {
                    "theme": "light",
                    "notifications": True,
                    "language": "en",
                },
            },
        }

        self.users[user_id] = user
        logger.info(f"Created user: {user['email']} ({user['role']})")
        return user

    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user login"""
        for user in self.users.values():
            if user["email"] == email and user["is_active"]:
                if check_password_hash(user["password_hash"], password):
                    user["last_login"] = datetime.utcnow().isoformat()
                    logger.info(f"User authenticated: {email}")
                    return user
        return None

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        user = self.users.get(user_id)
        if user:
            # Remove password hash from response
            user_copy = user.copy()
            user_copy.pop("password_hash", None)
            return user_copy
        return None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        for user in self.users.values():
            if user["email"] == email:
                user_copy = user.copy()
                user_copy.pop("password_hash", None)
                return user_copy
        return None

    def list_organization_users(self, org_id: str) -> List[Dict]:
        """List users in organization"""
        org_users = []
        for user in self.users.values():
            if user["organization_id"] == org_id:
                user_copy = user.copy()
                user_copy.pop("password_hash", None)
                org_users.append(user_copy)
        return org_users

    def update_user(self, user_id: str, data: Dict) -> Optional[Dict]:
        """Update user"""
        user = self.users.get(user_id)
        if not user:
            return None

        # Update allowed fields
        allowed_fields = ["first_name", "last_name", "role", "is_active", "profile"]
        for field in allowed_fields:
            if field in data:
                if field == "profile" and isinstance(data[field], dict):
                    user["profile"].update(data[field])
                else:
                    user[field] = data[field]

        user["updated_at"] = datetime.utcnow().isoformat()
        logger.info(f"Updated user: {user['email']}")
        return self.get_user(user_id)

    def change_password(
        self, user_id: str, current_password: str, new_password: str
    ) -> bool:
        """Change user password"""
        user = self.users.get(user_id)
        if not user:
            return False

        if not check_password_hash(user["password_hash"], current_password):
            return False

        user["password_hash"] = generate_password_hash(new_password)
        user["updated_at"] = datetime.utcnow().isoformat()
        logger.info(f"Password changed for user: {user['email']}")
        return True

    def has_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission"""
        user = self.users.get(user_id)
        if not user or not user["is_active"]:
            return False

        return self.role_manager.has_permission(user["role"], permission)


# Initialize global user manager
user_manager = UserManager()


@users_bp.route("/login", methods=["POST"])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        user = user_manager.authenticate_user(email, password)
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        # Create JWT token
        access_token = create_access_token(
            identity=user["id"], expires_delta=timedelta(hours=24)
        )

        return (
            jsonify(
                {
                    "access_token": access_token,
                    "user": user_manager.get_user(user["id"]),
                    "expires_in": 24 * 3600,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "Login failed"}), 500


@users_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user = user_manager.get_user(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"user": user}), 200

    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({"error": "Failed to get profile"}), 500


@users_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update current user profile"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        user = user_manager.update_user(user_id, data)
        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"user": user, "message": "Profile updated successfully"}), 200

    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        return jsonify({"error": "Failed to update profile"}), 500


@users_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        current_password = data.get("current_password")
        new_password = data.get("new_password")

        if not current_password or not new_password:
            return jsonify({"error": "Current and new password required"}), 400

        if len(new_password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        success = user_manager.change_password(user_id, current_password, new_password)
        if not success:
            return jsonify({"error": "Invalid current password"}), 400

        return jsonify({"message": "Password changed successfully"}), 200

    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        return jsonify({"error": "Failed to change password"}), 500


@users_bp.route("/organization/<org_id>", methods=["GET"])
@jwt_required()
def list_organization_users(org_id):
    """List users in organization (admin only)"""
    try:
        user_id = get_jwt_identity()

        # Check permissions
        if not user_manager.has_permission(user_id, "users.view"):
            return jsonify({"error": "Insufficient permissions"}), 403

        users = user_manager.list_organization_users(org_id)
        return jsonify({"users": users, "total": len(users)}), 200

    except Exception as e:
        logger.error(f"List users error: {str(e)}")
        return jsonify({"error": "Failed to list users"}), 500


@users_bp.route("/", methods=["POST"])
@jwt_required()
def create_user():
    """Create new user (admin only)"""
    try:
        user_id = get_jwt_identity()

        # Check permissions
        if not user_manager.has_permission(user_id, "users.create"):
            return jsonify({"error": "Insufficient permissions"}), 403

        data = request.get_json()
        password = data.pop("password", "temp123")

        user = user_manager.create_user(data, password)
        return (
            jsonify(
                {
                    "user": user_manager.get_user(user["id"]),
                    "message": "User created successfully",
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Create user error: {str(e)}")
        return jsonify({"error": "Failed to create user"}), 500


@users_bp.route("/permissions/check", methods=["POST"])
@jwt_required()
def check_permissions():
    """Check user permissions"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        permissions = data.get("permissions", [])

        results = {}
        for permission in permissions:
            results[permission] = user_manager.has_permission(user_id, permission)

        return jsonify({"permissions": results}), 200

    except Exception as e:
        logger.error(f"Check permissions error: {str(e)}")
        return jsonify({"error": "Failed to check permissions"}), 500
