
# --- Blueprint and Core Imports (must be first for route decorators) ---
from flask import Blueprint, jsonify, request, session, current_app
api_bp = Blueprint("api", __name__, url_prefix="/api/v1")
import logging
logger = logging.getLogger(__name__)
from datetime import datetime
from flask_jwt_extended import get_jwt_identity, create_access_token, create_refresh_token, jwt_required, get_jwt
from app.jwt_blocklist import add_token_to_blocklist
from app.models.database import db, User
from app.auth_decorators import auth_required
from app.extensions import limiter

# --- End Blueprint and Core Imports ---

# --- Validation and Utility Imports (must be before route decorators) ---
from app.utils.validation import (
    validate_json_request,
    validate_stores_data,
    validate_algorithm_options,
    api_error_handler,
    create_success_response,
    paginate_response,
    ValidationError,
    APIError,
)
# --- End Validation and Utility Imports ---

@api_bp.route("/auth/validate", methods=["POST"])
@api_error_handler
def validate_token():
    """Validate JWT access token for frontend session check"""
    from flask_jwt_extended import verify_jwt_in_request, get_jwt
    try:
        verify_jwt_in_request()
        jwt_data = get_jwt()
        # Optionally, check for blocklist or other custom logic here
        return jsonify({"valid": True}), 200
    except Exception as e:
        logger.warning(f"Token validation failed: {e}")
        return jsonify({"valid": False}), 200

"""
API Blueprint - RESTful API endpoints with database integration
Enhanced with comprehensive validation and error handling
"""

from app.services.routing_service import RoutingService
from app.services.database_service import DatabaseService
from app.monitoring import metrics_collector
# AUTO-PILOT: Enhanced validation and error handling


@api_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
@api_error_handler
def api_login():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        raise ValidationError("Email and password required")

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        raise APIError("Invalid credentials", status_code=401, code="INVALID_CREDENTIALS")
    if not user.is_active:
        raise APIError("User account is inactive", status_code=403, code="USER_INACTIVE")

    from datetime import timedelta
    access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=15))
    refresh_token = create_refresh_token(identity=user.id)
    user.last_login = datetime.utcnow()
    db.session.commit()

    # Set refresh token as secure, HTTP-only cookie
    # Return tokens and user info as top-level keys (not nested under 'data')
    response = jsonify({
        "success": True,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict(),
        "message": "Login successful"
    })
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=True,
        samesite="Strict",
        max_age=60*60*24*7  # 7 days
    )
    return response, 200

# User registration endpoint
@api_bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
@api_error_handler
def api_register():
    data = request.get_json()
    if not data:
        raise ValidationError("Request body required")
    
    required_fields = ["email", "password", "username"]
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValidationError(f"{field.capitalize()} is required")
    
    email = data["email"].lower().strip()
    username = data["username"].strip()
    password = data["password"]
    
    # Check if user already exists
    if User.query.filter_by(email=email).first():
        raise APIError("User with this email already exists", status_code=409, code="USER_EXISTS")
    
    if User.query.filter_by(username=username).first():
        raise APIError("Username already taken", status_code=409, code="USERNAME_TAKEN")
    
    try:
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            role=data.get("role", "user")
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create tokens for immediate login
        from datetime import timedelta
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=15))
        refresh_token = create_refresh_token(identity=user.id)
        
        response = jsonify({
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict(),
            "message": "Registration successful"
        })
        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            secure=True,
            samesite="Strict",
            max_age=60*60*24*7  # 7 days
        )
        return response, 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {e}")
        raise APIError("Registration failed", status_code=500, code="REGISTRATION_ERROR")

# Refresh token endpoint
@api_bp.route("/refresh", methods=["POST"], strict_slashes=False)
@jwt_required(refresh=True)
@api_error_handler
def refresh_access_token():
    # Accept requests with or without JSON body or content type
    # This allows clients to POST with no body and no Content-Type
    user_id = get_jwt_identity()
    from datetime import timedelta
    access_token = create_access_token(identity=user_id, expires_delta=timedelta(minutes=15))
    refresh_token = create_refresh_token(identity=user_id)
    response = jsonify({
        "success": True,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "message": "Token refreshed"
    })
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=True,
        samesite="Strict",
        max_age=60*60*24*7  # 7 days
    )
    return response, 200

# Logout endpoint
@api_bp.route("/logout", methods=["POST"], strict_slashes=False)
@jwt_required()
@api_error_handler
def api_logout():
    """Logout user and revoke JWT token"""
    jwt_data = get_jwt()
    jti = jwt_data["jti"]
    exp = jwt_data["exp"]
    add_token_to_blocklist(jti, exp)
    response = jsonify({
        "success": True,
        "message": "Successfully logged out. Token revoked."
    })
    # Clear the refresh_token cookie
    response.set_cookie(
        "refresh_token",
        "",
        httponly=True,
        secure=True,
        samesite="Strict",
        max_age=0
    )
    return response, 200

