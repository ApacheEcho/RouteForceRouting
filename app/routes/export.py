"""
Data Export API endpoints
"""

from flask import Blueprint, jsonify

export_bp = Blueprint("export", __name__, url_prefix="/api/export")


@export_bp.route("/routes", methods=["GET"])
def export_routes():
    """Simple routes export stub (JSON).

    Intended for integration tests; replace with real export logic or
    integrate with a reporting service as needed.
    """
    data = {
        "routes": [],
        "count": 0,
        "format": "json",
    }
    return jsonify(data), 200
