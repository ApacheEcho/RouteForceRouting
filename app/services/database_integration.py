"""
Database Integration Service for RouteForce Analytics
Connects analytics engine with persistent database storage
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_, desc, func

from app.models.database import db, Route
from app.models.insight import Insight

logger = logging.getLogger(__name__)


class DatabaseIntegrationService:
    """Service for integrating analytics with database storage"""

    def __init__(self):
        self.logger = logger

    def store_route_data(self, route_data: Dict[str, Any]) -> str:
        """
        Store route data in database

        Args:
            route_data: Route information dictionary

        Returns:
            route_id: Stored route ID
        """
        try:
            # Map incoming route_data into our Flask-SQLAlchemy Route model
            route = Route(
                name=route_data.get("name"),
                description=route_data.get("description"),
            )

            # store raw route payload in route_data column
            try:
                route.set_route_data(route_data.get("stops", []))
            except Exception:
                route.route_data = json.dumps(route_data.get("stops", []))

            # populate totals
            route.total_distance = route_data.get("distance") or route_data.get(
                "total_distance"
            )
            route.estimated_time = int(route_data.get("duration") or route_data.get(
                "estimated_time", 0
            ))

            # optional metrics
            route.optimization_score = route_data.get("optimization_score")
            route.algorithm_used = route_data.get("algorithm_used")

            db.session.add(route)
            db.session.commit()

            self.logger.info(f"Stored route data: {route.id}")
            return str(route.id)

        except Exception as e:
            self.logger.error(f"Error storing route data: {str(e)}")
            db.session.rollback()
            raise

    def store_route_insights(self, route_id: str, insights: List[Dict[str, Any]]) -> List[str]:
        """
        Store route insights in database

        Args:
            route_id: Route identifier
            insights: List of insight dictionaries

        Returns:
            List of stored insight IDs
        """
        try:
            insight_ids: List[str] = []

            for insight_data in insights:
                insight = Insight(
                    route_id=int(route_id) if isinstance(route_id, (int, str)) and str(route_id).isdigit() else route_id,
                    insight_type=insight_data.get("type", "general"),
                    content=insight_data.get("content", {}),
                )

                db.session.add(insight)
                db.session.flush()
                insight_ids.append(str(insight.id))

            db.session.commit()
            self.logger.info(f"Stored {len(insights)} insights for route {route_id}")
            return insight_ids

        except Exception as e:
            self.logger.error(f"Error storing insights: {str(e)}")
            db.session.rollback()
            raise

    def store_predictions(self, route_id: str, predictions: Dict[str, Any]) -> str:
        """
        Store route predictions in database

        Args:
            route_id: Route identifier
            predictions: Prediction data dictionary

        Returns:
            prediction_id: Stored prediction ID
        """
        try:
            # No dedicated prediction model in Flask-SQLAlchemy models; store as an Insight
            insight = Insight(
                route_id=int(route_id) if isinstance(route_id, (int, str)) and str(route_id).isdigit() else route_id,
                insight_type="prediction",
                content=predictions,
            )

            db.session.add(insight)
            db.session.commit()

            self.logger.info(f"Stored prediction for route {route_id}")
            return str(insight.id)

        except Exception as e:
            self.logger.error(f"Error storing prediction: {str(e)}")
            db.session.rollback()
            raise

    def get_historical_routes(
        self,
        driver_id: Optional[str] = None,
        days_back: int = 30,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve historical route data

        Args:
            driver_id: Optional driver filter
            days_back: Number of days to look back
            limit: Optional result limit

        Returns:
            List of route data dictionaries
        """
        try:
            query = db.session.query(Route)

            # Apply filters
            if driver_id:
                query = query.filter(Route.driver_id == driver_id)

            if days_back:
                cutoff_date = datetime.now() - timedelta(days=days_back)
                query = query.filter(Route.timestamp >= cutoff_date)

            # Order by timestamp
            query = query.order_by(desc(Route.timestamp))

            # Apply limit
            if limit:
                query = query.limit(limit)

            routes = query.all()

            # Convert to dictionaries
            route_data = []
            for route in routes:
                route_dict = {
                    "route_id": route.route_id,
                    "distance": route.distance,
                    "duration": route.duration,
                    "fuel_used": route.fuel_used,
                    "driver_id": route.driver_id,
                    "vehicle_type": route.vehicle_type,
                    "stops_count": route.stops_count,
                    "stops": route.stops_data,
                    "timestamp": route.timestamp.isoformat(),
                    "speed_avg": route.speed_avg,
                    "fuel_efficiency": route.fuel_efficiency,
                    "hour_of_day": route.hour_of_day,
                    "day_of_week": route.day_of_week,
                    "is_weekend": route.is_weekend,
                    "is_rush_hour": route.is_rush_hour,
                    "avg_stop_distance": route.avg_stop_distance,
                }
                route_data.append(route_dict)

            self.logger.info(f"Retrieved {len(route_data)} historical routes")
            return route_data

        except Exception as e:
            self.logger.error(f"Error retrieving historical routes: {str(e)}")
            raise

    def get_route_insights(
        self,
        route_id: Optional[str] = None,
        insight_type: Optional[str] = None,
        days_back: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve route insights from database

        Args:
            route_id: Optional route filter
            insight_type: Optional insight type filter
            days_back: Number of days to look back

        Returns:
            List of insight dictionaries
        """
        try:
            query = db.session.query(Insight)

            # Apply filters
            if route_id:
                # route_id could be stored as integer PK or route identifier; match both
                try:
                    rid = int(route_id)
                    query = query.filter(Insight.route_id == rid)
                except Exception:
                    query = query.filter(Insight.route_id == route_id)

            if insight_type:
                query = query.filter(Insight.insight_type == insight_type)

            if days_back:
                cutoff_date = datetime.now() - timedelta(days=days_back)
                query = query.filter(Insight.created_at >= cutoff_date)

            # Order by created_at
            query = query.order_by(desc(Insight.created_at))

            insights = query.all()

            # Convert to dictionaries
            insight_data: List[Dict[str, Any]] = []
            for insight in insights:
                insight_data.append(
                    {
                        "id": str(insight.id),
                        "route_id": insight.route_id,
                        "type": insight.insight_type,
                        "content": insight.content,
                        "created_at": insight.created_at.isoformat()
                        if insight.created_at
                        else None,
                    }
                )

            self.logger.info(f"Retrieved {len(insight_data)} insights")
            return insight_data

        except Exception as e:
            self.logger.error(f"Error retrieving insights: {str(e)}")
            raise

    def get_performance_metrics(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Get aggregated performance metrics

        Args:
            days_back: Number of days to analyze

        Returns:
            Performance metrics dictionary
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)

            # Get basic route metrics
            route_metrics = (
                db.session.query(
                    func.count(Route.id).label("total_routes"),
                    func.avg(Route.distance).label("avg_distance"),
                    func.avg(Route.duration).label("avg_duration"),
                    func.avg(Route.fuel_efficiency).label("avg_fuel_efficiency"),
                    func.sum(Route.distance).label("total_distance"),
                    func.sum(Route.duration).label("total_duration"),
                )
                .filter(Route.timestamp >= cutoff_date)
                .first()
            )

            # Get driver performance
            driver_metrics = (
                db.session.query(
                    Route.driver_id,
                    func.count(Route.id).label("route_count"),
                    func.avg(Route.fuel_efficiency).label("avg_efficiency"),
                    func.avg(Route.speed_avg).label("avg_speed"),
                )
                .filter(Route.timestamp >= cutoff_date)
                .group_by(Route.driver_id)
                .order_by(desc("avg_efficiency"))
                .limit(10)
                .all()
            )

            # Get time-based patterns
            time_patterns = (
                db.session.query(
                    Route.hour_of_day,
                    func.count(Route.id).label("route_count"),
                    func.avg(Route.fuel_efficiency).label("avg_efficiency"),
                )
                .filter(Route.timestamp >= cutoff_date)
                .group_by(Route.hour_of_day)
                .order_by(Route.hour_of_day)
                .all()
            )

            metrics = {
                "period_days": days_back,
                "total_routes": route_metrics.total_routes or 0,
                "avg_distance": float(route_metrics.avg_distance or 0),
                "avg_duration": float(route_metrics.avg_duration or 0),
                "avg_fuel_efficiency": float(route_metrics.avg_fuel_efficiency or 0),
                "total_distance": float(route_metrics.total_distance or 0),
                "total_duration": float(route_metrics.total_duration or 0),
                "top_drivers": [
                    {
                        "driver_id": d.driver_id,
                        "route_count": d.route_count,
                        "avg_efficiency": float(d.avg_efficiency or 0),
                        "avg_speed": float(d.avg_speed or 0),
                    }
                    for d in driver_metrics
                ],
                "hourly_patterns": [
                    {
                        "hour": p.hour_of_day,
                        "route_count": p.route_count,
                        "avg_efficiency": float(p.avg_efficiency or 0),
                    }
                    for p in time_patterns
                ],
            }

            return metrics

        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {str(e)}")
            raise

    def _is_rush_hour(self) -> bool:
        """Check if current time is during rush hour"""
        hour = datetime.now().hour
        return (7 <= hour <= 9) or (17 <= hour <= 19)

    def cleanup_old_data(self, days_to_keep: int = 90) -> Dict[str, int]:
        """
        Clean up old data from database

        Args:
            days_to_keep: Number of days of data to retain

        Returns:
            Cleanup statistics
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            # Count records to be deleted
            routes_to_delete = (
                db.session.query(Route).filter(Route.timestamp < cutoff_date).count()
            )
            # Only clean up insights and routes (predictions model not present in Flask models)
            insights_to_delete = (
                db.session.query(Insight).filter(Insight.created_at < cutoff_date).count()
            )

            # Delete old records
            db.session.query(Insight).filter(Insight.created_at < cutoff_date).delete()
            db.session.query(Route).filter(Route.created_at < cutoff_date).delete()

            db.session.commit()

            cleanup_stats = {
                "routes_deleted": routes_to_delete,
                "insights_deleted": insights_to_delete,
                "cutoff_date": cutoff_date.isoformat(),
            }

            self.logger.info(f"Cleanup completed: {cleanup_stats}")
            return cleanup_stats

        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
            db.session.rollback()
            raise


# Global instance
database_service = DatabaseIntegrationService()