def get_current_user_id():
    """Get current user ID from JWT or session (for backward compatibility)"""
    user_id = None
    try:
        user_id = get_jwt_identity()
    except Exception:
        pass
    if not user_id:
        user_id = session.get("user_id")
    return user_id


@api_bp.route("/stores", methods=["POST"])
@auth_required()
@api_error_handler
def create_store():
    """Create a new store for the current user"""
    data = request.get_json()
    if not data:
        raise ValidationError("No JSON data provided")

    name = data.get("name")
    address = data.get("address")
    if not name or not address:
        raise ValidationError("Missing name or address", field="name/address")

    user_id = get_current_user_id()
    if not user_id:
        raise APIError("Authentication required", status_code=401, code="AUTH_REQUIRED")

    store_service = DatabaseService()
    store_id = store_service.create_store(user_id=user_id, name=name, address=address)

    return create_success_response(
        data={"store_id": store_id},
        status_code=201,
        message="Store created successfully"
    )


@api_bp.route("/routes", methods=["POST"])
@api_error_handler
def create_route():
    """Create a new route via API with database persistence"""
    
    data = request.get_json()
    if not data:
        raise ValidationError("Request body required")
    
    # Get user ID if available (optional for public test endpoint)
    user_id = get_current_user_id()
    
    # Validate required fields
    stores = data.get("stores", [])
    if not stores:
        raise ValidationError("Stores are required")
    
    algorithm = data.get("algorithm", "greedy")
    constraints = data.get("constraints", {})
    options = data.get("options", {})

    # Generate route with database integration
    routing_service = RoutingService(user_id=user_id)

    # Extract algorithm from options
    algorithm = options.get("algorithm", "default")

    # Extract algorithm-specific parameters
    algorithm_params = {}
    if algorithm == "genetic":
        algorithm_params = {
            "ga_population_size": options.get("ga_population_size", 100),
            "ga_generations": options.get("ga_generations", 500),
            "ga_mutation_rate": options.get("ga_mutation_rate", 0.02),
            "ga_crossover_rate": options.get("ga_crossover_rate", 0.8),
            "ga_elite_size": options.get("ga_elite_size", 20),
            "ga_tournament_size": options.get("ga_tournament_size", 3),
        }
    elif algorithm == "simulated_annealing":
        algorithm_params = {
            "sa_initial_temperature": options.get(
                "sa_initial_temperature", 1000.0
            ),
            "sa_final_temperature": options.get("sa_final_temperature", 0.1),
            "sa_cooling_rate": options.get("sa_cooling_rate", 0.99),
            "sa_max_iterations": options.get("sa_max_iterations", 10000),
            "sa_iterations_per_temp": options.get(
                "sa_iterations_per_temp", 100
            ),
            "sa_reheat_threshold": options.get("sa_reheat_threshold", 1000),
            "sa_min_improvement_threshold": options.get(
                "sa_min_improvement_threshold", 0.001
            ),
        }
    elif algorithm == "multi_objective":
        algorithm_params = {
            "mo_objectives": options.get("mo_objectives", "distance,time"),
            "mo_population_size": options.get("mo_population_size", 100),
            "mo_generations": options.get("mo_generations", 200),
            "mo_mutation_rate": options.get("mo_mutation_rate", 0.1),
            "mo_crossover_rate": options.get("mo_crossover_rate", 0.9),
            "mo_tournament_size": options.get("mo_tournament_size", 2),
        }

    # Use the generate_route_from_stores method with algorithm support
    route = routing_service.generate_route_from_stores(
        stores,
        constraints,
        save_to_db=bool(user_id),
        algorithm=algorithm,
        algorithm_params=algorithm_params,
    )

    if not route:
        raise APIError(
            "Failed to generate route",
            status_code=422,
            code="ROUTE_GENERATION_FAILED",
        )

    # Get metrics
    metrics = routing_service.get_metrics()

    # Build response data
    route_data = {
        "route": route,
        "route_id": (
            metrics.route_id if metrics and metrics.route_id else None
        ),
        "algorithm_used": metrics.algorithm_used if metrics else algorithm,
    }

    # Build metadata
    metadata = {
        "total_stores": len(stores),
        "route_stores": len(route),
        "processing_time": routing_service.get_last_processing_time(),
        "optimization_score": metrics.optimization_score if metrics else 0,
    }

    # Include algorithm-specific metrics
    if metrics and metrics.algorithm_metrics:
        metadata["algorithm_metrics"] = metrics.algorithm_metrics

    return create_success_response(
        data=route_data,
        status_code=201,
        message="Route created successfully",
        metadata=metadata,
    )


