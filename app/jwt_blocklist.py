"""
JWT Blocklist for token revocation (logout support)
"""

from flask import current_app
from flask_jwt_extended import JWTManager
from redis import Redis
import os

# Use Redis for blocklist storage
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
redis_conn = Redis.from_url(redis_url)

BLOCKLIST_KEY = "jwt_blocklist"

def add_token_to_blocklist(jti: str, exp: int):
    """Add a JWT's jti to the blocklist until its expiration."""
    redis_conn.setex(f"{BLOCKLIST_KEY}:{jti}", exp, "revoked")

def is_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    entry = redis_conn.get(f"{BLOCKLIST_KEY}:{jti}")
    return entry is not None
