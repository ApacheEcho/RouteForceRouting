"""
API validation utilities for RouteForce
Enhanced input validation, error handling, and request/response management
"""

import logging
import traceback
from datetime import datetime
from functools import wraps
from typing import Any, Dict, List, Tuple

from flask import jsonify, request

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error for API requests"""

    def __init__(self, message: str, field: str = None, code: str = "VALIDATION_ERROR"):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(self.message)


class APIError(Exception):
    """Custom API error with status code"""

    def __init__(self, message: str, status_code: int = 500, code: str = "API_ERROR"):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(self.message)


def validate_json_request(
    required_fields: list[str] = None, optional_fields: list[str] = None
) -> dict[str, Any]:
    """
    Validate JSON request with required and optional fields

    Args:
        required_fields: List of required field names
        optional_fields: List of optional field names (for documentation)

    Returns:
        Dict containing validated JSON data

    Raises:
        ValidationError: If validation fails
    """
    if not request.is_json:
        raise ValidationError("Request must be JSON", code="INVALID_CONTENT_TYPE")

    try:
        data = request.get_json()
    except Exception as e:
        raise ValidationError(f"Invalid JSON: {str(e)}", code="INVALID_JSON")

    if not data:
        raise ValidationError("Empty JSON data", code="EMPTY_REQUEST")

    # Check required fields
    if required_fields:
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                code="MISSING_FIELDS",
            )

    return data


def validate_stores_data(stores: list[dict]) -> list[dict]:
    """
    Validate stores data structure

    Args:
        stores: List of store dictionaries

    Returns:
        List of validated store dictionaries

    Raises:
        ValidationError: If stores data is invalid
    """
    if not isinstance(stores, list):
        raise ValidationError("Stores must be a list", field="stores")

    if len(stores) == 0:
        raise ValidationError("At least one store is required", field="stores")

    if len(stores) > 100:  # Reasonable limit
        raise ValidationError("Too many stores (max 100)", field="stores")

    required_store_fields = ["address", "name"]

    validated_stores = []

    for i, store in enumerate(stores):
        if not isinstance(store, dict):
            raise ValidationError(f"Store {i} must be an object", field=f"stores[{i}]")

        # Check required fields
        for field in required_store_fields:
            if field not in store or not store[field]:
                raise ValidationError(
                    f"Store {i} missing required field: {field}",
                    field=f"stores[{i}].{field}",
                )

        # Validate address
        if not isinstance(store["address"], str) or len(store["address"].strip()) < 5:
            raise ValidationError(
                f"Store {i} address must be a valid string (min 5 characters)",
                field=f"stores[{i}].address",
            )

        # Validate name
        if not isinstance(store["name"], str) or len(store["name"].strip()) < 1:
            raise ValidationError(
                f"Store {i} name must be a valid string", field=f"stores[{i}].name"
            )

        # Validate coordinates if provided
        if "latitude" in store and store["latitude"] is not None:
            try:
                lat = float(store["latitude"])
                if not -90 <= lat <= 90:
                    raise ValidationError(
                        f"Store {i} latitude must be between -90 and 90",
                        field=f"stores[{i}].latitude",
                    )
            except (ValueError, TypeError):
                raise ValidationError(
                    f"Store {i} latitude must be a number",
                    field=f"stores[{i}].latitude",
                )

        if "longitude" in store and store["longitude"] is not None:
            try:
                lng = float(store["longitude"])
                if not -180 <= lng <= 180:
                    raise ValidationError(
                        f"Store {i} longitude must be between -180 and 180",
                        field=f"stores[{i}].longitude",
                    )
            except (ValueError, TypeError):
                raise ValidationError(
                    f"Store {i} longitude must be a number",
                    field=f"stores[{i}].longitude",
                )

        validated_stores.append(store)

    return validated_stores


def validate_algorithm_options(options: dict) -> dict:
    """
    Validate algorithm options

    Args:
        options: Dictionary of algorithm options

    Returns:
        Dictionary of validated options

    Raises:
        ValidationError: If options are invalid
    """
    if not isinstance(options, dict):
        raise ValidationError("Options must be an object", field="options")

    # Validate algorithm choice
    valid_algorithms = ["default", "genetic", "simulated_annealing", "multi_objective"]
    algorithm = options.get("algorithm", "default")

    if algorithm not in valid_algorithms:
        raise ValidationError(
            f"Invalid algorithm. Must be one of: {', '.join(valid_algorithms)}",
            field="options.algorithm",
        )

    # Validate numeric parameters
    numeric_params = {
        "ga_population_size": (10, 1000),
        "ga_generations": (10, 2000),
        "ga_mutation_rate": (0.0, 1.0),
        "ga_crossover_rate": (0.0, 1.0),
        "ga_elite_size": (1, 100),
        "ga_tournament_size": (2, 10),
        "sa_initial_temperature": (1.0, 10000.0),
        "sa_final_temperature": (0.001, 100.0),
        "sa_cooling_rate": (0.8, 0.999),
        "sa_max_iterations": (100, 50000),
        "sa_iterations_per_temp": (10, 1000),
        "sa_reheat_threshold": (100, 10000),
        "sa_min_improvement_threshold": (0.0001, 1.0),
        "mo_population_size": (10, 500),
        "mo_generations": (10, 1000),
        "mo_mutation_rate": (0.0, 1.0),
        "mo_crossover_rate": (0.0, 1.0),
        "mo_tournament_size": (2, 10),
    }

    for param, (min_val, max_val) in numeric_params.items():
        if param in options:
            try:
                value = float(options[param])
                if not min_val <= value <= max_val:
                    raise ValidationError(
                        f"{param} must be between {min_val} and {max_val}",
                        field=f"options.{param}",
                    )
                options[param] = value
            except (ValueError, TypeError):
                raise ValidationError(
                    f"{param} must be a number", field=f"options.{param}"
                )

    # Validate string parameters
    if "mo_objectives" in options:
        objectives = options["mo_objectives"]
        valid_objectives = ["distance", "time", "distance,time", "time,distance"]
        if objectives not in valid_objectives:
            raise ValidationError(
                f"mo_objectives must be one of: {', '.join(valid_objectives)}",
                field="options.mo_objectives",
            )

    return options


def api_error_handler(f):
    """
    Decorator for comprehensive API error handling
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)

        except ValidationError as e:
            logger.warning(f"Validation error in {f.__name__}: {e.message}")
            return (
                jsonify(
                    {
                        "error": e.message,
                        "code": e.code,
                        "field": e.field,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ),
                400,
            )

        except APIError as e:
            logger.error(f"API error in {f.__name__}: {e.message}")
            return (
                jsonify(
                    {
                        "error": e.message,
                        "code": e.code,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ),
                e.status_code,
            )

        except Exception as e:
            # Log the full traceback for debugging
            logger.error(f"Unexpected error in {f.__name__}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")

            # Return generic error to client (don't expose internal details)
            return (
                jsonify(
                    {
                        "error": "An unexpected error occurred",
                        "code": "INTERNAL_ERROR",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ),
                500,
            )

    return decorated_function


def create_success_response(
    data: Any, status_code: int = 200, message: str = None, metadata: dict = None
) -> tuple[dict, int]:
    """
    Create standardized success response

    Args:
        data: Response data
        status_code: HTTP status code
        message: Optional success message
        metadata: Optional metadata dictionary

    Returns:
        Tuple of (response_dict, status_code)
    """
    response = {
        "success": True,
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if message:
        response["message"] = message

    if metadata:
        response["metadata"] = metadata

    return jsonify(response), status_code


def paginate_response(
    items: list, page: int = 1, per_page: int = 10, max_per_page: int = 100
) -> dict:
    """
    Create paginated response

    Args:
        items: List of items to paginate
        page: Current page number (1-based)
        per_page: Items per page
        max_per_page: Maximum allowed items per page

    Returns:
        Dictionary with paginated data and metadata
    """
    # Validate pagination parameters
    if page < 1:
        raise ValidationError("Page must be >= 1", field="page")

    if per_page < 1:
        raise ValidationError("Per page must be >= 1", field="per_page")

    if per_page > max_per_page:
        raise ValidationError(f"Per page must be <= {max_per_page}", field="per_page")

    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    page_items = items[start_idx:end_idx]

    return {
        "items": page_items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    }
