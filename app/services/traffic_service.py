"""
Traffic-aware routing service using Google Maps API
Provides real-time traffic data for route optimization
"""

import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class TrafficConfig:
    """Configuration for traffic-aware routing"""

    api_key: str | None = None
    cache_duration: int = 300  # 5 minutes cache
    max_waypoints: int = 25  # Google Maps limit
    avoid_tolls: bool = False
    avoid_highways: bool = False
    avoid_ferries: bool = True
    departure_time: str | None = "now"  # "now" or ISO format
    traffic_model: str = "best_guess"  # best_guess, pessimistic, optimistic


@dataclass
class TrafficData:
    """Traffic data for a route segment"""

    origin: str
    destination: str
    distance_meters: int
    duration_seconds: int
    duration_in_traffic_seconds: int
    traffic_delay: int
    traffic_condition: str  # light, moderate, heavy, severe


class TrafficService:
    """Service for traffic-aware routing using Google Maps API"""

    def __init__(self, config: TrafficConfig = None):
        """Initialize traffic service"""
        self.config = config or TrafficConfig()
        self.cache = {}
        self.cache_timestamps = {}

        # Get API key from environment or config
        self.api_key = (
            self.config.api_key
            or os.getenv("GOOGLE_MAPS_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )

        if not self.api_key:
            logger.warning(
                "Google Maps API key not found. Traffic features will be limited."
            )
            self.api_available = False
        else:
            self.api_available = True
            logger.info("Google Maps API initialized for traffic data")

    def get_traffic_optimized_route(
        self,
        stores: list[dict[str, Any]],
        start_location: dict[str, Any] | None = None,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Generate traffic-optimized route using Google Maps API

        Args:
            stores: List of store locations
            start_location: Optional starting location
            constraints: Additional routing constraints

        Returns:
            Dictionary with optimized route and traffic data
        """
        try:
            if not self.api_available:
                return self._fallback_route(stores, "API not available")

            if len(stores) < 2:
                return self._fallback_route(stores, "Insufficient waypoints")

            # Prepare waypoints
            waypoints = self._prepare_waypoints(stores, start_location)

            if len(waypoints) > self.config.max_waypoints:
                logger.warning(
                    f"Too many waypoints ({len(waypoints)}), using clustering"
                )
                waypoints = self._cluster_waypoints(
                    waypoints, self.config.max_waypoints
                )

            # Get optimized route from Google Maps
            route_data = self._get_google_maps_route(waypoints, constraints)

            if not route_data:
                return self._fallback_route(stores, "Google Maps API failed")

            # Process traffic data
            traffic_info = self._process_traffic_data(route_data)

            # Build optimized route
            optimized_route = self._build_optimized_route(
                stores, route_data, traffic_info
            )

            return {
                "success": True,
                "route": optimized_route,
                "traffic_data": traffic_info,
                "google_maps_data": route_data,
                "total_distance": traffic_info.get("total_distance", 0),
                "total_duration": traffic_info.get("total_duration", 0),
                "traffic_delay": traffic_info.get("total_traffic_delay", 0),
                "algorithm_used": "traffic_optimized",
            }

        except Exception as e:
            logger.error(f"Error in traffic-optimized routing: {str(e)}")
            return self._fallback_route(stores, f"Error: {str(e)}")

    def get_traffic_data_for_segment(
        self,
        origin: dict[str, Any],
        destination: dict[str, Any],
        departure_time: str | None = None,
    ) -> TrafficData | None:
        """
        Get traffic data for a specific route segment

        Args:
            origin: Origin location with lat/lng
            destination: Destination location with lat/lng
            departure_time: Optional departure time

        Returns:
            TrafficData object or None if failed
        """
        try:
            if not self.api_available:
                return None

            # Create cache key
            cache_key = f"{origin['lat']},{origin['lng']}-{destination['lat']},{destination['lng']}"

            # Check cache
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]

            # Prepare request
            origin_str = f"{origin['lat']},{origin['lng']}"
            destination_str = f"{destination['lat']},{destination['lng']}"

            params = {
                "origin": origin_str,
                "destination": destination_str,
                "key": self.api_key,
                "departure_time": departure_time or self.config.departure_time,
                "traffic_model": self.config.traffic_model,
                "units": "metric",
            }

            # Add avoidance options
            avoid = []
            if self.config.avoid_tolls:
                avoid.append("tolls")
            if self.config.avoid_highways:
                avoid.append("highways")
            if self.config.avoid_ferries:
                avoid.append("ferries")

            if avoid:
                params["avoid"] = "|".join(avoid)

            # Make API request
            url = "https://maps.googleapis.com/maps/api/directions/json"
            response = requests.get(url, params=params, timeout=10)

            if response.status_code != 200:
                logger.error(f"Google Maps API error: {response.status_code}")
                return None

            data = response.json()

            if data["status"] != "OK":
                logger.error(f"Google Maps API status: {data['status']}")
                return None

            # Extract traffic data
            route = data["routes"][0]
            leg = route["legs"][0]

            traffic_data = TrafficData(
                origin=origin_str,
                destination=destination_str,
                distance_meters=leg["distance"]["value"],
                duration_seconds=leg["duration"]["value"],
                duration_in_traffic_seconds=leg.get("duration_in_traffic", {}).get(
                    "value", leg["duration"]["value"]
                ),
                traffic_delay=leg.get("duration_in_traffic", {}).get(
                    "value", leg["duration"]["value"]
                )
                - leg["duration"]["value"],
                traffic_condition=self._classify_traffic_condition(
                    leg["duration"]["value"],
                    leg.get("duration_in_traffic", {}).get(
                        "value", leg["duration"]["value"]
                    ),
                ),
            )

            # Cache the result
            self.cache[cache_key] = traffic_data
            self.cache_timestamps[cache_key] = time.time()

            return traffic_data

        except Exception as e:
            logger.error(f"Error getting traffic data: {str(e)}")
            return None

    def get_route_alternatives(
        self, stores: list[dict[str, Any]], max_alternatives: int = 3
    ) -> list[dict[str, Any]]:
        """
        Get alternative routes with traffic data

        Args:
            stores: List of store locations
            max_alternatives: Maximum number of alternatives to return

        Returns:
            List of alternative routes with traffic information
        """
        try:
            if not self.api_available or len(stores) < 2:
                return []

            alternatives = []
            waypoints = self._prepare_waypoints(stores)

            # Generate alternatives by varying route parameters
            route_configs = [
                {"avoid": [], "traffic_model": "best_guess"},
                {"avoid": ["highways"], "traffic_model": "best_guess"},
                {"avoid": ["tolls"], "traffic_model": "pessimistic"},
                {"avoid": ["highways", "tolls"], "traffic_model": "optimistic"},
            ]

            for i, config in enumerate(route_configs[:max_alternatives]):
                route_data = self._get_google_maps_route(waypoints, config)

                if route_data:
                    traffic_info = self._process_traffic_data(route_data)
                    optimized_route = self._build_optimized_route(
                        stores, route_data, traffic_info
                    )

                    alternatives.append(
                        {
                            "route_id": f"alternative_{i+1}",
                            "route": optimized_route,
                            "traffic_data": traffic_info,
                            "config": config,
                            "total_distance": traffic_info.get("total_distance", 0),
                            "total_duration": traffic_info.get("total_duration", 0),
                            "traffic_delay": traffic_info.get("total_traffic_delay", 0),
                        }
                    )

            # Sort by total duration (including traffic)
            alternatives.sort(key=lambda x: x["total_duration"])

            return alternatives

        except Exception as e:
            logger.error(f"Error getting route alternatives: {str(e)}")
            return []

    def predict_traffic_conditions(
        self, stores: list[dict[str, Any]], future_hours: list[int] = [1, 2, 4, 8]
    ) -> dict[str, Any]:
        """
        Predict traffic conditions for future departure times

        Args:
            stores: List of store locations
            future_hours: Hours in the future to predict

        Returns:
            Dictionary with traffic predictions
        """
        try:
            if not self.api_available:
                return {"error": "API not available"}

            predictions = {}
            base_time = datetime.now()

            for hours in future_hours:
                departure_time = base_time + timedelta(hours=hours)
                departure_timestamp = int(departure_time.timestamp())

                route_data = self._get_google_maps_route(
                    self._prepare_waypoints(stores),
                    {"departure_time": str(departure_timestamp)},
                )

                if route_data:
                    traffic_info = self._process_traffic_data(route_data)
                    predictions[f"{hours}h"] = {
                        "departure_time": departure_time.isoformat(),
                        "total_duration": traffic_info.get("total_duration", 0),
                        "traffic_delay": traffic_info.get("total_traffic_delay", 0),
                        "recommended": traffic_info.get("total_traffic_delay", 0)
                        < 300,  # Less than 5 min delay
                    }

            return {
                "success": True,
                "predictions": predictions,
                "best_time": (
                    min(predictions.items(), key=lambda x: x[1]["total_duration"])[0]
                    if predictions
                    else None
                ),
            }

        except Exception as e:
            logger.error(f"Error predicting traffic: {str(e)}")
            return {"error": str(e)}

    def _prepare_waypoints(
        self,
        stores: list[dict[str, Any]],
        start_location: dict[str, Any] | None = None,
    ) -> list[str]:
        """Prepare waypoints for Google Maps API"""
        waypoints = []

        # Add start location if provided
        if start_location and "lat" in start_location and "lng" in start_location:
            waypoints.append(f"{start_location['lat']},{start_location['lng']}")

        # Add store locations
        for store in stores:
            if "lat" in store and "lng" in store:
                waypoints.append(f"{store['lat']},{store['lng']}")
            elif "latitude" in store and "longitude" in store:
                waypoints.append(f"{store['latitude']},{store['longitude']}")

        return waypoints

    def _cluster_waypoints(self, waypoints: list[str], max_points: int) -> list[str]:
        """Cluster waypoints to reduce to maximum allowed"""
        if len(waypoints) <= max_points:
            return waypoints

        # Simple clustering by selecting every nth waypoint
        step = len(waypoints) // max_points
        clustered = [waypoints[0]]  # Always include start

        for i in range(step, len(waypoints) - 1, step):
            clustered.append(waypoints[i])

        clustered.append(waypoints[-1])  # Always include end

        return clustered[:max_points]

    def _get_google_maps_route(
        self, waypoints: list[str], constraints: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """Get route from Google Maps API"""
        try:
            if len(waypoints) < 2:
                return None

            params = {
                "origin": waypoints[0],
                "destination": waypoints[-1],
                "key": self.api_key,
                "optimize": "true",  # Optimize waypoint order
                "units": "metric",
                "departure_time": constraints.get(
                    "departure_time", self.config.departure_time
                ),
                "traffic_model": constraints.get(
                    "traffic_model", self.config.traffic_model
                ),
            }

            # Add intermediate waypoints
            if len(waypoints) > 2:
                params["waypoints"] = "|".join(waypoints[1:-1])

            # Add avoidance options
            avoid = constraints.get("avoid", [])
            if self.config.avoid_tolls and "tolls" not in avoid:
                avoid.append("tolls")
            if self.config.avoid_highways and "highways" not in avoid:
                avoid.append("highways")
            if self.config.avoid_ferries and "ferries" not in avoid:
                avoid.append("ferries")

            if avoid:
                params["avoid"] = "|".join(avoid)

            # Make API request
            url = "https://maps.googleapis.com/maps/api/directions/json"
            response = requests.get(url, params=params, timeout=15)

            if response.status_code != 200:
                logger.error(f"Google Maps API HTTP error: {response.status_code}")
                return None

            data = response.json()

            if data["status"] != "OK":
                logger.error(f"Google Maps API error: {data['status']}")
                return None

            return data

        except Exception as e:
            logger.error(f"Error calling Google Maps API: {str(e)}")
            return None

    def _process_traffic_data(self, route_data: dict[str, Any]) -> dict[str, Any]:
        """Process traffic data from Google Maps response"""
        try:
            route = route_data["routes"][0]

            total_distance = 0
            total_duration = 0
            total_traffic_delay = 0
            segments = []

            for leg in route["legs"]:
                leg_distance = leg["distance"]["value"]
                leg_duration = leg["duration"]["value"]
                leg_traffic_duration = leg.get("duration_in_traffic", {}).get(
                    "value", leg_duration
                )
                leg_traffic_delay = leg_traffic_duration - leg_duration

                total_distance += leg_distance
                total_duration += leg_traffic_duration
                total_traffic_delay += leg_traffic_delay

                segments.append(
                    {
                        "start_address": leg["start_address"],
                        "end_address": leg["end_address"],
                        "distance": leg_distance,
                        "duration": leg_duration,
                        "traffic_duration": leg_traffic_duration,
                        "traffic_delay": leg_traffic_delay,
                        "traffic_condition": self._classify_traffic_condition(
                            leg_duration, leg_traffic_duration
                        ),
                    }
                )

            return {
                "total_distance": total_distance,
                "total_duration": total_duration,
                "total_traffic_delay": total_traffic_delay,
                "average_speed": (
                    (total_distance / total_duration * 3.6) if total_duration > 0 else 0
                ),  # km/h
                "traffic_severity": self._classify_overall_traffic(
                    total_duration, total_traffic_delay
                ),
                "segments": segments,
                "waypoint_order": route.get("waypoint_order", []),
            }

        except Exception as e:
            logger.error(f"Error processing traffic data: {str(e)}")
            return {}

    def _classify_traffic_condition(
        self, normal_duration: int, traffic_duration: int
    ) -> str:
        """Classify traffic condition based on delay"""
        if traffic_duration <= normal_duration * 1.1:
            return "light"
        elif traffic_duration <= normal_duration * 1.3:
            return "moderate"
        elif traffic_duration <= normal_duration * 1.6:
            return "heavy"
        else:
            return "severe"

    def _classify_overall_traffic(self, total_duration: int, total_delay: int) -> str:
        """Classify overall traffic severity"""
        if total_delay <= 0:
            return "no_delay"
        elif total_delay <= total_duration * 0.1:
            return "light"
        elif total_delay <= total_duration * 0.25:
            return "moderate"
        elif total_delay <= total_duration * 0.5:
            return "heavy"
        else:
            return "severe"

    def _build_optimized_route(
        self,
        original_stores: list[dict[str, Any]],
        route_data: dict[str, Any],
        traffic_info: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Build optimized route from Google Maps data"""
        try:
            optimized_route = []
            waypoint_order = traffic_info.get("waypoint_order", [])

            # If Google Maps optimized the waypoint order, reorder stores
            if waypoint_order:
                # Reorder stores based on Google's optimization
                for idx in waypoint_order:
                    if idx < len(original_stores):
                        store = original_stores[idx].copy()
                        store["traffic_optimized"] = True
                        optimized_route.append(store)
            else:
                # Use original order
                optimized_route = [store.copy() for store in original_stores]

            # Add traffic information to each store
            for i, store in enumerate(optimized_route):
                if i < len(traffic_info.get("segments", [])):
                    segment = traffic_info["segments"][i]
                    store.update(
                        {
                            "segment_distance": segment["distance"],
                            "segment_duration": segment["duration"],
                            "traffic_duration": segment["traffic_duration"],
                            "traffic_delay": segment["traffic_delay"],
                            "traffic_condition": segment["traffic_condition"],
                        }
                    )

            return optimized_route

        except Exception as e:
            logger.error(f"Error building optimized route: {str(e)}")
            return original_stores

    def _fallback_route(
        self, stores: list[dict[str, Any]], reason: str
    ) -> dict[str, Any]:
        """Fallback to basic route when traffic API fails"""
        return {
            "success": False,
            "route": stores,
            "traffic_data": {},
            "error": reason,
            "algorithm_used": "fallback",
        }

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache_timestamps:
            return False

        return (
            time.time() - self.cache_timestamps[cache_key]
        ) < self.config.cache_duration

    def clear_cache(self):
        """Clear the traffic data cache"""
        self.cache.clear()
        self.cache_timestamps.clear()
        logger.info("Traffic data cache cleared")

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.cache)
        valid_entries = sum(1 for key in self.cache if self._is_cache_valid(key))

        return {
            "total_entries": total_entries,
            "valid_entries": valid_entries,
            "expired_entries": total_entries - valid_entries,
            "cache_hit_ratio": (
                valid_entries / total_entries if total_entries > 0 else 0
            ),
        }
