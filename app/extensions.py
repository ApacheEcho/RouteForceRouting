"""
Flask extensions for RouteForce Routing
Centralized to avoid circular imports
"""


from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.models.database import db

cache = Cache()
limiter = Limiter(key_func=get_remote_address)