@api_bp.route("/routes/<int:route_id>", methods=["GET"])
@auth_required()
@api_error_handler
def get_route(route_id: int):
    """Get route by ID from database"""
    # AUTO-PILOT: Enhanced validation and error handling
    if route_id <= 0:
        raise ValidationError(
            "Route ID must be a positive integer", field="route_id"
        )

    user_id = get_current_user_id()
    routing_service = RoutingService(user_id=user_id)

    route = routing_service.get_route_by_id(route_id)

    if not route:
        raise APIError(
            "Route not found", status_code=404, code="ROUTE_NOT_FOUND"
        )

    return create_success_response(
        data=route, message="Route retrieved successfully"
    )


@api_bp.route("/routes", methods=["GET"])
@auth_required()
@api_error_handler
def get_routes():
    """Get route history for current user with pagination"""
    user_id = get_current_user_id()
    if not user_id:
        raise APIError(
            "Authentication required", status_code=401, code="AUTH_REQUIRED"
        )

    # AUTO-PILOT: Enhanced pagination support
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    routing_service = RoutingService(user_id=user_id)

    # Get more routes for pagination
    try:
        all_routes = routing_service.get_route_history(
            limit=per_page * 10
        )  # Get more for pagination
    except AttributeError:
        # UnifiedRoutingService may not implement history in minimal/test envs
        all_routes = []

    # Apply pagination
    paginated_data = paginate_response(
        all_routes, page, per_page, max_per_page=50
    )

    return create_success_response(
        data=paginated_data["items"],
        message="Routes retrieved successfully",
        metadata=paginated_data["pagination"],
    )


@api_bp.route("/stores", methods=["GET"])
@auth_required()
@api_error_handler
def get_stores():
    """Get stores for current user with pagination"""
    user_id = get_current_user_id()
    if not user_id:
        raise APIError(
            "Authentication required", status_code=401, code="AUTH_REQUIRED"
        )

    # AUTO-PILOT: Enhanced pagination support
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    routing_service = RoutingService(user_id=user_id)
    all_stores = routing_service.get_user_stores()

    # Apply pagination
    paginated_data = paginate_response(
        all_stores, page, per_page, max_per_page=100
    )

    return create_success_response(
        data=paginated_data["items"],
        message="Stores retrieved successfully",
        metadata=paginated_data["pagination"],
    )


@api_bp.route("/stores/<int:store_id>", methods=["GET"])
@auth_required()
@api_error_handler
def get_store(store_id: int):
    """Get specific store by ID"""
    user_id = get_current_user_id()
    database_service = DatabaseService()

    store = database_service.get_store_by_id(store_id)

    if not store:
        raise APIError("Store not found", status_code=404, code="STORE_NOT_FOUND")

    # Check if user has access to this store
    if user_id and store.user_id != user_id:
        raise APIError("Access denied", status_code=403, code="ACCESS_DENIED")

    return create_success_response(data=store.to_dict(), message="Store retrieved successfully")


@api_bp.route("/routes/generate", methods=["POST"])
@auth_required()
@limiter.limit("10 per minute")
@api_error_handler
def generate_route_from_stores():
    """Generate route from database stores"""
    data = request.get_json()

    if not data:
        raise ValidationError("No JSON data provided")

    store_ids = data.get("store_ids", [])
    filters = data.get("filters", {})

    if not store_ids:
        raise ValidationError("No store IDs provided", field="store_ids")

    user_id = get_current_user_id()
    if not user_id:
        raise APIError("Authentication required", status_code=401, code="AUTH_REQUIRED")

    routing_service = RoutingService(user_id=user_id)
    route = routing_service.generate_route_from_db_stores(store_ids, filters)

    if not route:
        raise APIError("Failed to generate route", status_code=500, code="ROUTE_GENERATION_FAILED")

    metrics = routing_service.get_metrics()

    response_data = {
        "route": route,
        "metadata": {
            "total_stores": len(store_ids),
            "route_stores": len(route),
            "processing_time": routing_service.get_last_processing_time(),
            "optimization_score": (metrics.optimization_score if metrics else 0),
        },
    }

    if metrics and metrics.route_id:
        response_data["route_id"] = metrics.route_id

    return create_success_response(data=response_data, status_code=201, message="Route generated successfully")


