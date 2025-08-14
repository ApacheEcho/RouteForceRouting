"""
Enhanced Main Routes Blueprint for RouteForce
Consolidated routing with file upload and route generation
"""

import csv
import io
import logging
import os
import time
from typing import Any, Dict, List, Optional

from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from werkzeug.utils import secure_filename

from app import limiter
from app.models.route_request import RouteRequest
from app.services.file_service import FileService
from app.services.routing_service import RoutingService

logger = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)

# Configuration
ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@main_bp.route("/")
def index():
    """
    Unified homepage with navigation to all RouteForce features
    """
    return render_template("index.html")


@main_bp.route("/dashboard")
def dashboard_redirect():
    """Redirect to enhanced dashboard"""
    # Try different dashboard endpoints until we find one that works
    try:
        return redirect(url_for("enhanced_dashboard.realtime_dashboard"))
    except Exception:
        try:
            return redirect(url_for("dashboard.dashboard"))
        except Exception:
            # Fallback to a working dashboard route
            return redirect("/sitemap")


@main_bp.route("/generate")
def route_generator():
    """Route generation interface"""
    return render_template("route_generator.html")


@main_bp.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify(
        {"status": "healthy", "service": "RouteForce Routing", "version": "1.0.0"}
    )


@main_bp.route("/sitemap")
def sitemap():
    """
    Display all available routes and endpoints for navigation
    """
    from flask import url_for

    routes = []
    for rule in current_app.url_map.iter_rules():
        if "GET" in rule.methods and len(rule.arguments) == 0:
            try:
                url = url_for(rule.endpoint, **(rule.defaults or {}))
                routes.append(
                    {
                        "endpoint": rule.endpoint,
                        "url": url,
                        "methods": list(rule.methods),
                        "description": getattr(
                            current_app.view_functions.get(rule.endpoint),
                            "__doc__",
                            "No description",
                        ),
                    }
                )
            except Exception:
                pass  # Skip routes that can't be built

    return render_template("sitemap.html", routes=routes)


@main_bp.route("/generate", methods=["POST"])
@limiter.limit("10 per minute")
def generate_route():
    """Generate route with comprehensive validation and error handling from form submission"""
    try:
        # Parse all form parameters
        file = request.files.get("file")
        proximity = "proximity" in request.form
        time_start = request.form.get("time_start")
        time_end = request.form.get("time_end")
        priority_only = "priority_only" in request.form
        exclude_days = request.form.getlist("exclude_days")
        max_stores_per_chain = request.form.get("max_stores_per_chain", type=int)
        min_sales_threshold = request.form.get("min_sales_threshold", type=float)

        # Validate required file
        if not file or file.filename == "":
            return jsonify({"error": "No file uploaded"}), 400

        # Validate file type
        if not allowed_file(file.filename):
            return (
                jsonify(
                    {
                        "error": "Invalid file type. Please upload CSV or Excel file.",
                        "supported_formats": list(ALLOWED_EXTENSIONS),
                    }
                ),
                400,
            )

        # Validate time window
        if time_start and time_end:
            if time_start >= time_end:
                return jsonify({"error": "Time start must be before time end"}), 400

        # Validate numeric inputs
        if max_stores_per_chain is not None and max_stores_per_chain < 1:
            return jsonify({"error": "Max stores per chain must be at least 1"}), 400

        if min_sales_threshold is not None and min_sales_threshold < 0:
            return jsonify({"error": "Min sales threshold must be non-negative"}), 400

        # Initialize services
        routing_service = RoutingService()
        file_service = FileService()

        # Process the uploaded file
        try:
            stores = file_service.process_stores_file(file)
            if not stores:
                return jsonify({"error": "No valid stores found in file"}), 400
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return jsonify({"error": "Failed to process file", "details": str(e)}), 400

        # Build route generation parameters
        params = {
            "proximity": proximity,
            "time_start": time_start,
            "time_end": time_end,
            "priority_only": priority_only,
            "exclude_days": exclude_days,
            "max_stores_per_chain": max_stores_per_chain,
            "min_sales_threshold": min_sales_threshold,
        }

        # Generate route
        try:
            route_result = routing_service.generate_route_with_filters(stores, params)
            logger.info(
                f"Route generated successfully with {len(route_result) if route_result else 0} stops"
            )

            return (
                jsonify(
                    {
                        "message": "Route generated successfully",
                        "route": route_result,
                        "filters_applied": {
                            "proximity": proximity,
                            "time_window": (
                                f"{time_start} - {time_end}"
                                if time_start and time_end
                                else None
                            ),
                            "priority_only": priority_only,
                            "exclude_days": exclude_days,
                            "max_stores_per_chain": max_stores_per_chain,
                            "min_sales_threshold": min_sales_threshold,
                        },
                    }
                ),
                200,
            )

        except Exception as e:
            logger.error(f"Error generating route: {str(e)}")
            return (
                jsonify({"error": "Failed to generate route", "details": str(e)}),
                500,
            )

    except Exception as e:
        logger.error(f"Unexpected error in route generation: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@main_bp.route("/api/generate", methods=["POST"])
@limiter.limit("10 per minute")
def generate_route_api():
    """
    Enhanced route generation API with comprehensive filtering
    """
    try:
        # Initialize services
        routing_service = RoutingService()
        file_service = FileService()

        # Parse and validate request
        try:
            route_request = RouteRequest.from_request(request)
        except Exception as e:
            if "413" in str(e) or "Request Entity Too Large" in str(e):
                return (
                    jsonify(
                        {
                            "error": "File size too large",
                            "details": "Maximum file size is 16MB",
                        }
                    ),
                    413,
                )
            logger.error(f"Error parsing route request: {str(e)}")
            return jsonify({"error": "Invalid request format", "details": str(e)}), 400

        # Validate request
        validation_errors = route_request.validate()
        if validation_errors:
            return (
                jsonify({"error": "Validation failed", "details": validation_errors}),
                400,
            )

        # Process file upload if provided
        stores = []
        if route_request.file:
            try:
                stores = file_service.process_stores_file(route_request.file)
            except Exception as e:
                logger.error(f"Error processing stores file: {str(e)}")
                return (
                    jsonify({"error": "File processing failed", "details": str(e)}),
                    400,
                )
        elif route_request.stores:
            stores = route_request.stores
        else:
            return (
                jsonify(
                    {
                        "error": "No stores provided",
                        "details": "Either file upload or stores data required",
                    }
                ),
                400,
            )

        if not stores:
            return (
                jsonify(
                    {
                        "error": "No valid stores found",
                        "details": "File contains no processable store data",
                    }
                ),
                400,
            )

        # Generate route with constraints
        try:
            route = routing_service.generate_route(
                stores=stores,
                playbook=route_request.playbook or {},
                algorithm=route_request.algorithm,
                user_id=getattr(route_request, "user_id", None),
            )
        except Exception as e:
            logger.error(f"Error generating route: {str(e)}")
            return jsonify({"error": "Route generation failed", "details": str(e)}), 500

        # Get metrics if available
        metrics = routing_service.get_metrics()

        # Prepare response
        response_data = {
            "success": True,
            "route": route,
            "total_stores": len(route) if route else 0,
            "filters_applied": route_request.get_filters_summary(),
            "processing_time": (
                getattr(metrics, "processing_time", None) if metrics else None
            ),
            "optimization_score": (
                getattr(metrics, "optimization_score", None) if metrics else None
            ),
        }

        if metrics and hasattr(metrics, "algorithm_metrics"):
            response_data["algorithm_metrics"] = metrics.algorithm_metrics

        logger.info(f"Route generated successfully: {len(route) if route else 0} stops")
        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Unexpected error in route generation: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "details": "An unexpected error occurred during route generation",
                }
            ),
            500,
        )


