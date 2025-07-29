"""
JWT-based authentication and authorization for RouteForce
"""

import json
import logging
import secrets
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional

from flask import Blueprint, current_app, jsonify, request, session
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    verify_jwt_in_request,
)
from werkzeug.security import check_password_hash, generate_password_hash

logger = logging.getLogger(__name__)

# Initialize JWT Manager
jwt = JWTManager()


def init_jwt(app):
    """Initialize JWT with app"""
    jwt.init_app(app)

    # Configure JWT settings
    app.config["JWT_SECRET_KEY"] = app.config.get(
        "JWT_SECRET_KEY", secrets.token_hex(32)
    )
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"msg": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"msg": "Invalid token"}), 422

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"msg": "Missing token"}), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"msg": "Token has been revoked"}), 401


# ...rest of the code from app/auth_system.py...