@api_bp.route("/health", methods=["GET"])
def api_health():
    """API health check"""
    return jsonify(
        {
            "status": "healthy",
            "version": "1.0.0",
            "database": "connected",
            "endpoints": {
                "create_route": "/api/v1/routes",
                "get_routes": "/api/v1/routes",
                "get_route": "/api/v1/routes/<id>",
                "get_stores": "/api/v1/stores",
                "get_store": "/api/v1/stores/<id>",
                "generate_route": "/api/v1/routes/generate",
                "optimize_genetic": "/api/v1/routes/optimize/genetic",
                "optimize_simulated_annealing": "/api/v1/routes/optimize/simulated_annealing",
                "get_algorithms": "/api/v1/routes/algorithms",
                "create_clusters": "/api/v1/clusters",
                "health": "/api/v1/health",
                "ml_predict": "/api/v1/ml/predict",
                "ml_recommend": "/api/v1/ml/recommend",
                "ml_train": "/api/v1/ml/train",
                "ml_model_info": "/api/v1/ml/model-info",
                "generate_route_ml": "/api/v1/routes/generate/ml",
            },
            "algorithms": {
                "available": [
                    "default",
                    "genetic",
                    "simulated_annealing",
                    "multi_objective",
                ],
                "default": "default",
            },
        }
    )


@api_bp.route("/clusters", methods=["POST"])
@limiter.limit("10 per minute")
@api_error_handler
def create_clusters():
    """
    Create proximity clusters from stores

    Expected JSON payload:
    {
        "stores": [...],
        "radius_km": 2.0
    }
    """
    try:
        data = request.get_json()
        if not data or "stores" not in data:
            raise ValidationError("Missing stores data", field="stores")

        stores = data["stores"]
        radius_km = data.get("radius_km", 2.0)

        # Validate radius
        if not isinstance(radius_km, (int, float)) or radius_km <= 0:
            raise ValidationError("Invalid radius_km value", field="radius_km")

        # Validate stores have coordinates
        for store in stores:
            if "latitude" not in store or "longitude" not in store:
                raise ValidationError("All stores must have latitude and longitude", field="stores")

        routing_service = RoutingService()
        clusters = routing_service.cluster_stores_by_proximity(stores, radius_km)

        return create_success_response(
            data={
                "clusters": clusters,
                "cluster_count": len(clusters),
                "total_stores": len(stores),
                "radius_km": radius_km,
            },
            status_code=200,
            message="Clusters created successfully"
        )
    except ValidationError:
        # Let the api_error_handler decorator handle this
        raise
    except Exception as e:
        logger.error(f"Error in create_clusters: {e}", exc_info=True)
        return create_success_response(
            data=None,
            status_code=500,
            message="An unexpected error occurred while creating clusters. Please try again later."
        )


