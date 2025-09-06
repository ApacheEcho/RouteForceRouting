"""
Database service for RouteForce Routing
"""

from typing import List, Dict, Any, Optional
from flask import current_app
from sqlalchemy import func, desc
from app.models.database import (
    db,
    User,
    Store,
    Route,
    RouteOptimization,
    Analytics,
    Connection,
)
import logging

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations"""

    @staticmethod
    def create_user(
        username: str, email: str, password: str, **kwargs
    ) -> User:
        """Create a new user"""
        try:
            user = User(
                username=username,
                email=email,
                first_name=kwargs.get("first_name"),
                last_name=kwargs.get("last_name"),
                role=kwargs.get("role", "user"),
            )
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            logger.info(f"Created new user: {username}")
            return user

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating user {username}: {e}")
            raise

    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """Get user by username"""
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID"""
        return User.query.get(user_id)

    @staticmethod
    def create_store(name: str, **kwargs) -> Store:
        """Create a new store"""
        try:
            store = Store(
                name=name,
                address=kwargs.get("address"),
                latitude=kwargs.get("latitude"),
                longitude=kwargs.get("longitude"),
                chain=kwargs.get("chain"),
                store_type=kwargs.get("store_type"),
                priority=kwargs.get("priority", 1),
                user_id=kwargs.get("user_id"),
            )

            if kwargs.get("metadata"):
                store.set_metadata(kwargs["metadata"])

            db.session.add(store)
            db.session.commit()

            logger.info(f"Created new store: {name}")
            return store

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating store {name}: {e}")
            raise

    @staticmethod
    def get_stores_by_user(user_id: int) -> List[Store]:
        """Get stores by user ID"""
        return Store.query.filter_by(user_id=user_id, is_active=True).all()

    @staticmethod
    def get_all_stores() -> List[Store]:
        """Get all active stores"""
        return Store.query.filter_by(is_active=True).all()

    @staticmethod
    def get_store_by_id(store_id: int) -> Optional[Store]:
        """Get store by ID"""
        return Store.query.get(store_id)

    @staticmethod
    def create_route(route_data: List[Dict[str, Any]], **kwargs) -> Route:
        """Create a new route"""
        try:
            route = Route(
                name=kwargs.get("name"),
                description=kwargs.get("description"),
                total_distance=kwargs.get("total_distance"),
                estimated_time=kwargs.get("estimated_time"),
                optimization_score=kwargs.get("optimization_score"),
                algorithm_used=kwargs.get("algorithm_used"),
                user_id=kwargs.get("user_id"),
            )

            route.set_route_data(route_data)

            db.session.add(route)
            db.session.commit()

            logger.info(f"Created new route: {route.id}")
            return route

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating route: {e}")
            raise

    @staticmethod
    def get_route_by_id(route_id: int) -> Optional[Route]:
        """Get route by ID"""
        return Route.query.get(route_id)

    @staticmethod
    def get_routes_by_user(user_id: int, limit: int = 10) -> List[Route]:
        """Get routes by user ID with limit"""
        return (
            Route.query.filter_by(user_id=user_id)
            .order_by(Route.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def create_route_optimization(
        route_id: int, **kwargs
    ) -> RouteOptimization:
        """Create route optimization record"""
        try:
            optimization = RouteOptimization(
                route_id=route_id,
                execution_time=kwargs.get("execution_time"),
                algorithm=kwargs.get("algorithm"),
                improvement_score=kwargs.get("improvement_score"),
                original_distance=kwargs.get("original_distance"),
                optimized_distance=kwargs.get("optimized_distance"),
                stores_count=kwargs.get("stores_count"),
                user_id=kwargs.get("user_id"),
            )

            if kwargs.get("parameters"):
                optimization.set_parameters(kwargs["parameters"])

            db.session.add(optimization)
            db.session.commit()

            logger.info(f"Created optimization record for route {route_id}")
            return optimization

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating optimization record: {e}")
            raise

    @staticmethod
    def log_analytics_event(event_type: str, **kwargs) -> Analytics:
        """Log analytics event"""
        try:
            analytics = Analytics(
                event_type=event_type,
                user_id=kwargs.get("user_id"),
                session_id=kwargs.get("session_id"),
                ip_address=kwargs.get("ip_address"),
                user_agent=kwargs.get("user_agent"),
            )

            if kwargs.get("event_data"):
                analytics.set_event_data(kwargs["event_data"])

            db.session.add(analytics)
            db.session.commit()

            return analytics

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error logging analytics event {event_type}: {e}")
            raise

    @staticmethod
    def get_analytics_summary(days: int = 30) -> Dict[str, Any]:
        """Get analytics summary for the last N days"""
        try:
            from datetime import datetime, timedelta

            start_date = datetime.utcnow() - timedelta(days=days)

            # Total events
            total_events = Analytics.query.filter(
                Analytics.created_at >= start_date
            ).count()

            # Events by type
            events_by_type = (
                db.session.query(
                    Analytics.event_type,
                    func.count(Analytics.id).label("count"),
                )
                .filter(Analytics.created_at >= start_date)
                .group_by(Analytics.event_type)
                .all()
            )

            # Active users
            active_users = (
                db.session.query(
                    func.count(func.distinct(Analytics.user_id)).label("count")
                )
                .filter(
                    Analytics.created_at >= start_date,
                    Analytics.user_id.isnot(None),
                )
                .scalar()
            )

            # Routes generated
            routes_generated = Route.query.filter(
                Route.created_at >= start_date
            ).count()

            return {
                "total_events": total_events,
                "events_by_type": {
                    event_type: count for event_type, count in events_by_type
                },
                "active_users": active_users or 0,
                "routes_generated": routes_generated,
                "period_days": days,
            }

        except Exception as e:
            logger.error(f"Error getting analytics summary: {e}")
            return {}

    # === Connections ===
    @staticmethod
    def get_connections_for_user(user_id: int) -> Dict[str, Any]:
        try:
            conns = Connection.query.filter_by(user_id=user_id).all()
            return {c.provider: c.to_dict() for c in conns}
        except Exception as e:
            logger.error(f"Error loading connections for user {user_id}: {e}")
            return {}

    @staticmethod
    def upsert_connection(user_id: int, provider: str, *, connected: bool, auth_type: str | None = None, config: Dict[str, Any] | None = None) -> Connection:
        try:
            conn = Connection.query.filter_by(user_id=user_id, provider=provider).first()
            if not conn:
                conn = Connection(user_id=user_id, provider=provider)
                db.session.add(conn)
            conn.connected = connected
            if auth_type:
                conn.auth_type = auth_type
            if config is not None:
                conn.set_config(config)
            db.session.commit()
            return conn
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error upserting connection {provider} for {user_id}: {e}")
            raise

    @staticmethod
    def get_performance_metrics() -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            # Average optimization time
            avg_optimization_time = db.session.query(
                func.avg(RouteOptimization.execution_time).label("avg_time")
            ).scalar()

            # Total routes optimized
            total_routes = Route.query.count()

            # Average improvement score
            avg_improvement = db.session.query(
                func.avg(RouteOptimization.improvement_score).label(
                    "avg_improvement"
                )
            ).scalar()

            # Most used algorithm
            most_used_algorithm = (
                db.session.query(
                    RouteOptimization.algorithm,
                    func.count(RouteOptimization.id).label("count"),
                )
                .group_by(RouteOptimization.algorithm)
                .order_by(desc("count"))
                .first()
            )

            return {
                "avg_optimization_time": (
                    float(avg_optimization_time)
                    if avg_optimization_time
                    else 0
                ),
                "total_routes": total_routes,
                "avg_improvement_score": (
                    float(avg_improvement) if avg_improvement else 0
                ),
                "most_used_algorithm": (
                    most_used_algorithm[0] if most_used_algorithm else None
                ),
            }

        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}

    @staticmethod
    def bulk_create_stores(
        stores_data: List[Dict[str, Any]], user_id: Optional[int] = None
    ) -> List[Store]:
        """Bulk create stores from data"""
        try:
            stores = []
            for store_data in stores_data:
                store = Store(
                    name=store_data.get("name", ""),
                    address=store_data.get("address"),
                    latitude=store_data.get("latitude"),
                    longitude=store_data.get("longitude"),
                    chain=store_data.get("chain"),
                    store_type=store_data.get("store_type"),
                    priority=store_data.get("priority", 1),
                    user_id=user_id,
                )

                if store_data.get("metadata"):
                    store.set_metadata(store_data["metadata"])

                stores.append(store)

            db.session.add_all(stores)
            db.session.commit()

            logger.info(f"Bulk created {len(stores)} stores")
            return stores

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error bulk creating stores: {e}")
            raise
