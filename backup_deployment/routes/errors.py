"""
Error handling blueprint
"""

from flask import Blueprint, jsonify, request
import logging

logger = logging.getLogger(__name__)

errors_bp = Blueprint("errors", __name__)


@errors_bp.app_errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.url}")
    return (
        jsonify(
            {
                "error": "Resource not found",
                "message": "The requested resource was not found on this server",
            }
        ),
        404,
    )


@errors_bp.app_errorhandler(400)
def bad_request(error):
    """Handle 400 errors"""
    logger.warning(f"400 error: {request.url}")
    return (
        jsonify(
            {
                "error": "Bad request",
                "message": "The request could not be understood or was missing required parameters",
            }
        ),
        400,
    )


@errors_bp.app_errorhandler(413)
def file_too_large(error):
    """Handle file too large errors"""
    logger.warning(f"413 error: File too large from {request.remote_addr}")
    return (
        jsonify(
            {
                "error": "File too large",
                "message": "The uploaded file exceeds the maximum allowed size",
            }
        ),
        413,
    )


@errors_bp.app_errorhandler(429)
def ratelimit_handler(error):
    """Handle rate limit errors"""
    logger.warning(
        f"429 error: Rate limit exceeded from {request.remote_addr}"
    )
    return (
        jsonify(
            {
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
            }
        ),
        429,
    )


@errors_bp.app_errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error: {str(error)}")
    return (
        jsonify(
            {
                "error": "Internal server error",
                "message": "An unexpected error occurred. Please try again later.",
            }
        ),
        500,
    )
