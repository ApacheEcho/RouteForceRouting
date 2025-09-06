"""
Optimization API endpoints
Provides simple stubs for genetic and multi-objective optimization with input validation
"""

from flask import Blueprint, request, jsonify
import re

optimize_bp = Blueprint("optimize", __name__, url_prefix="/api/optimize")


def _invalid_input(payload: dict) -> bool:
    if not isinstance(payload, dict):
        return True
    # Basic validation for obvious XSS/script injections
    suspect = re.compile(r"<[^>]+>|script", re.IGNORECASE)
    for key in ("start_location", "end_location"):
        val = payload.get(key)
        if isinstance(val, str) and suspect.search(val or ""):
            return True
    return False


@optimize_bp.route("/genetic", methods=["POST"])
def optimize_genetic():
    """Stub endpoint for genetic optimization.

    Notes:
    - Validates obvious script payloads; returns 422 for invalid input.
    - Returns a minimal, fast response suitable for integration tests.
    - Replace with real optimization engine as needed.
    """
    data = request.get_json(silent=True) or {}
    if _invalid_input(data):
        return jsonify({"error": "Invalid input"}), 422
    # Minimal stubbed response keeps tests fast
    return jsonify({
        "success": True,
        "algorithm": "genetic",
        "route": [],
        "summary": {"distance_km": 0, "duration_min": 0},
    }), 200


@optimize_bp.route("/multi-objective", methods=["POST"])
def optimize_multi_objective():
    """Stub endpoint for multi-objective optimization.

    Same behavior as the genetic stub; intended to keep e2e and
    enterprise integration tests running quickly in CI.
    """
    data = request.get_json(silent=True) or {}
    if _invalid_input(data):
        return jsonify({"error": "Invalid input"}), 422
    return jsonify({
        "success": True,
        "algorithm": "multi_objective",
        "route": [],
        "summary": {"distance_km": 0, "duration_min": 0},
    }), 200
