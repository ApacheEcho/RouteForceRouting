"""
Response helper functions for consistent API responses
"""

from typing import Any, Dict, Optional
from flask import jsonify


def success_response(data: Any = None, message: str = "Success", status_code: int = 200):
    """
    Create a standardized success response
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code
    
    Returns:
        Flask response object
    """
    response_data = {
        "success": True,
        "message": message,
    }
    
    if data is not None:
        response_data["data"] = data
    
    return jsonify(response_data), status_code


def error_response(message: str = "An error occurred", status_code: int = 500, error_code: Optional[str] = None):
    """
    Create a standardized error response
    
    Args:
        message: Error message
        status_code: HTTP status code
        error_code: Optional error code for client handling
    
    Returns:
        Flask response object
    """
    response_data = {
        "success": False,
        "error": message,
    }
    
    if error_code:
        response_data["error_code"] = error_code
    
    return jsonify(response_data), status_code


def paginated_response(
    data: list, 
    total: int, 
    page: int = 1, 
    per_page: int = 10, 
    message: str = "Success"
):
    """
    Create a paginated response
    
    Args:
        data: List of items for current page
        total: Total number of items
        page: Current page number
        per_page: Items per page
        message: Success message
    
    Returns:
        Flask response object
    """
    total_pages = (total + per_page - 1) // per_page
    
    response_data = {
        "success": True,
        "message": message,
        "data": data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
    
    return jsonify(response_data), 200


def validation_error_response(errors: Dict[str, list]):
    """
    Create a validation error response
    
    Args:
        errors: Dictionary of field validation errors
    
    Returns:
        Flask response object
    """
    response_data = {
        "success": False,
        "error": "Validation failed",
        "validation_errors": errors
    }
    
    return jsonify(response_data), 400