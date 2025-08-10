"""
Authentication Decorators and Middleware for RouteForce
Provides role-based access control decorators for API endpoints
"""

import logging
from functools import wraps
from typing import List, Optional
from collections.abc import Callable

from flask import current_app, g, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.auth_system import ROLES, users_db

logger = logging.getLogger(__name__)


def auth_required(
    roles: list[str] | None = None, permissions: list[str] | None = None
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

                # Get user from database
                user = users_db.get(current_user_email)
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
                    user_role = user["role"]
                    user_permissions = ROLES.get(user_role, {}).get("permissions", [])

                    # Admin has all permissions
                    if "all" not in user_permissions:
                        missing_permissions = [
                            p for p in permissions if p not in user_permissions
                        ]
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

                user = users_db.get(current_user_email)
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
                user = users_db.get(current_user_email)
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


def get_current_user() -> dict | None:
    """Get current authenticated user from request context"""
    return getattr(g, "current_user", None)


def get_user_role() -> str | None:
    """Get current user's role"""
    user = get_current_user()
    return user.get("role") if user else None
