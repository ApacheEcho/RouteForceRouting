"""
Documented API Routes using Flask-RESTX
Enhances existing API endpoints with comprehensive documentation
"""

from flask import request, current_app, session
from flask_restx import Resource, Namespace, fields
import logging
from datetime import datetime
from typing import Dict, Any

from app.services.routing_service import RoutingService
from app.services.database_service import DatabaseService
from app import cache, limiter
from app.monitoring import metrics_collector

# Import models from API documentation config
from app.api_docs import (
    api, route_ns, analytics_ns, mobile_ns, traffic_ns,
    route_request_model, route_response_model, error_model, success_model,
    store_model, constraints_model, algorithm_options_model, analytics_model
)

# AUTO-PILOT: Enhanced validation and error handling
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

logger = logging.getLogger(__name__)


def get_current_user_id():
    """Get current user ID from session (placeholder for authentication)"""
    return session.get("user_id")


@route_ns.route('')
class RouteCollection(Resource):
    @route_ns.doc('create_route',
                 description='Create a new optimized route for field execution teams',
                 responses={
                     201: 'Route created successfully',
                     400: 'Bad request - invalid input data',
                     401: 'Authentication required',
                     422: 'Validation error',
                     500: 'Internal server error'
                 })
    @route_ns.expect(route_request_model)
    @route_ns.marshal_with(route_response_model, code=201)
    @limiter.limit("100 per minute")
    def post(self):
        """
        Create a new route via API with database persistence

        This endpoint accepts a list of stores and generates an optimized route
        using various algorithms including genetic algorithm, simulated annealing,
        and multi-objective optimization.

        The response includes the optimized route sequence, distance calculations,
        and a Google Maps URL for navigation.
        """
        try:
            # Validate JSON request
            data = validate_json_request(required_fields=["stores"])

            # Validate stores data
            stores = validate_stores_data(data["stores"])

            # Validate constraints (optional)
            constraints = data.get("constraints", {})
            if not isinstance(constraints, dict):
                raise ValidationError("Constraints must be an object", field="constraints")

            # Validate options (optional)
            options = data.get("options", {})
            options = validate_algorithm_options(options)

            # Get user ID (will be from authentication system later)
            user_id = get_current_user_id()

            # Generate route with database integration
            routing_service = RoutingService(user_id=user_id)

            # Extract algorithm from options
            algorithm = options.get("algorithm", "default")

            # Extract algorithm-specific parameters
            algorithm_params = {}
            if algorithm == "genetic":
                algorithm_params = {
                    "population_size": options.get("ga_population_size", 100),
                    "generations": options.get("ga_generations", 500),
                    "mutation_rate": options.get("ga_mutation_rate", 0.02),
                    "crossover_rate": options.get("ga_crossover_rate", 0.8),
                    "elite_size": options.get("ga_elite_size", 20),
                    "tournament_size": options.get("ga_tournament_size", 3),
                }
            elif algorithm == "simulated_annealing":
                algorithm_params = {
                    "initial_temperature": options.get("sa_initial_temperature", 1000.0),
                    "final_temperature": options.get("sa_final_temperature", 0.1),
                    "cooling_rate": options.get("sa_cooling_rate", 0.99),
                    "max_iterations": options.get("sa_max_iterations", 10000),
                }
            elif algorithm == "multi_objective":
                algorithm_params = {
                    "objectives": options.get("mo_objectives", "distance,time").split(","),
                    "population_size": options.get("mo_population_size", 100),
                    "generations": options.get("mo_generations", 200),
                }

            # Generate route
            route = routing_service.generate_route(
                stores, constraints=constraints, algorithm=algorithm, **algorithm_params
            )

            # Get optimization metrics
            metrics = routing_service.get_optimization_metrics()

            # Prepare response data
            route_data = {
                "route_id": route.get("id") if isinstance(route, dict) else None,
                "optimized_route": route if isinstance(route, list) else route.get("route", []),
                "total_distance": metrics.total_distance if metrics else 0,
                "total_duration": metrics.total_time if metrics else 0,
                "algorithm_used": algorithm,
                "optimization_time": routing_service.get_last_processing_time(),
                "google_maps_url": route.get("google_maps_url") if isinstance(route, dict) else "",
                "created_at": datetime.utcnow()
            }

            return route_data, 201

        except ValidationError as e:
            return {"error": str(e), "status_code": 400, "timestamp": datetime.utcnow()}, 400
        except APIError as e:
            return {"error": str(e), "status_code": e.status_code, "timestamp": datetime.utcnow()}, e.status_code
        except Exception as e:
            logger.error(f"Unexpected error in route creation: {str(e)}")
            return {"error": "Internal server error", "status_code": 500, "timestamp": datetime.utcnow()}, 500

    @route_ns.doc('get_routes',
                 description='Get route history for current user with pagination',
                 params={
                     'page': 'Page number (default: 1)',
                     'per_page': 'Items per page (default: 10, max: 50)'
                 },
                 responses={
                     200: 'Routes retrieved successfully',
                     401: 'Authentication required',
                     500: 'Internal server error'
                 })
    @route_ns.marshal_list_with(route_response_model)
    @limiter.limit("100 per minute")
    def get(self):
        """
        Get route history for current user with pagination

        Returns a paginated list of previously generated routes for the authenticated user.
        Includes route details, optimization metrics, and timestamps.
        """
        try:
            user_id = get_current_user_id()
            if not user_id:
                return {"error": "Authentication required", "status_code": 401, "timestamp": datetime.utcnow()}, 401

            # Get pagination parameters
            page = request.args.get("page", 1, type=int)
            per_page = request.args.get("per_page", 10, type=int)

            routing_service = RoutingService(user_id=user_id)

            # Get routes with pagination
            all_routes = routing_service.get_route_history(limit=per_page * 10)

            # Apply pagination
            paginated_data = paginate_response(all_routes, page, per_page, max_per_page=50)

            return paginated_data, 200

        except Exception as e:
            logger.error(f"Error retrieving routes: {str(e)}")
            return {"error": "Internal server error", "status_code": 500, "timestamp": datetime.utcnow()}, 500


