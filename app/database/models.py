"""
Database Models for RouteForce Analytics
Provides persistent storage for route data, analytics, and insights
"""

import json
import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class Route(Base):
    """Route data model"""

    __tablename__ = "routes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id = Column(String(100), unique=True, nullable=False, index=True)
    distance = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)
    fuel_used = Column(Float)
    driver_id = Column(String(50))
    vehicle_type = Column(String(50))
    stops_count = Column(Integer)
    stops_data = Column(JSON)  # Store stops as JSON
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Calculated fields
    speed_avg = Column(Float)
    fuel_efficiency = Column(Float)
    hour_of_day = Column(Integer)
    day_of_week = Column(Integer)
    is_weekend = Column(Boolean)
    is_rush_hour = Column(Boolean)
    avg_stop_distance = Column(Float)

    # Relationships
    insights = relationship("RouteInsightDB", back_populates="route")
    predictions = relationship("RoutePredictionDB", back_populates="route")


class RouteInsightDB(Base):
    """Route insights model"""

    __tablename__ = "route_insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id = Column(String(100), nullable=False, index=True)
    insight_type = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    impact_score = Column(Float)
    confidence = Column(Float)
    recommendations = Column(JSON)  # Store as JSON array
    metrics = Column(JSON)  # Store metrics as JSON
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationship
    route = relationship("Route", back_populates="insights")


class RoutePredictionDB(Base):
    """Route predictions model"""

    __tablename__ = "route_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id = Column(String(100), nullable=False, index=True)
    predicted_duration = Column(Float, nullable=False)
    predicted_fuel_cost = Column(Float, nullable=False)
    confidence_interval_low = Column(Float)
    confidence_interval_high = Column(Float)
    risk_factors = Column(JSON)  # Store as JSON array
    optimization_suggestions = Column(JSON)  # Store as JSON array
    actual_duration = Column(Float)  # For validation later
    actual_fuel_cost = Column(Float)  # For validation later
    prediction_accuracy = Column(Float)  # Calculated after completion
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationship
    route = relationship("Route", back_populates="predictions")


class PerformanceTrendDB(Base):
    """Performance trends model"""

    __tablename__ = "performance_trends"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_name = Column(String(100), nullable=False, index=True)
    current_value = Column(Float, nullable=False)
    trend_direction = Column(String(20), nullable=False)  # improving, declining, stable
    change_percentage = Column(Float)
    forecast_7d = Column(Float)
    forecast_30d = Column(Float)
    timeframe_days = Column(Integer, default=30)
    calculation_timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class FleetInsightDB(Base):
    """Fleet-wide insights model"""

    __tablename__ = "fleet_insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    total_routes = Column(Integer, nullable=False)
    avg_fuel_efficiency = Column(Float)
    avg_duration_minutes = Column(Float)
    recommendations = Column(JSON)  # Store as JSON array
    insights_summary = Column(JSON)  # Store insights as JSON
    trends_summary = Column(JSON)  # Store trends as JSON
    calculation_timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class AnalyticsAlert(Base):
    """Analytics alerts model"""

    __tablename__ = "analytics_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_type = Column(String(100), nullable=False, index=True)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    metric_name = Column(String(100))
    metric_value = Column(Float)
    threshold_value = Column(Float)
    affected_routes = Column(JSON)  # Store route IDs as JSON array
    recommended_actions = Column(JSON)  # Store actions as JSON array
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100))
    acknowledged_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime)


