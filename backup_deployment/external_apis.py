"""
External API Integration for RouteForce
Google Maps, Weather, and Traffic Data Integration
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import asyncio
import aiohttp
import logging
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)

@dataclass
class TrafficInfo:
    """Traffic information for a route segment"""
    distance: float
    duration: float
    duration_in_traffic: float
    traffic_delay: float
    conditions: str

@dataclass
class WeatherInfo:
    """Weather information for a location"""
    temperature: float
    humidity: float
    wind_speed: float
    visibility: float
    conditions: str
    precipitation: float
    impact_score: float  # 0-1, higher means worse for routing

@dataclass
class LocationInfo:
    """Geocoded location information"""
    address: str
    latitude: float
    longitude: float
    place_id: str
    accuracy: str

class GoogleMapsIntegration:
    """Google Maps API integration"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        self.base_url = "https://maps.googleapis.com/maps/api"
        self.session = requests.Session()
        
    def geocode_address(self, address: str) -> Optional[LocationInfo]:
        """Geocode an address to coordinates"""
        if not self.api_key:
            logger.warning("Google Maps API key not configured")
            return None
            
        try:
            url = f"{self.base_url}/geocode/json"
            params = {
                'address': address,
                'key': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('status') == 'OK' and data.get('results'):
                result = data['results'][0]
                location = result['geometry']['location']
                
                return LocationInfo(
                    address=result['formatted_address'],
                    latitude=location['lat'],
                    longitude=location['lng'],
                    place_id=result['place_id'],
                    accuracy=result['geometry']['location_type']
                )
                
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            
        return None
    
    def get_route_with_traffic(self, origin: str, destination: str, 
                              waypoints: List[str] = None) -> Optional[TrafficInfo]:
        """Get route information with traffic data"""
        if not self.api_key:
            logger.warning("Google Maps API key not configured")
            return None
            
        try:
            url = f"{self.base_url}/directions/json"
            params = {
                'origin': origin,
                'destination': destination,
                'key': self.api_key,
                'departure_time': 'now',
                'traffic_model': 'best_guess'
            }
            
            if waypoints:
                params['waypoints'] = '|'.join(waypoints)
                params['optimize'] = 'true'
            
            response = self.session.get(url, params=params, timeout=15)
            data = response.json()
            
            if data.get('status') == 'OK' and data.get('routes'):
                route = data['routes'][0]
                leg = route['legs'][0]
                
                distance = leg['distance']['value'] / 1000  # Convert to km
                duration = leg['duration']['value'] / 60  # Convert to minutes
                
                # Get traffic duration if available
                duration_in_traffic = duration
                if 'duration_in_traffic' in leg:
                    duration_in_traffic = leg['duration_in_traffic']['value'] / 60
                
                traffic_delay = duration_in_traffic - duration
                
                # Determine traffic conditions
                if traffic_delay <= 5:
                    conditions = 'light'
                elif traffic_delay <= 15:
                    conditions = 'moderate'
                else:
                    conditions = 'heavy'
                
                return TrafficInfo(
                    distance=distance,
                    duration=duration,
                    duration_in_traffic=duration_in_traffic,
                    traffic_delay=traffic_delay,
                    conditions=conditions
                )
                
        except Exception as e:
            logger.error(f"Traffic data error: {e}")
            
        return None
    
    def optimize_waypoints(self, origin: str, destination: str, 
                          waypoints: List[str]) -> List[str]:
        """Optimize waypoint order using Google Maps"""
        if not self.api_key or not waypoints:
            return waypoints
            
        try:
            url = f"{self.base_url}/directions/json"
            params = {
                'origin': origin,
                'destination': destination,
                'waypoints': 'optimize:true|' + '|'.join(waypoints),
                'key': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=15)
            data = response.json()
            
            if data.get('status') == 'OK' and data.get('routes'):
                route = data['routes'][0]
                if 'waypoint_order' in route:
                    order = route['waypoint_order']
                    return [waypoints[i] for i in order]
                    
        except Exception as e:
            logger.error(f"Waypoint optimization error: {e}")
            
        return waypoints

class WeatherIntegration:
    """Weather API integration using OpenWeatherMap"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.session = requests.Session()
        
    def get_weather(self, latitude: float, longitude: float) -> Optional[WeatherInfo]:
        """Get current weather for coordinates"""
        if not self.api_key:
            # Return simulated weather data
            return self._get_simulated_weather()
            
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                main = data.get('main', {})
                weather = data.get('weather', [{}])[0]
                wind = data.get('wind', {})
                
                # Calculate impact score based on conditions
                impact_score = self._calculate_weather_impact(
                    weather.get('main', ''),
                    wind.get('speed', 0),
                    main.get('humidity', 0)
                )
                
                return WeatherInfo(
                    temperature=main.get('temp', 20),
                    humidity=main.get('humidity', 50),
                    wind_speed=wind.get('speed', 0),
                    visibility=data.get('visibility', 10000) / 1000,  # Convert to km
                    conditions=weather.get('main', 'Clear'),
                    precipitation=data.get('rain', {}).get('1h', 0),
                    impact_score=impact_score
                )
                
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            
        return self._get_simulated_weather()
    
    def get_weather_forecast(self, latitude: float, longitude: float, 
                           hours: int = 24) -> List[WeatherInfo]:
        """Get weather forecast for next few hours"""
        if not self.api_key:
            return [self._get_simulated_weather() for _ in range(hours)]
            
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': min(hours // 3, 40)  # API returns 3-hour intervals
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                forecasts = []
                for item in data.get('list', []):
                    main = item.get('main', {})
                    weather = item.get('weather', [{}])[0]
                    wind = item.get('wind', {})
                    
                    impact_score = self._calculate_weather_impact(
                        weather.get('main', ''),
                        wind.get('speed', 0),
                        main.get('humidity', 0)
                    )
                    
                    forecasts.append(WeatherInfo(
                        temperature=main.get('temp', 20),
                        humidity=main.get('humidity', 50),
                        wind_speed=wind.get('speed', 0),
                        visibility=10,  # Default visibility
                        conditions=weather.get('main', 'Clear'),
                        precipitation=item.get('rain', {}).get('3h', 0),
                        impact_score=impact_score
                    ))
                
                return forecasts
                
        except Exception as e:
            logger.error(f"Weather forecast error: {e}")
            
        return [self._get_simulated_weather() for _ in range(hours)]
    
    def _calculate_weather_impact(self, conditions: str, wind_speed: float, 
                                 humidity: float) -> float:
        """Calculate weather impact score on routing (0-1)"""
        impact = 0.0
        
        # Weather condition impact
        condition_impact = {
            'thunderstorm': 0.8,
            'drizzle': 0.3,
            'rain': 0.5,
            'snow': 0.7,
            'mist': 0.4,
            'fog': 0.6,
            'clear': 0.0,
            'clouds': 0.1
        }
        
        impact += condition_impact.get(conditions.lower(), 0.2)
        
        # Wind impact
        if wind_speed > 20:  # High wind
            impact += 0.3
        elif wind_speed > 10:  # Moderate wind
            impact += 0.1
            
        # Humidity impact
        if humidity > 90:  # Very high humidity
            impact += 0.2
        elif humidity > 70:  # High humidity
            impact += 0.1
            
        return min(impact, 1.0)
    
    def _get_simulated_weather(self) -> WeatherInfo:
        """Get simulated weather data when API is not available"""
        import random
        
        conditions_list = ['Clear', 'Clouds', 'Rain', 'Fog']
        condition = random.choice(conditions_list)
        
        return WeatherInfo(
            temperature=random.uniform(15, 30),
            humidity=random.uniform(40, 80),
            wind_speed=random.uniform(0, 15),
            visibility=random.uniform(5, 10),
            conditions=condition,
            precipitation=random.uniform(0, 5) if condition == 'Rain' else 0,
            impact_score=random.uniform(0, 0.5)
        )

class ExternalDataManager:
    """Manages all external data integrations"""
    
    def __init__(self):
        self.maps = GoogleMapsIntegration()
        self.weather = WeatherIntegration()
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        
    def enhance_route_with_external_data(self, route_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance route data with external APIs"""
        enhanced = route_data.copy()
        
        try:
            # Get route coordinates if not present
            if 'coordinates' not in enhanced and 'stops' in enhanced:
                coordinates = self._geocode_stops(enhanced['stops'])
                enhanced['coordinates'] = coordinates
            
            # Get traffic information
            if 'coordinates' in enhanced and len(enhanced['coordinates']) >= 2:
                traffic_info = self._get_route_traffic(enhanced['coordinates'])
                if traffic_info:
                    enhanced.update({
                        'traffic_delay': traffic_info.traffic_delay,
                        'traffic_conditions': traffic_info.conditions,
                        'duration_with_traffic': traffic_info.duration_in_traffic
                    })
            
            # Get weather information
            if 'coordinates' in enhanced and enhanced['coordinates']:
                weather_info = self._get_route_weather(enhanced['coordinates'][0])
                if weather_info:
                    enhanced.update({
                        'weather_conditions': weather_info.conditions,
                        'weather_impact': weather_info.impact_score,
                        'temperature': weather_info.temperature,
                        'precipitation': weather_info.precipitation
                    })
            
            # Calculate enhanced efficiency score
            enhanced['enhanced_efficiency_score'] = self._calculate_enhanced_efficiency(enhanced)
            
        except Exception as e:
            logger.error(f"External data enhancement error: {e}")
        
        return enhanced
    
    def optimize_route_with_traffic(self, origin: str, destination: str, 
                                   waypoints: List[str]) -> Dict[str, Any]:
        """Optimize route considering current traffic"""
        try:
            # Optimize waypoint order
            optimized_waypoints = self.maps.optimize_waypoints(origin, destination, waypoints)
            
            # Get traffic information for optimized route
            traffic_info = self.maps.get_route_with_traffic(
                origin, destination, optimized_waypoints
            )
            
            # Get weather impact
            origin_coords = self.maps.geocode_address(origin)
            weather_impact = 0
            if origin_coords:
                weather = self.weather.get_weather(origin_coords.latitude, origin_coords.longitude)
                if weather:
                    weather_impact = weather.impact_score
            
            return {
                'optimized_waypoints': optimized_waypoints,
                'original_waypoints': waypoints,
                'traffic_info': traffic_info.__dict__ if traffic_info else None,
                'weather_impact': weather_impact,
                'optimization_improvement': len(waypoints) != len(optimized_waypoints)
            }
            
        except Exception as e:
            logger.error(f"Route optimization error: {e}")
            return {
                'optimized_waypoints': waypoints,
                'original_waypoints': waypoints,
                'error': str(e)
            }
    
    def get_route_recommendations(self, route_data: Dict[str, Any]) -> List[str]:
        """Get AI recommendations based on external data"""
        recommendations = []
        
        try:
            enhanced_data = self.enhance_route_with_external_data(route_data)
            
            # Traffic-based recommendations
            if enhanced_data.get('traffic_delay', 0) > 15:
                recommendations.append(f"Heavy traffic detected. Consider departing {int(enhanced_data['traffic_delay'])} minutes earlier.")
            
            # Weather-based recommendations
            weather_impact = enhanced_data.get('weather_impact', 0)
            if weather_impact > 0.5:
                conditions = enhanced_data.get('weather_conditions', '')
                recommendations.append(f"Poor weather conditions ({conditions}). Allow extra time and drive carefully.")
                
                if enhanced_data.get('precipitation', 0) > 2:
                    recommendations.append("Rain expected. Ensure vehicles have good tires and visibility equipment.")
            
            # Time-based recommendations
            hour = datetime.now().hour
            if hour in [7, 8, 17, 18, 19]:
                recommendations.append("Rush hour traffic. Consider alternative departure times.")
            
            # Efficiency recommendations
            efficiency_score = enhanced_data.get('enhanced_efficiency_score', 0)
            if efficiency_score < 0.6:
                recommendations.append("Route efficiency below optimal. Consider route optimization.")
            
        except Exception as e:
            logger.error(f"Recommendations error: {e}")
            recommendations.append("Unable to generate external data recommendations.")
        
        return recommendations
    
    def _geocode_stops(self, stops: List[str]) -> List[Tuple[float, float]]:
        """Geocode list of stops to coordinates"""
        coordinates = []
        for stop in stops:
            cache_key = f"geocode_{stop}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if time.time() - timestamp < self.cache_timeout:
                    coordinates.append(cached_data)
                    continue
            
            location = self.maps.geocode_address(stop)
            if location:
                coord = (location.latitude, location.longitude)
                coordinates.append(coord)
                self.cache[cache_key] = (coord, time.time())
            else:
                # Use default coordinates if geocoding fails
                coordinates.append((40.7128, -74.0060))  # NYC default
        
        return coordinates
    
    def _get_route_traffic(self, coordinates: List[Tuple[float, float]]) -> Optional[TrafficInfo]:
        """Get traffic information for route coordinates"""
        if len(coordinates) < 2:
            return None
            
        origin = f"{coordinates[0][0]},{coordinates[0][1]}"
        destination = f"{coordinates[-1][0]},{coordinates[-1][1]}"
        
        waypoints = []
        if len(coordinates) > 2:
            waypoints = [f"{lat},{lng}" for lat, lng in coordinates[1:-1]]
        
        return self.maps.get_route_with_traffic(origin, destination, waypoints)
    
    def _get_route_weather(self, coordinates: Tuple[float, float]) -> Optional[WeatherInfo]:
        """Get weather information for route start point"""
        cache_key = f"weather_{coordinates[0]}_{coordinates[1]}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_timeout:
                return cached_data
        
        weather = self.weather.get_weather(coordinates[0], coordinates[1])
        if weather:
            self.cache[cache_key] = (weather, time.time())
        
        return weather
    
    def _calculate_enhanced_efficiency(self, route_data: Dict[str, Any]) -> float:
        """Calculate enhanced efficiency score with external data"""
        base_score = 0.5
        
        # Traffic impact
        traffic_delay = route_data.get('traffic_delay', 0)
        if traffic_delay <= 5:
            base_score += 0.2
        elif traffic_delay <= 15:
            base_score += 0.1
        else:
            base_score -= 0.1
        
        # Weather impact
        weather_impact = route_data.get('weather_impact', 0)
        base_score -= weather_impact * 0.3
        
        # Time of day impact
        hour = datetime.now().hour
        if 10 <= hour <= 16:  # Off-peak hours
            base_score += 0.1
        elif hour in [7, 8, 17, 18, 19]:  # Rush hours
            base_score -= 0.2
        
        return max(0, min(1, base_score))

# Global instance
external_data_manager = ExternalDataManager()

def get_external_data_manager() -> ExternalDataManager:
    """Get the global external data manager instance"""
    return external_data_manager