@main_bp.route("/api/export", methods=["POST"])
@limiter.limit("5 per minute")
def export_route():
    """Export generated route to CSV format"""
    try:
        # Get route data from request
        data = request.get_json()
        if not data or "route" not in data:
            return jsonify({"error": "No route data provided"}), 400

        route = data["route"]
        if not route:
            return jsonify({"error": "Empty route provided"}), 400

        # Generate CSV
        output = io.StringIO()
        if route and len(route) > 0:
            # Get all possible fieldnames from all stores
            fieldnames = set()
            for store in route:
                fieldnames.update(store.keys())
            fieldnames = sorted(list(fieldnames))

            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(route)
        else:
            output.write("No route data to export\n")

        # Prepare response
        output.seek(0)
        filename = f"routeforce_route_{len(route)}_stores.csv"

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except Exception as e:
        logger.error(f"Error exporting route: {str(e)}")
        return jsonify({"error": "Export failed", "details": str(e)}), 500


@main_bp.route("/api/upload/validate", methods=["POST"])
def validate_upload():
    """Validate uploaded file without processing"""
    try:
        file = request.files.get("file")
        if not file or file.filename == "":
            return jsonify({"error": "No file provided"}), 400

        if not allowed_file(file.filename):
            return (
                jsonify(
                    {
                        "error": "Invalid file type",
                        "allowed_types": list(ALLOWED_EXTENSIONS),
                    }
                ),
                400,
            )

        # Initialize file service and validate
        file_service = FileService()
        validation_result = file_service.validate_file(file)

        return jsonify(validation_result), 200

    except Exception as e:
        logger.error(f"Error validating file: {str(e)}")
        return jsonify({"error": "Validation failed", "details": str(e)}), 500


@main_bp.route("/api/algorithms", methods=["GET"])
def get_available_algorithms():
    """Get list of available routing algorithms"""
    try:
        routing_service = RoutingService()
        algorithms = routing_service.get_available_algorithms()

        return jsonify({"algorithms": algorithms, "default": "genetic"}), 200

    except Exception as e:
        logger.error(f"Error getting algorithms: {str(e)}")
        return jsonify({"error": "Failed to get algorithms"}), 500