class DatabaseManager:
    """Database manager for analytics data"""

    def __init__(
        self, database_url: str = "postgresql://user:password@localhost/routeforce"
    ):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        """Get database session"""
        return self.SessionLocal()

    def save_route_data(self, route_data: dict) -> str:
        """Save route data to database"""
        session = self.get_session()
        try:
            route = Route(
                route_id=route_data["route_id"],
                distance=route_data["distance"],
                duration=route_data["duration"],
                fuel_used=route_data.get("fuel_used"),
                driver_id=route_data.get("driver_id"),
                vehicle_type=route_data.get("vehicle_type"),
                stops_count=route_data.get("stops_count"),
                stops_data=route_data.get("stops", []),
                speed_avg=route_data.get("speed_avg"),
                fuel_efficiency=route_data.get("fuel_efficiency"),
                hour_of_day=route_data.get("hour_of_day"),
                day_of_week=route_data.get("day_of_week"),
                is_weekend=route_data.get("is_weekend", False),
                is_rush_hour=route_data.get("is_rush_hour", False),
                avg_stop_distance=route_data.get("avg_stop_distance"),
            )
            session.add(route)
            session.commit()
            return str(route.id)
        finally:
            session.close()

    def save_insight(self, insight_data: dict) -> str:
        """Save route insight to database"""
        session = self.get_session()
        try:
            insight = RouteInsightDB(
                route_id=insight_data["route_id"],
                insight_type=insight_data["insight_type"],
                title=insight_data["title"],
                description=insight_data["description"],
                impact_score=insight_data["impact_score"],
                confidence=insight_data["confidence"],
                recommendations=insight_data["recommendations"],
                metrics=insight_data["metrics"],
            )
            session.add(insight)
            session.commit()
            return str(insight.id)
        finally:
            session.close()

    def save_prediction(self, prediction_data: dict) -> str:
        """Save route prediction to database"""
        session = self.get_session()
        try:
            prediction = RoutePredictionDB(
                route_id=prediction_data["route_id"],
                predicted_duration=prediction_data["predicted_duration"],
                predicted_fuel_cost=prediction_data["predicted_fuel_cost"],
                confidence_interval_low=prediction_data["confidence_interval"][0],
                confidence_interval_high=prediction_data["confidence_interval"][1],
                risk_factors=prediction_data["risk_factors"],
                optimization_suggestions=prediction_data["optimization_suggestions"],
            )
            session.add(prediction)
            session.commit()
            return str(prediction.id)
        finally:
            session.close()

    def save_alert(self, alert_data: dict) -> str:
        """Save analytics alert to database"""
        session = self.get_session()
        try:
            alert = AnalyticsAlert(
                alert_type=alert_data["type"],
                severity=alert_data["severity"],
                title=alert_data["title"],
                message=alert_data["message"],
                metric_name=alert_data.get("metric"),
                metric_value=alert_data.get("value"),
                threshold_value=alert_data.get("threshold"),
                affected_routes=alert_data.get("routes", []),
                recommended_actions=alert_data.get("actions", []),
            )
            session.add(alert)
            session.commit()
            return str(alert.id)
        finally:
            session.close()

    def get_historical_routes(self, limit: int = 1000):
        """Get historical route data"""
        session = self.get_session()
        try:
            routes = (
                session.query(Route).order_by(Route.timestamp.desc()).limit(limit).all()
            )
            return [self._route_to_dict(route) for route in routes]
        finally:
            session.close()

    def get_unacknowledged_alerts(self):
        """Get unacknowledged alerts"""
        session = self.get_session()
        try:
            alerts = (
                session.query(AnalyticsAlert)
                .filter(AnalyticsAlert.is_acknowledged == False)
                .order_by(AnalyticsAlert.created_at.desc())
                .all()
            )
            return [self._alert_to_dict(alert) for alert in alerts]
        finally:
            session.close()

    def acknowledge_alert(self, alert_id: str, user_id: str):
        """Acknowledge an alert"""
        session = self.get_session()
        try:
            alert = (
                session.query(AnalyticsAlert)
                .filter(AnalyticsAlert.id == alert_id)
                .first()
            )
            if alert:
                alert.is_acknowledged = True
                alert.acknowledged_by = user_id
                alert.acknowledged_at = datetime.utcnow()
                session.commit()
                return True
            return False
        finally:
            session.close()

    def _route_to_dict(self, route):
        """Convert route model to dictionary"""
        return {
            "route_id": route.route_id,
            "distance": route.distance,
            "duration": route.duration,
            "fuel_used": route.fuel_used,
            "driver_id": route.driver_id,
            "vehicle_type": route.vehicle_type,
            "stops_count": route.stops_count,
            "stops": route.stops_data,
            "speed_avg": route.speed_avg,
            "fuel_efficiency": route.fuel_efficiency,
            "hour_of_day": route.hour_of_day,
            "day_of_week": route.day_of_week,
            "is_weekend": route.is_weekend,
            "is_rush_hour": route.is_rush_hour,
            "avg_stop_distance": route.avg_stop_distance,
            "timestamp": route.timestamp.isoformat() if route.timestamp else None,
        }

    def _alert_to_dict(self, alert):
        """Convert alert model to dictionary"""
        return {
            "id": str(alert.id),
            "type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title,
            "message": alert.message,
            "metric": alert.metric_name,
            "value": alert.metric_value,
            "threshold": alert.threshold_value,
            "routes": alert.affected_routes,
            "actions": alert.recommended_actions,
            "is_acknowledged": alert.is_acknowledged,
            "acknowledged_by": alert.acknowledged_by,
            "acknowledged_at": (
                alert.acknowledged_at.isoformat() if alert.acknowledged_at else None
            ),
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
        }


# Global database manager instance
db_manager = None


def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager


def init_database(database_url: str = None):
    """Initialize database with tables"""
    global db_manager
    if database_url:
        db_manager = DatabaseManager(database_url)
    else:
        db_manager = DatabaseManager()

    db_manager.create_tables()
    return db_manager
