"""
Voice Dashboard Route
Serves the voice-to-code integration dashboard
"""

from flask import Blueprint, render_template, current_app

voice_dashboard_bp = Blueprint("voice_dashboard", __name__)


@voice_dashboard_bp.route("/voice-dashboard")
def voice_dashboard():
    """
    Serve the Voice Dashboard page
    """
    return render_template(
        "voice_dashboard.html",
        title="Voice-to-Code Dashboard",
        description="Maximize productivity with voice coding tools",
    )
