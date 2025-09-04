"""
Route Scoring API endpoints
Provides REST API for route scoring functionality
"""

import logging
from typing import Any, Dict, List

from flask import Blueprint, jsonify, request

from app.services.route_scoring_service import (
    PRESET_WEIGHTS,
    ScoringWeights,
    create_route_scorer,
    create_route_scorer_preset,
)

logger = logging.getLogger(__name__)
scoring_bp = Blueprint("scoring", __name__, url_prefix="/api/route")


def _validate_location(item: Dict[str, Any]) -> List[str]:
    errors = []
    if not isinstance(item, dict):
        return ["Each route item must be an object"]
    if "lat" not in item or "lon" not in item:
        errors.append("Each item requires 'lat' and 'lon'")
    else:
        try:
            float(item["lat"])
            float(item["lon"])
        except Exception:
            errors.append("'lat' and 'lon' must be numbers")
    if "priority" in item and not isinstance(item["priority"], (int, float)):
        errors.append("'priority' must be a number if provided")
    return errors


def _validate_weights(weights: Dict[str, Any]) -> List[str]:
    allowed = {
        "distance_weight",
        "time_weight",
        "priority_weight",
        "traffic_weight",
        "playbook_weight",
        "efficiency_weight",
    }
    errors = []
    for k, v in weights.items():
        if k not in allowed:
            errors.append(f"Unknown weight: {k}")
        else:
            try:
                float(v)
            except Exception:
                errors.append(f"Weight '{k}' must be a number")
    return errors


@scoring_bp.route("/score", methods=["POST"])
def score_route():
    """
    Score a single route
    ---
    tags:
      - Routes
    summary: Score a route with weighted components
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [route]
          properties:
            route:
              type: array
              items:
                $ref: '#/definitions/RouteItem'
            context:
              type: object
            weights:
              type: object
            preset:
              type: string
              enum: [balanced, distance_focused, priority_focused, traffic_aware, playbook_strict]
    responses:
      200:
        description: Score computed
        schema:
          $ref: '#/definitions/RouteScoreResponse'
        examples:
          application/json:
            success: true
            score:
              total_score: 87.25
              component_scores: { distance: 0.92, time: 0.85, priority: 0.90, traffic: 0.78, playbook: 0.80, efficiency: 0.70 }
              raw_metrics: { total_distance_km: 12.3, total_time_h: 0.75 }
              metadata: { route_length: 5 }
              calculation_time_ms: 4.12
      400:
        description: Bad request
        schema:
          $ref: '#/definitions/ErrorResponse'
      422:
        description: Validation error
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Server error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        route = data.get("route", [])
        if not isinstance(route, list) or not route:
            return jsonify({"error": "'route' must be a non-empty list"}), 400

        # Validate route items
        all_errors: List[str] = []
        for idx, item in enumerate(route):
            errs = _validate_location(item)
            if errs:
                all_errors.extend([f"route[{idx}]: {e}" for e in errs])
        if all_errors:
            return (
                jsonify(
                    {"error": "Invalid route data", "details": all_errors}
                ),
                422,
            )

        context = data.get("context", {})

        # Create scorer with custom weights or preset
        if "weights" in data and data["weights"] is not None:
            if not isinstance(data["weights"], dict):
                return jsonify({"error": "'weights' must be an object"}), 400
            weight_errors = _validate_weights(data["weights"])
            if weight_errors:
                return (
                    jsonify(
                        {"error": "Invalid weights", "details": weight_errors}
                    ),
                    422,
                )
            weights_data = data["weights"]
            weights = ScoringWeights(**weights_data)
            scorer = create_route_scorer(weights)
        elif "preset" in data and data["preset"]:
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
    ---
    tags:
      - Routes
    summary: Compare multiple routes and return the best
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [routes]
          properties:
            routes:
              type: array
              items:
                type: array
                items:
                  $ref: '#/definitions/RouteItem'
            context:
              type: object
            preset:
              type: string
    responses:
      200:
        description: Comparison computed
        schema:
          $ref: '#/definitions/RouteCompareResponse'
        examples:
          application/json:
            success: true
            comparison:
              route_count: 2
              scores:
                - { total_score: 82.5, component_scores: { distance: 0.9 }, raw_metrics: { }, metadata: { }, calculation_time_ms: 3.2 }
                - { total_score: 78.1, component_scores: { distance: 0.85 }, raw_metrics: { }, metadata: { }, calculation_time_ms: 3.4 }
              best_route_index: 0
              best_score: 82.5
              score_range: { min: 78.1, max: 82.5, average: 80.3 }
      400:
        description: Bad request
        schema:
          $ref: '#/definitions/ErrorResponse'
      422:
        description: Validation error
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Server error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        routes = data.get("routes", [])
        if not isinstance(routes, list) or not routes:
            return jsonify({"error": "'routes' must be a non-empty list"}), 400

        # Validate each route
        all_errors: List[str] = []
        for r_idx, route in enumerate(routes):
            if not isinstance(route, list) or not route:
                all_errors.append(f"routes[{r_idx}] must be a non-empty list")
                continue
            for i_idx, item in enumerate(route):
                errs = _validate_location(item)
                if errs:
                    all_errors.extend(
                        [f"routes[{r_idx}][{i_idx}]: {e}" for e in errs]
                    )
        if all_errors:
            return (
                jsonify(
                    {"error": "Invalid routes data", "details": all_errors}
                ),
                422,
            )

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

        return jsonify(
            {"success": True, "presets": presets, "default": "balanced"}
        )

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

        return jsonify(
            {"success": True, "history": history, "count": len(history)}
        )

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
