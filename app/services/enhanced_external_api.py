"""
Enhanced External API Service for RouteForce Analytics
Integrates external data sources with analytics and real-time decision making
"""

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import redis

from app.external_apis import (GoogleMapsIntegration, TrafficInfo, WeatherInfo,
                               WeatherIntegration)
from app.services.database_integration import database_service

logger = logging.getLogger(__name__)


@dataclass
class ContextualRouteData:
    """Enhanced route data with external context"""

    route_id: str
    distance: float
    duration: float
    traffic_info: TrafficInfo
    weather_info: list[WeatherInfo]
    fuel_impact_factor: float
    delay_probability: float
    risk_score: float
    optimization_opportunities: list[str]


class EnhancedExternalAPIService:
    """Enhanced external API service with analytics integration"""

    def __init__(self):
        self.maps_api = GoogleMapsIntegration()
        self.weather_api = WeatherIntegration()
        self.cache = self._init_cache()
        self.executor = ThreadPoolExecutor(max_workers=10)

    def _init_cache(self):
        """Initialize Redis cache for API responses"""
        try:
            # Try to connect to Redis with environment configuration
            redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
            cache = redis.from_url(redis_url, decode_responses=True)
            cache.ping()
            logger.info("✅ Redis cache connected successfully")
            return cache
        except Exception as e:
            logger.info(
                "ℹ️ Redis not available, using in-memory cache (normal for basic deployments)"
            )
            return {}

    def get_enhanced_route_data(
        self, origin: str, destination: str, waypoints: list[str] = None
    ) -> ContextualRouteData:
        """
        Get comprehensive route data with traffic, weather, and analytics context

        Args:
            origin: Starting location
            destination: End location
            waypoints: Optional intermediate stops

        Returns:
            Enhanced route data with external context
        """
        try:
            # Generate cache key
            cache_key = f"enhanced_route:{hash(f'{origin}:{destination}:{waypoints}')}"

            # Check cache first
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return ContextualRouteData(**cached_data)

            # Get basic route data
            route_data = self.maps_api.get_route_data(origin, destination, waypoints)

            # Get traffic information
            traffic_info = self.maps_api.get_traffic_info(origin, destination)

            # Get weather for all locations
            weather_futures = []
            locations = [origin] + (waypoints or []) + [destination]

            with ThreadPoolExecutor(max_workers=5) as executor:
                weather_futures = [
                    executor.submit(self.weather_api.get_weather_data, location)
                    for location in locations
                ]

                weather_data = []
                for future in as_completed(weather_futures):
                    try:
                        weather_info = future.result(timeout=5)
                        if weather_info:
                            weather_data.append(weather_info)
                    except Exception as e:
                        logger.error(f"Error getting weather data: {e}")

            # Calculate impact factors
            fuel_impact = self._calculate_fuel_impact(weather_data, traffic_info)
            delay_probability = self._calculate_delay_probability(
                traffic_info, weather_data
            )
            risk_score = self._calculate_risk_score(weather_data, traffic_info)
            optimization_opportunities = self._identify_optimization_opportunities(
                route_data, traffic_info, weather_data
            )

            # Create enhanced route data
            enhanced_data = ContextualRouteData(
                route_id=f"route_{datetime.now().timestamp()}",
                distance=route_data.get("distance", 0),
                duration=route_data.get("duration", 0),
                traffic_info=traffic_info,
                weather_info=weather_data,
                fuel_impact_factor=fuel_impact,
                delay_probability=delay_probability,
                risk_score=risk_score,
                optimization_opportunities=optimization_opportunities,
            )

            # Cache the result
            self._store_in_cache(cache_key, asdict(enhanced_data), ttl=300)  # 5 minutes

            return enhanced_data

        except Exception as e:
            logger.error(f"Error getting enhanced route data: {e}")
            # Return basic data if external APIs fail
            return ContextualRouteData(
                route_id=f"route_{datetime.now().timestamp()}",
                distance=10.0,
                duration=30.0,
                traffic_info=TrafficInfo(10.0, 30.0, 35.0, 5.0, "moderate"),
                weather_info=[],
                fuel_impact_factor=1.0,
                delay_probability=0.1,
                risk_score=0.3,
                optimization_opportunities=["Data unavailable - using defaults"],
            )

    def get_real_time_updates(
        self, route_id: str, current_location: tuple[float, float]
    ) -> dict[str, Any]:
        """
        Get real-time updates for an active route

        Args:
            route_id: Active route identifier
            current_location: Current GPS coordinates (lat, lon)

        Returns:
            Real-time route updates and recommendations
        """
        try:
            lat, lon = current_location

            # Get current traffic conditions
            traffic_future = self.executor.submit(
                self.maps_api.get_current_traffic, lat, lon
            )

            # Get current weather
            weather_future = self.executor.submit(
                self.weather_api.get_current_weather, lat, lon
            )

            # Get results with timeout
            traffic_data = traffic_future.result(timeout=3)
            weather_data = weather_future.result(timeout=3)

            # Analyze changes from original route
            updates = {
                "timestamp": datetime.now().isoformat(),
                "location": {"lat": lat, "lon": lon},
                "traffic_update": traffic_data,
                "weather_update": weather_data,
                "recommendations": [],
                "alerts": [],
                "eta_adjustment": 0,
            }

            # Check for significant changes
            if traffic_data and traffic_data.get("severity", "low") in [
                "high",
                "severe",
            ]:
                updates["alerts"].append(
                    {
                        "type": "traffic",
                        "severity": "high",
                        "message": "Heavy traffic detected ahead",
                        "recommendation": "Consider alternative route",
                    }
                )
                updates["eta_adjustment"] += traffic_data.get("delay_minutes", 0)

            if weather_data and weather_data.get("impact_score", 0) > 0.7:
                updates["alerts"].append(
                    {
                        "type": "weather",
                        "severity": "medium",
                        "message": "Adverse weather conditions",
                        "recommendation": "Reduce speed and increase following distance",
                    }
                )
                updates["eta_adjustment"] += 5  # Weather impact

            # Store update in database
            try:
                database_service.store_route_data(
                    {
                        "route_id": route_id,
                        "real_time_update": updates,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            except Exception as e:
                logger.error(f"Failed to store real-time update: {e}")

            return updates

        except Exception as e:
            logger.error(f"Error getting real-time updates: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "location": {"lat": lat, "lon": lon},
                "error": "Unable to fetch real-time data",
                "recommendations": ["Continue with planned route"],
                "alerts": [],
                "eta_adjustment": 0,
            }

    def optimize_route_with_context(
        self, route_request: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Optimize route considering external factors and analytics insights

        Args:
            route_request: Route optimization request

        Returns:
            Optimized route with context and recommendations
        """
        try:
            origin = route_request["origin"]
            destination = route_request["destination"]
            waypoints = route_request.get("waypoints", [])
            preferences = route_request.get("preferences", {})

            # Get multiple route options
            route_options = []

            # Standard route
            standard_route = self.get_enhanced_route_data(
                origin, destination, waypoints
            )
            route_options.append(("standard", standard_route))

            # Alternative routes if available
            try:
                alt_routes = self.maps_api.get_alternative_routes(
                    origin, destination, waypoints
                )
                for i, alt_route in enumerate(alt_routes[:2]):  # Max 2 alternatives
                    enhanced_alt = self.get_enhanced_route_data(
                        alt_route["origin"],
                        alt_route["destination"],
                        alt_route.get("waypoints"),
                    )
                    route_options.append((f"alternative_{i+1}", enhanced_alt))
            except Exception as e:
                logger.warning(f"Could not get alternative routes: {e}")

            # Score each route option
            scored_routes = []
            for route_name, route_data in route_options:
                score = self._score_route_option(route_data, preferences)
                scored_routes.append(
                    {
                        "name": route_name,
                        "data": route_data,
                        "score": score,
                        "summary": self._generate_route_summary(route_data),
                    }
                )

            # Sort by score (higher is better)
            scored_routes.sort(key=lambda x: x["score"], reverse=True)
            best_route = scored_routes[0]

            optimization_result = {
                "recommended_route": best_route,
                "alternatives": scored_routes[1:],
                "optimization_factors": {
                    "weather_impact": best_route["data"].fuel_impact_factor,
                    "traffic_delay_risk": best_route["data"].delay_probability,
                    "overall_risk": best_route["data"].risk_score,
                },
                "recommendations": best_route["data"].optimization_opportunities,
                "analysis_timestamp": datetime.now().isoformat(),
            }

            # Store optimization result
            try:
                database_service.store_route_data(
                    {
                        "route_id": best_route["data"].route_id,
                        "optimization_result": optimization_result,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            except Exception as e:
                logger.error(f"Failed to store optimization result: {e}")

            return optimization_result

        except Exception as e:
            logger.error(f"Error optimizing route with context: {e}")
            return {
                "error": "Route optimization failed",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _calculate_fuel_impact(
        self, weather_data: list[WeatherInfo], traffic_info: TrafficInfo
    ) -> float:
        """Calculate fuel consumption impact factor"""
        try:
            base_impact = 1.0

            # Weather impact
            for weather in weather_data:
                if weather.wind_speed > 25:  # km/h
                    base_impact += 0.05  # 5% increase for strong winds
                if weather.temperature < 0 or weather.temperature > 35:
                    base_impact += 0.03  # 3% increase for extreme temperatures
                if weather.precipitation > 5:  # mm
                    base_impact += 0.08  # 8% increase for heavy rain

            # Traffic impact
            if traffic_info.traffic_delay > 10:  # minutes
                base_impact += 0.15  # 15% increase for significant delays
            elif traffic_info.traffic_delay > 5:
                base_impact += 0.08  # 8% increase for moderate delays

            return min(base_impact, 1.5)  # Cap at 50% increase

        except Exception as e:
            logger.error(f"Error calculating fuel impact: {e}")
            return 1.0

    def _calculate_delay_probability(
        self, traffic_info: TrafficInfo, weather_data: list[WeatherInfo]
    ) -> float:
        """Calculate probability of delays"""
        try:
            base_probability = 0.1  # 10% base probability

            # Traffic-based probability
            if traffic_info.traffic_delay > 15:
                base_probability += 0.4
            elif traffic_info.traffic_delay > 5:
                base_probability += 0.2

            # Weather-based probability
            for weather in weather_data:
                if weather.impact_score > 0.7:
                    base_probability += 0.3
                elif weather.impact_score > 0.4:
                    base_probability += 0.15

            return min(base_probability, 0.9)  # Cap at 90%

        except Exception as e:
            logger.error(f"Error calculating delay probability: {e}")
            return 0.1

    def _calculate_risk_score(
        self, weather_data: list[WeatherInfo], traffic_info: TrafficInfo
    ) -> float:
        """Calculate overall route risk score"""
        try:
            risk_factors = []

            # Weather risks
            for weather in weather_data:
                risk_factors.append(weather.impact_score)

            # Traffic risks
            traffic_risk = min(traffic_info.traffic_delay / 30, 1.0)  # Normalize to 0-1
            risk_factors.append(traffic_risk)

            # Calculate weighted average
            if risk_factors:
                return sum(risk_factors) / len(risk_factors)
            return 0.0

        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 0.0

    def _identify_optimization_opportunities(
        self,
        route_data: dict,
        traffic_info: TrafficInfo,
        weather_data: list[WeatherInfo],
    ) -> list[str]:
        """Identify route optimization opportunities"""
        opportunities = []

        try:
            # Time-based opportunities
            current_hour = datetime.now().hour
            if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:
                opportunities.append(
                    "Consider scheduling outside rush hours to avoid traffic"
                )

            # Weather-based opportunities
            for weather in weather_data:
                if weather.precipitation > 2:
                    opportunities.append(
                        "Rain detected - allow extra time and reduce speed"
                    )
                if weather.wind_speed > 30:
                    opportunities.append(
                        "Strong winds - fuel efficiency may be reduced"
                    )
                if weather.visibility < 5:  # km
                    opportunities.append(
                        "Poor visibility - consider delaying departure"
                    )

            # Traffic-based opportunities
            if traffic_info.traffic_delay > 10:
                opportunities.append("Heavy traffic - explore alternative routes")
                opportunities.append("Consider departure time adjustment")

            # General opportunities
            route_distance = route_data.get("distance", 0)
            if route_distance > 50:
                opportunities.append("Long route - plan fuel stops and driver breaks")

            return opportunities[:5]  # Limit to top 5 opportunities

        except Exception as e:
            logger.error(f"Error identifying optimization opportunities: {e}")
            return ["Unable to analyze optimization opportunities"]

    def _score_route_option(
        self, route_data: ContextualRouteData, preferences: dict[str, Any]
    ) -> float:
        """Score a route option based on preferences and external factors"""
        try:
            # Base score from route characteristics
            base_score = 100.0

            # Apply penalties based on factors
            base_score -= route_data.fuel_impact_factor * 20  # Fuel efficiency penalty
            base_score -= route_data.delay_probability * 30  # Delay probability penalty
            base_score -= route_data.risk_score * 25  # Risk penalty

            # Apply preferences
            priority = preferences.get("priority", "balanced")
            if priority == "speed":
                base_score -= route_data.duration * 0.5  # Penalize longer routes more
            elif priority == "efficiency":
                base_score -= (
                    route_data.fuel_impact_factor * 30
                )  # Emphasize fuel efficiency
            elif priority == "safety":
                base_score -= route_data.risk_score * 40  # Emphasize safety

            return max(base_score, 0.0)

        except Exception as e:
            logger.error(f"Error scoring route option: {e}")
            return 50.0  # Default middle score

    def _generate_route_summary(
        self, route_data: ContextualRouteData
    ) -> dict[str, Any]:
        """Generate a summary of route characteristics"""
        return {
            "distance_km": round(route_data.distance, 1),
            "estimated_duration_min": round(route_data.duration, 0),
            "traffic_delay_min": round(route_data.traffic_info.traffic_delay, 0),
            "fuel_impact_percent": round((route_data.fuel_impact_factor - 1) * 100, 1),
            "delay_risk_percent": round(route_data.delay_probability * 100, 1),
            "overall_risk": (
                "low"
                if route_data.risk_score < 0.3
                else "medium" if route_data.risk_score < 0.7 else "high"
            ),
            "weather_conditions": [w.conditions for w in route_data.weather_info],
            "key_recommendations": route_data.optimization_opportunities[:3],
        }

    def _get_from_cache(self, key: str) -> dict[str, Any] | None:
        """Get data from cache"""
        try:
            if isinstance(self.cache, dict):
                return self.cache.get(key)
            else:
                cached = self.cache.get(key)
                return json.loads(cached) if cached else None
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            return None

    def _store_in_cache(self, key: str, data: dict[str, Any], ttl: int = 300):
        """Store data in cache"""
        try:
            if isinstance(self.cache, dict):
                self.cache[key] = data
            else:
                self.cache.setex(key, ttl, json.dumps(data, default=str))
        except Exception as e:
            logger.error(f"Cache write error: {e}")


# Global service instance
enhanced_api_service = EnhancedExternalAPIService()