@main_bp.route("/api/v1/validate_playbook", methods=["POST"])
@limiter.limit("10 per minute")
def validate_playbook_constraints():
    """Validate playbook constraint structure and content"""
    try:
        playbook_file = request.files.get("playbook")
        if not playbook_file or playbook_file.filename == "":
            return jsonify({"error": "Missing playbook file"}), 400

        # Initialize file service for validation
        file_service = FileService()

        try:
            # Use file service to validate playbook
            validation_result = file_service.validate_playbook_file(playbook_file)
            return jsonify(validation_result), (
                200 if validation_result.get("valid") else 400
            )

        except Exception as e:
            logger.error(f"Playbook validation failed: {e}")
            return (
                jsonify(
                    {"valid": False, "error": "Validation error", "details": str(e)}
                ),
                400,
            )

    except Exception as e:
        logger.error(f"Unexpected error in playbook validation: {e}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@main_bp.route("/api/route/progress/<task_id>")
def route_progress(task_id):
    """Get route generation progress for real-time updates"""
    try:
        # Simulated progress tracking (in production, this would use Redis or database)
        progress = {
            "task_id": task_id,
            "status": "processing",
            "progress": 75,
            "current_step": "Optimizing route order",
            "total_steps": 5,
            "completed_steps": 3,
            "estimated_time_remaining": "30 seconds",
            "message": "Applying genetic algorithm optimization...",
        }
        return jsonify(progress)
    except Exception as e:
        logger.error(f"Error getting route progress: {str(e)}")
        return jsonify({"error": "Failed to get progress"}), 500


@main_bp.route("/api/route/history")
def route_history():
    """Get user's route generation history"""
    try:
        # Mock route history (in production, this would come from database)
        history = [
            {
                "id": "route_001",
                "timestamp": "2025-07-22T10:30:00Z",
                "stores_count": 25,
                "optimization_type": "genetic_algorithm",
                "total_distance": "142.5 km",
                "estimated_time": "3.2 hours",
                "status": "completed",
            },
            {
                "id": "route_002",
                "timestamp": "2025-07-22T09:15:00Z",
                "stores_count": 18,
                "optimization_type": "simulated_annealing",
                "total_distance": "98.3 km",
                "estimated_time": "2.1 hours",
                "status": "completed",
            },
        ]
        return jsonify({"routes": history, "total_count": len(history)})
    except Exception as e:
        logger.error(f"Error getting route history: {str(e)}")
        return jsonify({"error": "Failed to get history"}), 500


@main_bp.route("/api/route/save", methods=["POST"])
def save_route_configuration():
    """Save route configuration for later use"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Mock save operation
        config_id = f"config_{int(time.time())}"
        saved_config = {
            "id": config_id,
            "name": data.get("name", "Untitled Configuration"),
            "settings": data.get("settings", {}),
            "created_at": "2025-07-22T10:30:00Z",
            "user_id": "demo_user",
        }

        return jsonify(
            {"message": "Configuration saved successfully", "config": saved_config}
        )
    except Exception as e:
        logger.error(f"Error saving route configuration: {str(e)}")
        return jsonify({"error": "Failed to save configuration"}), 500


@main_bp.route("/api/analytics/stats")
def analytics_stats():
    """Return live analytics stats for dashboard card"""
    # Example stats; replace with real queries as needed
    stats = {
        "total_routes": 1245,
        "active_users": 37,
        "avg_optimization_time": 2.3
    }
    return jsonify(stats)


# Legacy route support for backward compatibility
@main_bp.route("/upload", methods=["POST"])
def legacy_upload():
    """Legacy upload endpoint - redirects to new API"""
    return generate_route_api()


@main_bp.route("/export", methods=["POST"])
def legacy_export():
    """Legacy export endpoint - redirects to new API"""
    return export_route()


@main_bp.route("/app")
def react_app():
    """Serve React application for integrated dashboard access"""
    try:
        # Serve React build from Flask
        import os

        build_path = os.path.join(
            current_app.root_path, "..", "frontend", "dist", "index.html"
        )
        if os.path.exists(build_path):
            return send_file(build_path)
        else:
            # Fallback to redirect to external React app
            logger.warning("React build not found, redirecting to external app")
            return redirect("https://app.routeforcepro.com")
    except Exception as e:
        logger.error(f"Error serving React app: {str(e)}")
        return redirect("https://app.routeforcepro.com")


@main_bp.route("/app/<path:filename>")
def react_static(filename):
    """Serve React static files"""
    try:
        import os

        static_dir = os.path.join(current_app.root_path, "..", "frontend", "dist")
        file_path = os.path.join(static_dir, filename)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            logger.warning(f"React static file not found: {filename}")
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        logger.error(f"Error serving React static file {filename}: {str(e)}")
        return jsonify({"error": "File not found"}), 404


@main_bp.route("/api/health")
def api_health():
    """API Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "service": "RouteForce API",
            "version": "1.0.0",
            "timestamp": "2025-07-22",
        }
    )