@route_ns.route('/<int:route_id>')
class Route(Resource):
    @route_ns.doc('get_route',
                 description='Get specific route by ID',
                 params={'route_id': 'Unique route identifier'},
                 responses={
                     200: 'Route retrieved successfully',
                     401: 'Authentication required',
                     404: 'Route not found',
                     500: 'Internal server error'
                 })
    @route_ns.marshal_with(route_response_model)
    @limiter.limit("100 per minute")
    def get(self, route_id):
        """
        Get route by ID from database

        Retrieves detailed information about a specific route including
        the optimized sequence, metrics, and navigation information.
        """
        try:
            if route_id <= 0:
                return {"error": "Route ID must be a positive integer", "status_code": 400, "timestamp": datetime.utcnow()}, 400

            user_id = get_current_user_id()
            routing_service = RoutingService(user_id=user_id)

            route = routing_service.get_route_by_id(route_id)

            if not route:
                return {"error": "Route not found", "status_code": 404, "timestamp": datetime.utcnow()}, 404

            return route, 200

        except Exception as e:
            logger.error(f"Error retrieving route {route_id}: {str(e)}")
            return {"error": "Internal server error", "status_code": 500, "timestamp": datetime.utcnow()}, 500


@analytics_ns.route('/usage')
class AnalyticsUsage(Resource):
    @analytics_ns.doc('get_analytics',
                     description='Get analytics and usage statistics',
                     params={
                         'period': 'Time period (day, week, month, year)',
                         'start_date': 'Start date (YYYY-MM-DD)',
                         'end_date': 'End date (YYYY-MM-DD)'
                     },
                     responses={
                         200: 'Analytics retrieved successfully',
                         401: 'Authentication required',
                         500: 'Internal server error'
                     })
    @analytics_ns.marshal_with(analytics_model)
    @limiter.limit("50 per minute")
    def get(self):
        """
        Get analytics and usage statistics

        Returns comprehensive analytics including route generation statistics,
        algorithm usage patterns, and performance metrics.
        """
        try:
            user_id = get_current_user_id()
            if not user_id:
                return {"error": "Authentication required", "status_code": 401, "timestamp": datetime.utcnow()}, 401

            # Get analytics parameters
            period = request.args.get('period', 'week')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')

            # Mock analytics data for demonstration
            analytics_data = {
                "total_routes": 150,
                "total_distance": 12500.5,
                "avg_optimization_time": 2.3,
                "algorithm_usage": {
                    "genetic": 45,
                    "simulated_annealing": 35,
                    "default": 70
                },
                "time_period": period
            }

            return analytics_data, 200

        except Exception as e:
            logger.error(f"Error retrieving analytics: {str(e)}")
            return {"error": "Internal server error", "status_code": 500, "timestamp": datetime.utcnow()}, 500