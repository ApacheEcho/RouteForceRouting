"""
Multi-tenant Organization Management System
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import logging

# Initialize blueprint
organizations_bp = Blueprint("organizations", __name__, url_prefix="/api/organizations")
logger = logging.getLogger(__name__)


@dataclass
class Organization:
    """Organization data model"""

    id: str
    name: str
    subdomain: str
    plan: str = "basic"
    max_users: int = 10
    max_routes: int = 1000
    is_active: bool = True
    created_at: str = None
    settings: Dict = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.settings is None:
            self.settings = {
                "analytics_enabled": True,
                "real_time_tracking": True,
                "advanced_optimization": self.plan in ["pro", "enterprise"],
                "api_access": True,
                "data_retention_days": 90 if self.plan == "basic" else 365,
                "concurrent_optimizations": 1 if self.plan == "basic" else 5,
            }


@dataclass
class User:
    """User data model with organization context"""

    id: str
    organization_id: str
    email: str
    username: str
    first_name: str
    last_name: str
    role: str = "user"  # user, admin, org_admin, super_admin
    is_active: bool = True
    permissions: List[str] = None
    last_login: str = None
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.permissions is None:
            self.permissions = self._get_default_permissions()

    def _get_default_permissions(self) -> List[str]:
        """Get default permissions based on role"""
        role_permissions = {
            "user": ["view_routes", "create_routes", "optimize_routes"],
            "admin": [
                "view_routes",
                "create_routes",
                "optimize_routes",
                "manage_users",
                "view_analytics",
            ],
            "org_admin": ["*"],  # All organization-level permissions
            "super_admin": ["**"],  # System-wide permissions
        }
        return role_permissions.get(self.role, [])


class OrganizationManager:
    """Multi-tenant organization management"""

    def __init__(self):
        self.organizations = {}
        self.users = {}
        self._init_demo_data()

    def _init_demo_data(self):
        """Initialize with demo organizations"""
        demo_orgs = [
            Organization(
                id=str(uuid.uuid4()),
                name="RouteForce Demo",
                subdomain="demo",
                plan="enterprise",
                max_users=100,
                max_routes=10000,
            ),
            Organization(
                id=str(uuid.uuid4()),
                name="Logistics Pro Inc",
                subdomain="logistics-pro",
                plan="pro",
                max_users=50,
                max_routes=5000,
            ),
            Organization(
                id=str(uuid.uuid4()),
                name="SmallFleet Solutions",
                subdomain="smallfleet",
                plan="basic",
                max_users=10,
                max_routes=500,
            ),
        ]

        for org in demo_orgs:
            self.organizations[org.id] = org

    def create_organization(self, data: Dict) -> Organization:
        """Create new organization"""
        org_id = str(uuid.uuid4())
        org = Organization(
            id=org_id,
            name=data["name"],
            subdomain=data["subdomain"],
            plan=data.get("plan", "basic"),
            max_users=data.get("max_users", 10),
            max_routes=data.get("max_routes", 1000),
        )

        self.organizations[org_id] = org
        logger.info(f"Created organization: {org.name} ({org.subdomain})")
        return org

    def get_organization(self, org_id: str) -> Optional[Organization]:
        """Get organization by ID"""
        return self.organizations.get(org_id)

    def get_organization_by_subdomain(self, subdomain: str) -> Optional[Organization]:
        """Get organization by subdomain"""
        for org in self.organizations.values():
            if org.subdomain == subdomain:
                return org
        return None

    def list_organizations(self) -> List[Organization]:
        """List all organizations"""
        return list(self.organizations.values())

    def update_organization(self, org_id: str, data: Dict) -> Optional[Organization]:
        """Update organization"""
        org = self.organizations.get(org_id)
        if not org:
            return None

        for key, value in data.items():
            if hasattr(org, key):
                setattr(org, key, value)

        logger.info(f"Updated organization: {org.name}")
        return org

    def delete_organization(self, org_id: str) -> bool:
        """Delete organization"""
        if org_id in self.organizations:
            org = self.organizations[org_id]
            org.is_active = False
            logger.info(f"Deactivated organization: {org.name}")
            return True
        return False

    def get_organization_stats(self, org_id: str) -> Dict:
        """Get organization usage statistics"""
        org = self.organizations.get(org_id)
        if not org:
            return {}

        # Get user count for this organization
        user_count = len(
            [u for u in self.users.values() if u.organization_id == org_id]
        )

        return {
            "organization_id": org_id,
            "name": org.name,
            "plan": org.plan,
            "users": {
                "current": user_count,
                "limit": org.max_users,
                "usage_percent": (user_count / org.max_users) * 100,
            },
            "routes": {
                "current": 0,  # TODO: Integrate with route system
                "limit": org.max_routes,
                "usage_percent": 0,
            },
            "settings": org.settings,
            "is_active": org.is_active,
        }


# Initialize global organization manager
org_manager = OrganizationManager()


@organizations_bp.route("/list", methods=["GET"])
@jwt_required()
def list_organizations():
    """List all organizations (super admin only)"""
    try:
        # TODO: Check super admin permissions
        orgs = org_manager.list_organizations()
        return (
            jsonify(
                {"organizations": [asdict(org) for org in orgs], "total": len(orgs)}
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error listing organizations: {str(e)}")
        return jsonify({"error": "Failed to list organizations"}), 500


@organizations_bp.route("/", methods=["POST"])
@jwt_required()
def create_organization():
    """Create new organization"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["name", "subdomain"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Check if subdomain is unique
        existing = org_manager.get_organization_by_subdomain(data["subdomain"])
        if existing:
            return jsonify({"error": "Subdomain already exists"}), 409

        org = org_manager.create_organization(data)
        return (
            jsonify(
                {
                    "organization": asdict(org),
                    "message": "Organization created successfully",
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Error creating organization: {str(e)}")
        return jsonify({"error": "Failed to create organization"}), 500


@organizations_bp.route("/<org_id>", methods=["GET"])
@jwt_required()
def get_organization(org_id):
    """Get organization details"""
    try:
        org = org_manager.get_organization(org_id)
        if not org:
            return jsonify({"error": "Organization not found"}), 404

        stats = org_manager.get_organization_stats(org_id)
        return jsonify({"organization": asdict(org), "stats": stats}), 200

    except Exception as e:
        logger.error(f"Error getting organization: {str(e)}")
        return jsonify({"error": "Failed to get organization"}), 500


@organizations_bp.route("/<org_id>", methods=["PUT"])
@jwt_required()
def update_organization(org_id):
    """Update organization"""
    try:
        data = request.get_json()
        org = org_manager.update_organization(org_id, data)

        if not org:
            return jsonify({"error": "Organization not found"}), 404

        return (
            jsonify(
                {
                    "organization": asdict(org),
                    "message": "Organization updated successfully",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error updating organization: {str(e)}")
        return jsonify({"error": "Failed to update organization"}), 500


@organizations_bp.route("/<org_id>/stats", methods=["GET"])
@jwt_required()
def get_organization_stats(org_id):
    """Get organization usage statistics"""
    try:
        stats = org_manager.get_organization_stats(org_id)
        if not stats:
            return jsonify({"error": "Organization not found"}), 404

        return jsonify(stats), 200

    except Exception as e:
        logger.error(f"Error getting organization stats: {str(e)}")
        return jsonify({"error": "Failed to get organization stats"}), 500


@organizations_bp.route("/subdomain/<subdomain>", methods=["GET"])
def get_organization_by_subdomain(subdomain):
    """Get organization by subdomain (public endpoint for tenant resolution)"""
    try:
        org = org_manager.get_organization_by_subdomain(subdomain)
        if not org or not org.is_active:
            return jsonify({"error": "Organization not found"}), 404

        # Return limited public information
        return (
            jsonify(
                {
                    "id": org.id,
                    "name": org.name,
                    "subdomain": org.subdomain,
                    "plan": org.plan,
                    "settings": {
                        "analytics_enabled": org.settings.get(
                            "analytics_enabled", False
                        ),
                        "real_time_tracking": org.settings.get(
                            "real_time_tracking", False
                        ),
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error getting organization by subdomain: {str(e)}")
        return jsonify({"error": "Failed to get organization"}), 500
