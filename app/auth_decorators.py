"""
Authentication Decorators and Middleware for RouteForce
Provides role-based access control decorators for API endpoints
"""

from functools import wraps
from flask import request, jsonify, current_app, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
import logging
from typing import List, Optional, Callable, Any

from app.auth_system import users_db, ROLES

logger = logging.getLogger(__name__)


def _resolve_user(identity: str):
    """Resolve a user identity which may be an email or an id.

    Tries local users_db by key, then searches by id or email in users_db values,
    then falls back to enterprise user manager if available.
    Returns user dict or None.
    """
    if not identity:
        return None

    # Direct lookup by email key
    user = users_db.get(identity)
    if user:
        return user

    # Search by id or email in stored users
    for u in users_db.values():
        if u.get("id") == identity or u.get("email") == identity:
            return u

    # Fallback to enterprise user manager
    try:
        from app.enterprise.users import user_manager

        enterprise_user = user_manager.get_user(identity)
        if enterprise_user:
            # adapt enterprise user shape to local users_db-like dict
            # and include permissions from the enterprise role manager when possible
            perms = []
            try:
                role_name = enterprise_user.get("role")
                role_obj = user_manager.role_manager.get_role(role_name)
                if role_obj:
                    perms = role_obj.permissions
            except Exception:
                perms = []

            return {
                "id": enterprise_user.get("id"),
                "email": enterprise_user.get("email"),
                "role": enterprise_user.get("role"),
                "is_active": enterprise_user.get("is_active", True),
                "permissions": perms,
            }
    except Exception:
        pass

    return None


def auth_required(
    roles: Optional[List[str]] = None, permissions: Optional[List[str]] = None
):
    """
    Decorator for requiring authentication and authorization

    Args:
        roles: List of allowed roles
        permissions: List of required permissions
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Verify JWT token
                verify_jwt_in_request()
                current_user_email = get_jwt_identity()

                if not current_user_email:
                    return (
                        jsonify(
                            {
                                "error": "Authentication required",
                                "message": "Valid JWT token required",
                            }
                        ),
                        401,
                    )

                # Get user from database (flexible resolver)
                user = _resolve_user(current_user_email)
                if not user:
                    return (
                        jsonify(
                            {
                                "error": "User not found",
                                "message": "User account not found",
                            }
                        ),
                        401,
                    )

                # Store user in request context
                g.current_user = user

                # Check role-based access
                if roles and user["role"] not in roles:
                    return (
                        jsonify(
                            {
                                "error": "Insufficient permissions",
                                "message": f'Role {user["role"]} not authorized for this endpoint',
                                "required_roles": roles,
                            }
                        ),
                        403,
                    )

                # Check permission-based access
                if permissions:
                    # Resolve permissions list (may come from enterprise user resolver)
                    user_permissions = user.get("permissions")
                    if user_permissions is None:
                        user_role = user.get("role")
                        user_permissions = ROLES.get(user_role, {}).get("permissions", [])

                    # helper: check permission with wildcard support
                    def _perm_matches(user_perms: List[str], perm: str) -> bool:
                        if not user_perms:
                            return False
                        if "all" in user_perms:
                            return True

                        for up in user_perms:
                            # exact match
                            if up == perm:
                                return True

                            # wildcard namespace like 'analytics.*' should match 'analytics.view'
                            if up.endswith(".*"):
                                ns = up[:-2]
                                # direct namespace match e.g., 'analytics.view'
                                if perm.startswith(ns + "."):
                                    return True
                                # support 'verb_resource' style like 'view_analytics'
                                if "_" in perm:
                                    verb, resource = perm.split("_", 1)
                                    if resource == ns:
                                        return True

                            # system wildcard
                            if up == "system.*":
                                return True

                        return False

                    missing_permissions = [p for p in permissions if not _perm_matches(user_permissions, p)]
                    if missing_permissions:
                        return (
                            jsonify(
                                {
                                    "error": "Insufficient permissions",
                                    "message": f"Missing required permissions: {missing_permissions}",
                                    "user_permissions": user_permissions,
                                    "required_permissions": permissions,
                                }
                            ),
                            403,
                        )

                # Log access
                logger.info(
                    f"Authenticated access: {user['email']} ({user['role']}) to {request.endpoint}"
                )

                return f(*args, **kwargs)

            except Exception as e:
                logger.error(f"Authentication error: {str(e)}")
                return (
                    jsonify({"error": "Authentication failed", "message": str(e)}),
                    401,
                )

        return decorated_function

    return decorator


def require_auth(f: Callable) -> Callable:
    """Simple authentication requirement decorator (alias for auth_required)"""
    return auth_required()(f)


def admin_required(f: Callable) -> Callable:
    """Decorator for admin-only endpoints"""
    return auth_required(roles=["admin"])(f)


def dispatcher_required(f: Callable) -> Callable:
    """Decorator for dispatcher and admin access"""
    return auth_required(roles=["admin", "dispatcher"])(f)


def analytics_access_required(f: Callable) -> Callable:
    """Decorator for analytics access (admin, dispatcher, viewer)"""
    return auth_required(permissions=["view_analytics"])(f)


def route_management_required(f: Callable) -> Callable:
    """Decorator for route management access"""
    return auth_required(permissions=["manage_routes"])(f)


def driver_access_required(f: Callable) -> Callable:
    """Decorator for driver-specific access"""

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Verify JWT token
                verify_jwt_in_request()
                current_user_email = get_jwt_identity()

                user = _resolve_user(current_user_email)
                if not user:
                    return jsonify({"error": "User not found"}), 401

                g.current_user = user

                # Check if user is driver or has higher permissions
                if user["role"] == "driver":
                    # Driver can only access their own data
                    driver_id = request.view_args.get("driver_id") or request.args.get(
                        "driver_id"
                    )
                    if driver_id and driver_id != user["id"]:
                        return (
                            jsonify(
                                {
                                    "error": "Access denied",
                                    "message": "Drivers can only access their own data",
                                }
                            ),
                            403,
                        )
                elif user["role"] not in ["admin", "dispatcher"]:
                    return jsonify({"error": "Insufficient permissions"}), 403

                return f(*args, **kwargs)

            except Exception as e:
                logger.error(f"Driver access authentication error: {str(e)}")
                return (
                    jsonify({"error": "Authentication failed", "message": str(e)}),
                    401,
                )

        return decorated_function

    return decorator


def optional_auth(f: Callable) -> Callable:
    """
    Decorator for optional authentication
    Provides user context if authenticated, but doesn't require it
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
            current_user_email = get_jwt_identity()

            if current_user_email:
                user = _resolve_user(current_user_email)
                g.current_user = user
            else:
                g.current_user = None

            return f(*args, **kwargs)

        except Exception as e:
            # Optional auth should not fail the request
            g.current_user = None
            return f(*args, **kwargs)

    return decorated_function


