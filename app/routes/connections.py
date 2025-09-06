"""
Connections API - Manage third-party service connections (skeleton)
Supports listing providers, connection status, mock connect/disconnect,
and placeholder OAuth endpoints.
"""

from flask import Blueprint, jsonify, request, g
from typing import Dict, Any
from app.auth_decorators import auth_required
import logging
from app.services.database_service import DatabaseService
from flask_jwt_extended import get_jwt_identity

logger = logging.getLogger(__name__)

connections_bp = Blueprint("connections", __name__, url_prefix="/api/connections")

# In-memory store (skeleton). Replace with DB models in production.
# Legacy in-memory store retained for fallback only
_connections_store: Dict[str, Dict[str, Dict[str, Any]]] = {}

SUPPORTED_PROVIDERS = [
    {
        "key": "openai",
        "name": "OpenAI (ChatGPT)",
        "type": "llm",
        "auth": "api_key|oauth",
        "docs": "https://platform.openai.com/",
    },
    {
        "key": "anthropic",
        "name": "Anthropic (Claude)",
        "type": "llm",
        "auth": "api_key",
        "docs": "https://docs.anthropic.com/",
    },
    {
        "key": "google_gemini",
        "name": "Google Gemini",
        "type": "llm",
        "auth": "api_key|oauth",
        "docs": "https://ai.google.dev/",
    },
    {
        "key": "microsoft_copilot",
        "name": "Microsoft Copilot (Graph)",
        "type": "assistant",
        "auth": "oauth",
        "docs": "https://learn.microsoft.com/en-us/microsoft-copilot/",
    },
    {
        "key": "salesforce",
        "name": "Salesforce",
        "type": "crm",
        "auth": "oauth",
        "docs": "https://developer.salesforce.com/",
    },
    {
        "key": "power_bi",
        "name": "Microsoft Power BI",
        "type": "bi",
        "auth": "oauth",
        "docs": "https://learn.microsoft.com/en-us/power-bi/developer/",
    },
    {
        "key": "azure",
        "name": "Microsoft Azure",
        "type": "cloud",
        "auth": "oauth",
        "docs": "https://learn.microsoft.com/en-us/azure/",
    },
    {
        "key": "nielsen",
        "name": "Nielsen",
        "type": "data",
        "auth": "oauth|service",
        "docs": "https://developer.nielsen.com/",
    },
    {
        "key": "iri",
        "name": "IRI",
        "type": "data",
        "auth": "oauth|service",
        "docs": "https://www.iriworldwide.com/",
    },
]


def _uid() -> str:
    user = getattr(g, "current_user", None)
    if user is None:
        return "anonymous"
    # SQLAlchemy user or enterprise dict
    return str(getattr(user, "id", None) or user.get("id"))


@connections_bp.route("/providers", methods=["GET"])
@auth_required()
def list_providers():
    return jsonify({"success": True, "providers": SUPPORTED_PROVIDERS})


@connections_bp.route("/status", methods=["GET"])
@auth_required()
def get_status():
    try:
        user = getattr(g, "current_user", None)
        user_id = getattr(user, "id", None) or user.get("id")
        if not user_id:
            return jsonify({"success": False, "error": "user not resolved"}), 400
        status = DatabaseService.get_connections_for_user(int(user_id))
        # Merge legacy in-memory in case of no DB migration yet
        mem = _connections_store.get(str(user_id), {})
        status.update(mem)
        return jsonify({"success": True, "status": status})
    except Exception as e:
        logger.error(f"status error: {e}")
        return jsonify({"success": False, "error": "failed to load status"}), 500


@connections_bp.route("/connect", methods=["POST"])
@auth_required()
def connect_provider():
    data = request.get_json(silent=True) or {}
    provider = data.get("provider")
    token = data.get("token")  # api key or oauth token (placeholder)
    config = data.get("config", {})
    if not provider:
        return jsonify({"success": False, "error": "provider required"}), 400
    user = getattr(g, "current_user", None)
    user_id = getattr(user, "id", None) or user.get("id")
    if not user_id:
        return jsonify({"success": False, "error": "user not resolved"}), 400
    # Never store tokens directly; track presence only
    cfg = {**config, "has_token": bool(token)} if isinstance(config, dict) else {"has_token": bool(token)}
    conn = DatabaseService.upsert_connection(int(user_id), provider, connected=True, auth_type=("api_key" if token else None), config=cfg)
    logger.info("User %s connected provider %s", user_id, provider)
    return jsonify({"success": True, "provider": provider, "connection": conn.to_dict()})


@connections_bp.route("/disconnect", methods=["POST"])
@auth_required()
def disconnect_provider():
    data = request.get_json(silent=True) or {}
    provider = data.get("provider")
    if not provider:
        return jsonify({"success": False, "error": "provider required"}), 400
    user = getattr(g, "current_user", None)
    user_id = getattr(user, "id", None) or user.get("id")
    if not user_id:
        return jsonify({"success": False, "error": "user not resolved"}), 400
    DatabaseService.upsert_connection(int(user_id), provider, connected=False)
    return jsonify({"success": True, "provider": provider})


@connections_bp.route("/oauth/start/<provider>", methods=["GET"])
@auth_required()
def oauth_start(provider: str):
    # Placeholder: return a structured authorization URL using environment if present
    import os, urllib.parse
    client_id = os.getenv(f"{provider.upper()}_CLIENT_ID", "demo-client")
    auth_base = os.getenv(f"{provider.upper()}_AUTH_URL", "https://auth.example.com/oauth/authorize")
    redirect_uri = os.getenv("OAUTH_REDIRECT_BASE", "http://localhost:5000") + f"/api/connections/oauth/callback/{provider}"
    scope = os.getenv(f"{provider.upper()}_SCOPES", "basic")
    state = "rf_demo_state"
    params = urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scope,
        "state": state,
    })
    auth_url = f"{auth_base}?{params}"
    return jsonify({"success": True, "authorization_url": auth_url, "state": state})


@connections_bp.route("/oauth/callback/<provider>", methods=["GET"])
@auth_required()
def oauth_callback(provider: str):
    # Placeholder: mark as connected; in production, exchange code for token here
    code = request.args.get("code")
    state = request.args.get("state")
    user = getattr(g, "current_user", None)
    user_id = getattr(user, "id", None) or user.get("id")
    if not user_id:
        return jsonify({"success": False, "error": "user not resolved"}), 400
    cfg = {"oauth": True, "has_token": bool(code), "state": state}
    conn = DatabaseService.upsert_connection(int(user_id), provider, connected=True, auth_type="oauth", config=cfg)
    return jsonify({"success": True, "provider": provider, "connected": True, "connection": conn.to_dict()})