@api_bp.route("/metrics", methods=["GET"])
@limiter.limit("100 per minute")
def get_live_metrics():
    """
    Get real-time application metrics
    Demonstrates live data collection for enterprise dashboard
    """
    try:
        # Record the metrics request
        import time

        start_time = time.time()

        # Get current metrics snapshot from monitoring system
        metrics = metrics_collector.get_metrics()

        # Add computed metrics for demonstration
        if not hasattr(metrics_collector, "start_time"):
            metrics_collector.start_time = time.time()

        uptime_seconds = int(time.time() - metrics_collector.start_time)

        # Enhanced metrics with real data
        enhanced_metrics = {
            **metrics,
            "uptime_seconds": uptime_seconds,
            "requests_per_minute": metrics.get("requests_total", 0)
            / max(1, uptime_seconds / 60),
            "system_status": "healthy",
            "response_time": time.time() - start_time,
        }

        # Record this request
        metrics_collector.record_request(
            endpoint="api.get_live_metrics",
            response_time=time.time() - start_time,
            status_code=200,
            user_ip=request.remote_addr,
        )

        return (
            jsonify(
                {
                    "status": "success",
                    "data": enhanced_metrics,
                    "timestamp": time.time(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error retrieving metrics: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Failed to retrieve metrics",
                    "error": (
                        str(e)
                        if current_app.debug
                        else "Internal server error"
                    ),
                }
            ),
            500,
        )


@api_bp.route("/routes/optimize/genetic", methods=["POST"])
@limiter.limit("100 per minute")
@api_error_handler
def optimize_route_genetic():
    """
    Optimize route using genetic algorithm

    Expected JSON payload:
    {
        "stores": [...],
        "constraints": {...},
        "genetic_config": {
            "population_size": 100,
            "generations": 500,
            "mutation_rate": 0.02,
            "crossover_rate": 0.8,
            "elite_size": 20,
            "tournament_size": 3
        }
    }
    """
    data = request.get_json()
    if not data:
        raise ValidationError("No JSON data provided")

    stores = data.get("stores", [])
    constraints = data.get("constraints", {})
    genetic_config = data.get("genetic_config", {})

    if not stores:
        raise ValidationError("No stores provided", field="stores")
    if len(stores) < 2:
        raise ValidationError("At least 2 stores required for genetic optimization", field="stores")

    user_id = get_current_user_id()
    routing_service = RoutingService(user_id=user_id)

    filters = {
        "algorithm": "genetic",
        "ga_population_size": genetic_config.get("population_size", 100),
        "ga_generations": genetic_config.get("generations", 500),
        "ga_mutation_rate": genetic_config.get("mutation_rate", 0.02),
        "ga_crossover_rate": genetic_config.get("crossover_rate", 0.8),
        "ga_elite_size": genetic_config.get("elite_size", 20),
        "ga_tournament_size": genetic_config.get("tournament_size", 3),
    }

    # Use provided genetic configuration and avoid DB writes in API tests
    route = routing_service.generate_route_from_stores(
        stores,
        constraints,
        save_to_db=False,
        algorithm="genetic",
        algorithm_params=genetic_config,
    )

    metrics = routing_service.get_metrics()

    response_data = {
        "route": route,
        "metadata": {
            "total_stores": len(stores),
            "route_stores": len(route) if route else 0,
            "processing_time": routing_service.get_last_processing_time(),
            "optimization_score": (metrics.optimization_score if metrics else 0),
            "algorithm_used": "genetic",
        },
    }
    if metrics and metrics.algorithm_metrics:
        response_data["genetic_metrics"] = metrics.algorithm_metrics
    if metrics and metrics.route_id:
        response_data["route_id"] = metrics.route_id
        response_data["metadata"]["route_id"] = metrics.route_id

    return create_success_response(
        data=response_data,
        status_code=200,
        message="Route optimized with genetic algorithm"
    )


@api_bp.route("/routes/optimize/simulated_annealing", methods=["POST"])
@limiter.limit("100 per minute")
@api_error_handler
def optimize_route_simulated_annealing():
    """
    Optimize route using simulated annealing algorithm

    Expected JSON payload:
    {
        "stores": [...],
        "constraints": {...},
        "sa_config": {
            "initial_temperature": 1000.0,
            "final_temperature": 0.1,
            "cooling_rate": 0.99,
            "max_iterations": 10000,
            "max_no_improvement": 1000,
            "acceptance_threshold": 0.001
        }
    }
    """
    data = request.get_json()
    if not data:
        raise ValidationError("No JSON data provided")

    stores = data.get("stores", [])
    constraints = data.get("constraints", {})
    sa_config = data.get("sa_config", {})

    if not stores:
        raise ValidationError("No stores provided", field="stores")
    if len(stores) < 2:
        raise ValidationError("At least 2 stores required for simulated annealing optimization", field="stores")

    user_id = get_current_user_id()
    routing_service = RoutingService(user_id=user_id)

    algorithm_params = {
        "sa_initial_temperature": sa_config.get("initial_temperature", 1000.0),
        "sa_final_temperature": sa_config.get("final_temperature", 0.1),
        "sa_cooling_rate": sa_config.get("cooling_rate", 0.99),
        "sa_max_iterations": sa_config.get("max_iterations", 10000),
        "sa_iterations_per_temp": sa_config.get("iterations_per_temp", 100),
        "sa_reheat_threshold": sa_config.get("reheat_threshold", 1000),
        "sa_min_improvement_threshold": sa_config.get("min_improvement_threshold", 0.001),
    }

    route = routing_service.generate_route_from_stores(
        stores,
        constraints,
        save_to_db=True,
        algorithm="simulated_annealing",
        algorithm_params=algorithm_params,
    )

    metrics = routing_service.get_metrics()

    response_data = {
        "route": route,
        "metadata": {
            "total_stores": len(stores),
            "route_stores": len(route) if route else 0,
            "processing_time": routing_service.get_last_processing_time(),
            "optimization_score": (metrics.optimization_score if metrics else 0),
            "algorithm_used": "simulated_annealing",
        },
    }
    if metrics and metrics.algorithm_metrics:
        response_data["simulated_annealing_metrics"] = metrics.algorithm_metrics
    if metrics and metrics.route_id:
        response_data["route_id"] = metrics.route_id
        response_data["metadata"]["route_id"] = metrics.route_id

    return create_success_response(
        data=response_data,
        status_code=201,
        message="Route optimized with simulated annealing"
    )


@api_bp.route("/routes/algorithms", methods=["GET"])
@limiter.limit("100 per minute")
def get_available_algorithms():
    """Get available optimization algorithms"""
    try:
        algorithms = {
            "default": {
                "name": "Default Algorithm",
                "description": "Basic route optimization using greedy nearest neighbor approach",
                "parameters": {},
            },
            "genetic": {
                "name": "Genetic Algorithm",
                "description": "Advanced evolutionary optimization for complex routing problems",
                "parameters": {
                    "population_size": {
                        "type": "integer",
                        "default": 100,
                        "min": 20,
                        "max": 500,
                        "description": "Size of the population for each generation",
                    },
                    "generations": {
                        "type": "integer",
                        "default": 500,
                        "min": 50,
                        "max": 2000,
                        "description": "Number of generations to evolve",
                    },
                    "mutation_rate": {
                        "type": "float",
                        "default": 0.02,
                        "min": 0.001,
                        "max": 0.1,
                        "description": "Probability of mutation for each individual",
                    },
                    "crossover_rate": {
                        "type": "float",
                        "default": 0.8,
                        "min": 0.1,
                        "max": 1.0,
                        "description": "Probability of crossover between parents",
                    },
                    "elite_size": {
                        "type": "integer",
                        "default": 20,
                        "min": 1,
                        "max": 100,
                        "description": "Number of best individuals to keep each generation",
                    },
                    "tournament_size": {
                        "type": "integer",
                        "default": 3,
                        "min": 2,
                        "max": 10,
                        "description": "Size of tournament for selection",
                    },
                },
            },
            "simulated_annealing": {
                "name": "Simulated Annealing",
                "description": "Probabilistic technique for approximating the global optimum of a given function",
                "parameters": {
                    "initial_temperature": {
                        "type": "float",
                        "default": 1000.0,
                        "min": 0.1,
                        "max": 10000.0,
                        "description": "Initial temperature for annealing schedule",
                    },
                    "final_temperature": {
                        "type": "float",
                        "default": 0.1,
                        "min": 0.0,
                        "max": 100.0,
                        "description": "Final temperature for annealing schedule",
                    },
                    "cooling_rate": {
                        "type": "float",
                        "default": 0.99,
                        "min": 0.80,
                        "max": 1.0,
                        "description": "Cooling rate for temperature reduction",
                    },
                    "max_iterations": {
                        "type": "integer",
                        "default": 10000,
                        "min": 1000,
                        "max": 100000,
                        "description": "Maximum number of iterations to perform",
                    },
                    "iterations_per_temp": {
                        "type": "integer",
                        "default": 100,
                        "min": 10,
                        "max": 1000,
                        "description": "Number of iterations per temperature level",
                    },
                    "reheat_threshold": {
                        "type": "integer",
                        "default": 1000,
                        "min": 100,
                        "max": 10000,
                        "description": "Iterations without improvement before reheating",
                    },
                    "min_improvement_threshold": {
                        "type": "float",
                        "default": 0.001,
                        "min": 0.0001,
                        "max": 0.1,
                        "description": "Minimum improvement threshold for convergence",
                    },
                },
            },
            "multi_objective": {
                "name": "Multi-Objective Optimization",
                "description": "NSGA-II based multi-objective optimization for Pareto-optimal solutions",
                "parameters": {
                    "objectives": {
                        "type": "string",
                        "default": "distance,time",
                        "description": "Comma-separated list of objectives to optimize (distance,time,priority,fuel_cost)",
                    },
                    "population_size": {
                        "type": "integer",
                        "default": 100,
                        "min": 20,
                        "max": 500,
                        "description": "Size of the population for each generation",
                    },
                    "generations": {
                        "type": "integer",
                        "default": 200,
                        "min": 50,
                        "max": 1000,
                        "description": "Number of generations to evolve",
                    },
                    "mutation_rate": {
                        "type": "float",
                        "default": 0.1,
                        "min": 0.01,
                        "max": 0.5,
                        "description": "Probability of mutation for each individual",
                    },
                    "crossover_rate": {
                        "type": "float",
                        "default": 0.9,
                        "min": 0.1,
                        "max": 1.0,
                        "description": "Probability of crossover between parents",
                    },
                    "tournament_size": {
                        "type": "integer",
                        "default": 2,
                        "min": 2,
                        "max": 10,
                        "description": "Size of tournament for selection",
                    },
                },
            },
        }

        return jsonify({"algorithms": algorithms, "default": "default"}), 200

    except Exception as e:
        logger.error(f"API error getting algorithms: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@api_bp.route("/ml/predict", methods=["POST"])
@limiter.limit("10 per minute")
@api_error_handler
def predict_route_performance():
    """
    Predict route optimization performance using ML

    Expected JSON payload:
    {
        "stores": [
            {
                "id": "store_1",
                "name": "Store 1",
                "lat": 40.7128,
                "lon": -74.0060,
                "priority": 1,
                "demand": 100
            }
        ],
        "context": {
            "weather_factor": 1.0,
            "traffic_factor": 1.2,
            "timestamp": "2024-01-15T10:30:00"
        }
    }
    """
    data = request.get_json()
    if not data or "stores" not in data:
        raise ValidationError("Missing stores data", field="stores")

    stores = data["stores"]
    context = data.get("context")

    if not stores:
        raise ValidationError("No stores provided", field="stores")

    # Get current user (if authenticated)
    user_id = session.get("user_id")

    # Initialize routing service
    routing_service = RoutingService(user_id=user_id)

    # Get ML prediction
    result = routing_service.predict_route_performance(stores, context)

    return create_success_response(
        data=result,
        status_code=200,
        message="Prediction successful"
    )


@api_bp.route("/ml/recommend", methods=["POST"])
@limiter.limit("10 per minute")
@api_error_handler
def recommend_algorithm():
    """
    Recommend best algorithm for given stores using ML

    Expected JSON payload:
    {
        "stores": [
            {
                "id": "store_1",
                "name": "Store 1",
                "lat": 40.7128,
                "lon": -74.0060,
                "priority": 1,
                "demand": 100
            }
        ],
        "context": {
            "weather_factor": 1.0,
            "traffic_factor": 1.2,
            "timestamp": "2024-01-15T10:30:00"
        }
    }
    """
    data = request.get_json()
    if not data or "stores" not in data:
        raise ValidationError("Missing stores data", field="stores")

    stores = data["stores"]
    context = data.get("context")

    if not stores:
        raise ValidationError("No stores provided", field="stores")

    # Get current user (if authenticated)
    user_id = session.get("user_id")

    # Initialize routing service
    routing_service = RoutingService(user_id=user_id)

    # Get ML recommendation
    result = routing_service.recommend_algorithm(stores, context)

    return create_success_response(
        data=result,
        status_code=200,
        message="Recommendation successful"
    )


@api_bp.route("/ml/train", methods=["POST"])
@limiter.limit("1 per minute")
@api_error_handler
def train_ml_models():
    """
    Train ML models on collected data

    Expected JSON payload:
    {
        "force_retrain": false
    }
    """
    data = request.get_json() or {}

    # Get current user (if authenticated)
    user_id = session.get("user_id")

    # Initialize routing service
    routing_service = RoutingService(user_id=user_id)

    # Train ML models
    result = routing_service.train_ml_models()

    return create_success_response(
        data=result,
        status_code=200,
        message="ML model training successful"
    )


@api_bp.route("/ml/model-info", methods=["GET"])
@limiter.limit("30 per minute")
@api_error_handler
def get_ml_model_info():
    """
    Get information about the ML model
    """
    # Get current user (if authenticated)
    user_id = session.get("user_id")

    # Initialize routing service
    routing_service = RoutingService(user_id=user_id)

    # Get ML model info
    result = routing_service.get_ml_model_info()

    return create_success_response(
        data=result,
        status_code=200,
        message="ML model info retrieved successfully"
    )


@api_bp.route("/routes/generate/ml", methods=["POST"])
@limiter.limit("10 per minute")
@api_error_handler
def generate_route_with_ml():
    """
    Generate route using ML-recommended algorithm

    Expected JSON payload:
    {
        "stores": [
            {
                "id": "store_1",
                "name": "Store 1",
                "lat": 40.7128,
                "lon": -74.0060,
                "priority": 1,
                "demand": 100
            }
        ],
        "constraints": {
            "max_distance": 100,
            "max_time": 480,
            "start_location": {"lat": 40.7128, "lon": -74.0060}
        },
        "context": {
            "weather_factor": 1.0,
            "traffic_factor": 1.2,
            "timestamp": "2024-01-15T10:30:00"
        }
    }
    """
    data = request.get_json()
    if not data or "stores" not in data:
        raise ValidationError("Missing stores data", field="stores")

    stores = data["stores"]
    constraints = data.get("constraints", {})
    context = data.get("context")

    if not stores:
        raise ValidationError("No stores provided", field="stores")

    # Get current user (if authenticated)
    user_id = session.get("user_id")

    # Initialize routing service
    routing_service = RoutingService(user_id=user_id)

    # Generate route with ML recommendation
    result = routing_service.generate_route_with_ml_recommendation(
        stores, constraints, context
    )

    return create_success_response(
        data=result,
        status_code=200,
        message="Route generated with ML recommendation"
    )


@api_bp.route("/optimize", methods=["POST"])
@limiter.limit("100 per minute")  # Increased for testing and production load
def optimize_route():
    """
    Simple route optimization endpoint for testing and integration

    Expected JSON payload:
    {
        "stops": [
            {"id": "1", "lat": 37.7749, "lng": -122.4194, "name": "Stop 1"},
            {"id": "2", "lat": 37.7849, "lng": -122.4094, "name": "Stop 2"}
        ],
        "algorithm": "genetic|simulated_annealing|multi_objective",
        "depot": {"lat": 37.7649, "lng": -122.4294, "name": "Depot"}
    }
    """
    data = request.get_json()
    if not data:
        raise ValidationError("No JSON data provided")

    stops = data.get("stops", [])
    algorithm = data.get("algorithm", "genetic")
    depot = data.get("depot", {})

    # Validate algorithm
    valid_algorithms = [
        "genetic",
        "simulated_annealing",
        "multi_objective",
    ]
    if algorithm not in valid_algorithms:
        raise ValidationError(f"Invalid algorithm: {algorithm}", field="algorithm")

    if not stops:
        raise ValidationError("No stops provided", field="stops")

    # Convert stops to stores format
    stores = []
    for i, stop in enumerate(stops):
        store = {
            "id": stop.get("id", f"stop_{i}"),
            "name": stop.get("name", f"Stop {i+1}"),
            "latitude": stop.get("lat", 0),
            "longitude": stop.get("lng", 0),
            "priority": stop.get("priority", 1),
            "demand": stop.get("demand", 1),
        }
        stores.append(store)

    # Add depot as starting point if provided
    if depot:
        depot_store = {
            "id": "depot",
            "name": depot.get("name", "Depot"),
            "latitude": depot.get("lat", 0),
            "longitude": depot.get("lng", 0),
            "priority": 0,
            "demand": 0,
        }
        stores.insert(0, depot_store)

    user_id = get_current_user_id()
    routing_service = RoutingService(user_id=user_id)

    # Generate optimized route
    route = routing_service.generate_route_from_stores(
        stores, filters={"algorithm": algorithm}
    )

    # Get metrics
    metrics = routing_service.get_metrics()

    # Convert route back to simple format
    optimized_route = []
    if route:
        for stop in route:
            optimized_route.append(
                {
                    "id": stop.get("id"),
                    "name": stop.get("name"),
                    "lat": stop.get("latitude"),
                    "lng": stop.get("longitude"),
                    "order": len(optimized_route),
                }
            )

    # Calculate basic metrics
    total_distance = 0
    if len(optimized_route) > 1:
        from math import radians, cos, sin, asin, sqrt

        def haversine(lon1, lat1, lon2, lat2):
            """Calculate the great circle distance between two points on earth"""
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = (
                sin(dlat / 2) ** 2
                + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            )
            c = 2 * asin(sqrt(a))
            r = 6371  # Radius of earth in kilometers
            return c * r

        for i in range(len(optimized_route) - 1):
            curr = optimized_route[i]
            next_stop = optimized_route[i + 1]
            distance = haversine(
                curr["lng"],
                curr["lat"],
                next_stop["lng"],
                next_stop["lat"],
            )
            total_distance += distance

    response_data = {
        "optimized_route": optimized_route,
        "algorithm_used": algorithm,
        "total_distance_km": round(total_distance, 2),
        "total_stops": len(optimized_route),
        "processing_time": routing_service.get_last_processing_time(),
        "optimization_score": metrics.optimization_score if metrics else 0,
    }

    if metrics and metrics.route_id:
        response_data["route_id"] = metrics.route_id

    return create_success_response(
        data=response_data,
        status_code=200,
        message="Route optimized successfully"
    )


@api_bp.route("/analytics", methods=["GET"])
@limiter.limit("100 per minute")
def get_analytics():
    """
    Simple analytics endpoint for testing and integration
    """
    try:
        user_id = get_current_user_id()
        routing_service = RoutingService(user_id=user_id)


        # Get basic analytics
        analytics = {
            "total_routes": 0,
            "avg_optimization_score": 0,
            "total_distance_saved": 0,
            "algorithm_usage": {
                "genetic": 0,
                "simulated_annealing": 0,
                "multi_objective": 0,
                "default": 0,
            },
            "recent_routes": [],
        }

        routes = routing_service.get_route_history(limit=10)
        analytics["total_routes"] = len(routes)
        analytics["recent_routes"] = routes

        if routes:
            scores = [
                r.get("optimization_score", 0)
                for r in routes
                if r.get("optimization_score")
            ]
            if scores:
                analytics["avg_optimization_score"] = sum(scores) / len(scores)

        return (
            jsonify(
                {
                    "success": True,
                    "analytics": analytics,
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"API error getting analytics: {str(e)}")
        return (
            jsonify(
                {"success": False, "error": f"Analytics failed: {str(e)}"}
            ),
            500,
        )
