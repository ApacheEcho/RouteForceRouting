"""
Route Scoring API endpoints
Provides REST API for route scoring functionality
"""

import logging

from flask import Blueprint, jsonify, request

from app.services.route_scoring_service import (
    PRESET_WEIGHTS,
    ScoringWeights,
    create_route_scorer,
    create_route_scorer_preset,
)

logger = logging.getLogger(__name__)
scoring_bp = Blueprint("scoring", __name__, url_prefix="/api/route")


@scoring_bp.route("/score", methods=["POST"])
def score_route():
    """
    Score a single route

    Expected JSON:
    {
        "route": [list of stores],
        "context": {optional context data},
        "weights": {optional custom weights},
        "preset": "balanced|distance_focused|priority_focused|traffic_aware|playbook_strict"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        route = data.get("route", [])
        if not route:
            return jsonify({"error": "Route is required"}), 400

        context = data.get("context", {})

        # Create scorer with custom weights or preset
        if "weights" in data:
            weights_data = data["weights"]
            weights = ScoringWeights(**weights_data)
            scorer = create_route_scorer(weights)
        elif "preset" in data:
            preset = data["preset"]
            if preset not in PRESET_WEIGHTS:
                return (
                    jsonify(
                        {
                            "error": f"Invalid preset. Available: {list(PRESET_WEIGHTS.keys())}"
                        }
                    ),
                    400,
                )
            scorer = create_route_scorer_preset(preset)
        else:
            scorer = create_route_scorer()  # Default balanced weights

        # Calculate score
        score = scorer.score_route(route, context)

        return jsonify({"success": True, "score": score.to_dict()})

    except Exception as e:
        logger.error(f"Error in score_route endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@scoring_bp.route("/score/compare", methods=["POST"])
def compare_routes():
    """
    Compare multiple routes

    Expected JSON:
    {
        "routes": [list of route lists],
        "context": {optional context data},
        "preset": "balanced|distance_focused|..."
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        routes = data.get("routes", [])
        if not routes:
            return jsonify({"error": "Routes list is required"}), 400

        if len(routes) < 2:
            return jsonify({"error": "At least 2 routes required for comparison"}), 400

        context = data.get("context", {})
        preset = data.get("preset", "balanced")

        if preset not in PRESET_WEIGHTS:
            return (
                jsonify(
                    {
                        "error": f"Invalid preset. Available: {list(PRESET_WEIGHTS.keys())}"
                    }
                ),
                400,
            )

        scorer = create_route_scorer_preset(preset)
        comparison = scorer.compare_routes(routes, context)

        return jsonify({"success": True, "comparison": comparison})

    except Exception as e:
        logger.error(f"Error in compare_routes endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@scoring_bp.route("/score/weights", methods=["GET"])
def get_available_weights():
    """Get available weight presets and their configurations"""
    try:
        presets = {}
        for name, weights in PRESET_WEIGHTS.items():
            presets[name] = {
                "distance_weight": weights.distance_weight,
                "time_weight": weights.time_weight,
                "priority_weight": weights.priority_weight,
                "traffic_weight": weights.traffic_weight,
                "playbook_weight": weights.playbook_weight,
                "efficiency_weight": weights.efficiency_weight,
            }

        return jsonify({"success": True, "presets": presets, "default": "balanced"})

    except Exception as e:
        logger.error(f"Error in get_available_weights endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@scoring_bp.route("/score/history", methods=["GET"])
def get_scoring_history():
    """Get recent scoring history"""
    try:
        limit = request.args.get("limit", 10, type=int)
        limit = min(max(limit, 1), 100)  # Clamp between 1 and 100

        # Get scorer from app context or create new one
        scorer = create_route_scorer()
        history = scorer.get_scoring_history(limit)

        return jsonify({"success": True, "history": history, "count": len(history)})

    except Exception as e:
        logger.error(f"Error in get_scoring_history endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@scoring_bp.route("/score/test", methods=["GET"])
def test_scoring():
    """Test endpoint with sample data"""
    try:
        # Sample route data
        sample_route = [
            {
                "name": "Store A",
                "lat": 40.7128,
                "lon": -74.0060,
                "priority": 8,
                "chain": "SuperMart",
            },
            {
                "name": "Store B",
                "lat": 40.7589,
                "lon": -73.9851,
                "priority": 6,
                "chain": "QuickShop",
            },
            {
                "name": "Store C",
                "lat": 40.7505,
                "lon": -73.9934,
                "priority": 9,
                "chain": "SuperMart",
            },
        ]

        sample_context = {
            "route_id": "test_route",
            "playbook": {
                "rules": [
                    {"type": "max_stores", "value": 10},
                    {"type": "priority_threshold", "value": 5},
                ]
            },
        }

        scorer = create_route_scorer()
        score = scorer.score_route(sample_route, sample_context)

        return jsonify(
            {
                "success": True,
                "message": "Route scoring service is working correctly",
                "sample_score": score.to_dict(),
                "sample_route": sample_route,
                "sample_context": sample_context,
            }
        )

    except Exception as e:
        logger.error(f"Error in test_scoring endpoint: {e}")
        return jsonify({"error": str(e)}), 500
