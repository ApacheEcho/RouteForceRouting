"""
JWT Blocklist for token revocation (logout support)
"""

from flask import current_app
from flask_jwt_extended import JWTManager
from redis import Redis
from redis.exceptions import RedisError
import os
from typing import Set

# Use Redis for blocklist storage
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
redis_conn = Redis.from_url(redis_url)

# In-memory fallback for test/local environments without Redis
_memory_blocklist: Set[str] = set()

BLOCKLIST_KEY = "jwt_blocklist"

def add_token_to_blocklist(jti: str, exp: int):
    """Add a JWT's jti to the blocklist until its expiration.

    Falls back to an in-memory set if Redis is unavailable.
    """
    try:
        redis_conn.setex(f"{BLOCKLIST_KEY}:{jti}", exp, "revoked")
    except Exception:  # Redis not available in tests/sandbox
        _memory_blocklist.add(jti)

def is_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    try:
        entry = redis_conn.get(f"{BLOCKLIST_KEY}:{jti}")
        return entry is not None
    except Exception:  # Redis not available
        return jti in _memory_blocklist
