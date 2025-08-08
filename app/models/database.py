"""
Database models for RouteForce Routing
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
from typing import Dict, Any, List, Optional
from sqlalchemy import Index

db = SQLAlchemy()
migrate = Migrate()


class User(db.Model):
    """User model for authentication and preferences"""

    __tablename__ = "users"
    __table_args__ = (
        Index("idx_users_username", "username"),
        Index("idx_users_email", "email"),
        Index("idx_users_created_at", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(20), default="user")  # admin, manager, user, driver
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_login = db.Column(db.DateTime)

    # Relationships
    routes = db.relationship("Route", backref="user", lazy=True)
    stores = db.relationship("Store", backref="user", lazy=True)

    def set_password(self, password: str):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }


class Store(db.Model):
    """Store model for store locations and metadata"""

    __tablename__ = "stores"
    __table_args__ = (
        Index("idx_stores_name", "name"),
        Index("idx_stores_chain", "chain"),
        Index("idx_stores_user_id", "user_id"),
        Index("idx_stores_is_active", "is_active"),
        Index("idx_stores_created_at", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    chain = db.Column(db.String(100), nullable=True)
    store_type = db.Column(db.String(50), nullable=True)
    priority = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    store_metadata = db.Column(
        db.Text, nullable=True
    )  # JSON string for additional data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    def set_metadata(self, metadata: Dict[str, Any]):
        """Set metadata as JSON string"""
        self.store_metadata = json.dumps(metadata)

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata as dictionary"""
        if self.store_metadata:
            try:
                return json.loads(self.store_metadata)
            except json.JSONDecodeError:
                return {}
        return {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert store to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "chain": self.chain,
            "store_type": self.store_type,
            "priority": self.priority,
            "is_active": self.is_active,
            "store_metadata": self.get_metadata(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Route(db.Model):
    """Route model for route history and metadata"""

    __tablename__ = "routes"
    __table_args__ = (
        Index("idx_routes_user_id", "user_id"),
        Index("idx_routes_created_at", "created_at"),
        Index("idx_routes_status", "status"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    route_data = db.Column(db.Text, nullable=False)  # JSON string of route
    total_distance = db.Column(db.Float, nullable=True)
    estimated_time = db.Column(db.Integer, nullable=True)  # Minutes
    optimization_score = db.Column(db.Float, nullable=True)
    algorithm_used = db.Column(db.String(50), nullable=True)
    status = db.Column(
        db.String(20), default="generated"
    )  # generated, in_progress, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Relationships
    optimizations = db.relationship("RouteOptimization", backref="route", lazy=True)

    def set_route_data(self, route_data: List[Dict[str, Any]]):
        """Set route data as JSON string"""
        self.route_data = json.dumps(route_data)

    def get_route_data(self) -> List[Dict[str, Any]]:
        """Get route data as list of dictionaries"""
        if self.route_data:
            try:
                return json.loads(self.route_data)
            except json.JSONDecodeError:
                return []
        return []

    def to_dict(self) -> Dict[str, Any]:
        """Convert route to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "route_data": self.get_route_data(),
            "total_distance": self.total_distance,
            "estimated_time": self.estimated_time,
            "optimization_score": self.optimization_score,
            "algorithm_used": self.algorithm_used,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class RouteOptimization(db.Model):
    """Route optimization metrics and performance data"""

    __tablename__ = "route_optimizations"
    __table_args__ = (
        Index("idx_routeopt_route_id", "route_id"),
        Index("idx_routeopt_user_id", "user_id"),
        Index("idx_routeopt_created_at", "created_at"),
        Index("idx_routeopt_algorithm", "algorithm"),
    )

    id = db.Column(db.Integer, primary_key=True)
    execution_time = db.Column(db.Float, nullable=False)  # Seconds
    algorithm = db.Column(db.String(50), nullable=False)
    parameters = db.Column(db.Text, nullable=True)  # JSON string
    improvement_score = db.Column(db.Float, nullable=True)
    original_distance = db.Column(db.Float, nullable=True)
    optimized_distance = db.Column(db.Float, nullable=True)
    stores_count = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    route_id = db.Column(db.Integer, db.ForeignKey("routes.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    def set_parameters(self, parameters: Dict[str, Any]):
        """Set parameters as JSON string"""
        self.parameters = json.dumps(parameters)

    def get_parameters(self) -> Dict[str, Any]:
        """Get parameters as dictionary"""
        if self.parameters:
            try:
                return json.loads(self.parameters)
            except json.JSONDecodeError:
                return {}
        return {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert optimization to dictionary"""
        return {
            "id": self.id,
            "execution_time": self.execution_time,
            "algorithm": self.algorithm,
            "parameters": self.get_parameters(),
            "improvement_score": self.improvement_score,
            "original_distance": self.original_distance,
            "optimized_distance": self.optimized_distance,
            "stores_count": self.stores_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Analytics(db.Model):
    """Analytics and usage statistics"""

    __tablename__ = "analytics"
    __table_args__ = (
        Index("idx_analytics_event_type", "event_type"),
        Index("idx_analytics_user_id", "user_id"),
        Index("idx_analytics_created_at", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(
        db.String(50), nullable=False
    )  # route_generated, user_login, etc.
    event_data = db.Column(db.Text, nullable=True)  # JSON string
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    session_id = db.Column(db.String(100), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_event_data(self, event_data: Dict[str, Any]):
        """Set event data as JSON string"""
        self.event_data = json.dumps(event_data)

    def get_event_data(self) -> Dict[str, Any]:
        """Get event data as dictionary"""
        if self.event_data:
            try:
                return json.loads(self.event_data)
            except json.JSONDecodeError:
                return {}
        return {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert analytics to dictionary"""
        return {
            "id": self.id,
            "event_type": self.event_type,
            "event_data": self.get_event_data(),
            "user_id": self.user_id,
            "session_id": self.session_id,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
