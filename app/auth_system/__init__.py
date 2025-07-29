# Re-export users_db, ROLES, and auth_manager for package imports
from app.auth_system import ROLES, auth_manager, users_db

__all__ = ["users_db", "ROLES", "auth_manager"]
