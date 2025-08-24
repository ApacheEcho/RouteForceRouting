"""
Enhanced Dashboard for RouteForce Routing
Advanced analytics and algorithm comparison dashboard
"""

import logging
import time
from datetime import datetime

from flask import Blueprint, jsonify, render_template, request, session

from app.services.routing_service import RoutingService

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():
    """Enhanced dashboard with algorithm comparison"""
    return render_template("dashboard/enhanced_dashboard.html")


@dashboard_bp.route("/dashboard/api/algorithms/compare", methods=["POST"])
def compare_algorithms():
    """Compare performance of different algorithms"""
    try:
        data = request.get_json()
        stores = data.get("stores", [])

        if not stores:
            return jsonify({"error": "No stores provided"}), 400

        # Get current user
        user_id = session.get("user_id")

        # Algorithms to compare
        algorithms = [
            {"name": "Default", "algorithm": "default"},
            {"name": "Genetic Algorithm", "algorithm": "genetic"},
            {"name": "Simulated Annealing", "algorithm": "simulated_annealing"},
            {"name": "Multi-Objective", "algorithm": "multi_objective"},
        ]

        results = []

        for algo in algorithms:
            try:
                routing_service = RoutingService(user_id=user_id)

                start_time = time.time()
                route = routing_service.generate_route(stores, {}, algo["algorithm"])
                processing_time = time.time() - start_time

                # Get metrics
                metrics = routing_service.get_metrics()

                result = {
                    "algorithm": algo["name"],
                    "algorithm_key": algo["algorithm"],
                    "success": True,
                    "processing_time": processing_time,
                    "route_length": len(route),
                    "optimization_score": metrics.optimization_score if metrics else 0,
                    "metrics": metrics.__dict__ if metrics else {},
                }

                # Extract algorithm-specific metrics
                if metrics and metrics.algorithm_metrics:
                    result["improvement_percent"] = metrics.algorithm_metrics.get(
                        "improvement_percent", 0
                    )
                    result["initial_distance"] = metrics.algorithm_metrics.get(
                        "initial_distance", 0
                    )
                    result["final_distance"] = metrics.algorithm_metrics.get(
                        "final_distance", 0
                    )
                else:
                    result["improvement_percent"] = 0
                    result["initial_distance"] = 0
                    result["final_distance"] = 0

                results.append(result)

            except Exception as e:
                logger.error(f"Error running {algo['name']}: {str(e)}")
                results.append(
                    {
                        "algorithm": algo["name"],
                        "algorithm_key": algo["algorithm"],
                        "success": False,
                        "error": str(e),
                    }
                )

        return jsonify(
            {
                "success": True,
                "results": results,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error in algorithm comparison: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@dashboard_bp.route("/dashboard/api/performance/history", methods=["GET"])
def get_performance_history():
    """Get historical performance data"""
    try:
        user_id = session.get("user_id")

        # Mock historical data for now
        # In a real implementation, this would come from the database
        history = [
            {
                "date": "2025-07-15",
                "genetic": {"avg_improvement": 8.5, "avg_time": 1.2},
                "simulated_annealing": {"avg_improvement": 24.2, "avg_time": 0.03},
                "multi_objective": {"avg_improvement": 15.8, "avg_time": 2.1},
                "default": {"avg_improvement": 0, "avg_time": 0.1},
            },
            {
                "date": "2025-07-16",
                "genetic": {"avg_improvement": 9.1, "avg_time": 1.3},
                "simulated_annealing": {"avg_improvement": 25.1, "avg_time": 0.02},
                "multi_objective": {"avg_improvement": 16.2, "avg_time": 2.0},
                "default": {"avg_improvement": 0, "avg_time": 0.1},
            },
            {
                "date": "2025-07-17",
                "genetic": {"avg_improvement": 9.5, "avg_time": 1.4},
                "simulated_annealing": {"avg_improvement": 26.0, "avg_time": 0.02},
                "multi_objective": {"avg_improvement": 17.1, "avg_time": 1.9},
                "default": {"avg_improvement": 0, "avg_time": 0.1},
            },
        ]

        return jsonify({"success": True, "history": history})

    except Exception as e:
        logger.error(f"Error getting performance history: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@dashboard_bp.route("/dashboard/api/algorithm/details/<algorithm>", methods=["GET"])
def get_algorithm_details(algorithm):
    """Get detailed information about a specific algorithm"""
    try:
        algorithm_info = {
            "genetic": {
                "name": "Genetic Algorithm",
                "description": "Evolution-based optimization using selection, crossover, and mutation",
                "best_for": "Complex routes with many stores (15+ locations)",
                "parameters": {
                    "population_size": {"default": 100, "range": [20, 500]},
                    "generations": {"default": 500, "range": [50, 2000]},
                    "mutation_rate": {"default": 0.02, "range": [0.001, 0.1]},
                    "crossover_rate": {"default": 0.8, "range": [0.1, 1.0]},
                },
                "performance": {
                    "avg_improvement": "5-15%",
                    "avg_time": "1-3 seconds",
                    "consistency": "High",
                },
            },
            "simulated_annealing": {
                "name": "Simulated Annealing",
                "description": "Temperature-based optimization with probabilistic acceptance",
                "best_for": "Quick optimization with excellent results",
                "parameters": {
                    "initial_temperature": {"default": 1000.0, "range": [100, 10000]},
                    "cooling_rate": {"default": 0.95, "range": [0.8, 0.99]},
                    "cooling_schedule": {
                        "default": "exponential",
                        "options": ["exponential", "linear", "logarithmic"],
                    },
                    "neighborhood_operator": {
                        "default": "swap",
                        "options": ["swap", "insert", "reverse", "mixed"],
                    },
                },
                "performance": {
                    "avg_improvement": "20-30%",
                    "avg_time": "0.01-0.05 seconds",
                    "consistency": "Very High",
                },
            },
            "multi_objective": {
                "name": "Multi-Objective Optimization",
                "description": "NSGA-II based optimization for multiple competing objectives",
                "best_for": "Complex scenarios with multiple optimization goals",
                "parameters": {
                    "objectives": {
                        "default": "distance,time",
                        "options": ["distance", "time", "priority", "fuel_cost"],
                    },
                    "population_size": {"default": 100, "range": [20, 500]},
                    "generations": {"default": 200, "range": [50, 1000]},
                    "mutation_rate": {"default": 0.1, "range": [0.01, 0.5]},
                },
                "performance": {
                    "avg_improvement": "10-20%",
                    "avg_time": "1.5-3 seconds",
                    "consistency": "High",
                },
            },
            "default": {
                "name": "Default Algorithm",
                "description": "Baseline nearest-neighbor with local optimization",
                "best_for": "Quick results and baseline comparison",
                "parameters": {
                    "optimization_level": {
                        "default": "medium",
                        "options": ["low", "medium", "high"],
                    }
                },
                "performance": {
                    "avg_improvement": "0%",
                    "avg_time": "0.05-0.1 seconds",
                    "consistency": "Perfect",
                },
            },
        }

        if algorithm not in algorithm_info:
            return jsonify({"error": "Algorithm not found"}), 404

        return jsonify({"success": True, "algorithm": algorithm_info[algorithm]})

    except Exception as e:
        logger.error(f"Error getting algorithm details: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@dashboard_bp.route("/dashboard/api/system/status", methods=["GET"])
def get_system_status():
    """Get current system status and statistics"""
    try:
        # Get system statistics
        stats = {
            "total_routes_optimized": 1247,  # Mock data
            "total_distance_saved": 3841.5,  # km
            "total_time_saved": 127.3,  # hours
            "avg_improvement": 18.7,  # percent
            "algorithms_available": 4,
            "api_endpoints": 16,
            "uptime": "7 days, 14 hours",
            "status": "healthy",
        }

        # Get current performance
        performance = {
            "cpu_usage": 23.5,  # percent
            "memory_usage": 456.2,  # MB
            "request_rate": 45.2,  # requests/minute
            "avg_response_time": 0.08,  # seconds
            "error_rate": 0.02,  # percent
        }

        # Get recent activity
        recent_activity = [
            {
                "timestamp": "2025-07-18T13:45:23Z",
                "type": "optimization",
                "algorithm": "simulated_annealing",
                "improvement": 24.3,
                "stores": 8,
            },
            {
                "timestamp": "2025-07-18T13:43:15Z",
                "type": "optimization",
                "algorithm": "genetic",
                "improvement": 12.1,
                "stores": 15,
            },
            {
                "timestamp": "2025-07-18T13:41:07Z",
                "type": "optimization",
                "algorithm": "multi_objective",
                "improvement": 18.9,
                "stores": 12,
            },
        ]

        return jsonify(
            {
                "success": True,
                "statistics": stats,
                "performance": performance,
                "recent_activity": recent_activity,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