def validate_api_key(f: Callable) -> Callable:
    """
    Decorator for API key validation (for external integrations)
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key") or request.args.get("api_key")

        if not api_key:
            return (
                jsonify(
                    {
                        "error": "API key required",
                        "message": "X-API-Key header or api_key parameter required",
                    }
                ),
                401,
            )

        # Check API key (implement your API key validation logic)
        valid_api_keys = current_app.config.get("VALID_API_KEYS", [])
        if api_key not in valid_api_keys:
            return jsonify({"error": "Invalid API key"}), 401

        return f(*args, **kwargs)

    return decorated_function


def rate_limit_by_user(f: Callable) -> Callable:
    """
    Decorator for user-specific rate limiting
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_email = get_jwt_identity()

            # Apply user-specific rate limiting logic here
            # This is a placeholder - implement actual rate limiting

            return f(*args, **kwargs)

        except Exception as e:
            return jsonify({"error": "Rate limit check failed", "message": str(e)}), 429

    return decorated_function


def audit_log(action: str, resource: str = None):
    """
    Decorator for audit logging

    Args:
        action: Action being performed
        resource: Resource being accessed
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get user info if available
                user_email = "anonymous"
                try:
                    verify_jwt_in_request(optional=True)
                    user_email = get_jwt_identity() or "anonymous"
                except:
                    pass

                # Log the action
                logger.info(
                    f"AUDIT: User {user_email} performed {action} on {resource or 'unknown'}"
                )

                # Execute the function
                result = f(*args, **kwargs)

                # Log successful completion
                logger.info(
                    f"AUDIT: Action {action} completed successfully for user {user_email}"
                )

                return result

            except Exception as e:
                # Log failed action
                logger.error(
                    f"AUDIT: Action {action} failed for user {user_email}: {str(e)}"
                )
                raise

        return decorated_function

    return decorator


# Utility functions for permission checking
def has_permission(user: dict, permission: str) -> bool:
    """Check if user has specific permission"""
    user_role = user.get("role")
    user_permissions = ROLES.get(user_role, {}).get("permissions", [])
    return "all" in user_permissions or permission in user_permissions


def get_current_user() -> Optional[dict]:
    """Get current authenticated user from request context"""
    return getattr(g, "current_user", None)


def get_user_role() -> Optional[str]:
    """Get current user's role"""
    user = get_current_user()
    return user.get("role") if user else None
