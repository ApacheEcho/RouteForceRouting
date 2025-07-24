"""
Advanced Analytics Service for RouteForce Routing
Provides comprehensive analytics and monitoring capabilities
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import uuid
from collections import defaultdict, Counter
from statistics import mean, median
import numpy as np

logger = logging.getLogger(__name__)

class AnalyticsService:
    """
    Comprehensive analytics service for RouteForce Routing
    Tracks mobile usage, driver performance, route optimization, and system metrics
    """
    
    def __init__(self):
        # In production, use Redis or dedicated analytics database
        self.mobile_sessions = {}
        self.driver_metrics = defaultdict(list)
        self.route_analytics = []
        self.api_metrics = defaultdict(list)
        self.system_events = []
        self.performance_data = defaultdict(list)
        
    def track_mobile_session(self, device_id: str, session_data: Dict[str, Any]) -> None:
        """Track mobile app session analytics"""
        try:
            session_id = str(uuid.uuid4())
            timestamp = datetime.utcnow()
            
            session_record = {
                'session_id': session_id,
                'device_id': device_id,
                'app_version': session_data.get('app_version'),
                'device_type': session_data.get('device_type'),
                'started_at': timestamp.isoformat(),
                'last_activity': timestamp.isoformat(),
                'api_calls': 0,
                'features_used': [],
                'location_updates': 0,
                'route_requests': 0,
                'offline_syncs': 0
            }
            
            self.mobile_sessions[session_id] = session_record
            logger.info(f"Mobile session tracked: {device_id}")
            
        except Exception as e:
            logger.error(f"Failed to track mobile session: {e}")
    
    def track_api_usage(self, endpoint: str, method: str, response_time: float, 
                       status_code: int, user_agent: str = None) -> None:
        """Track API endpoint usage and performance"""
        try:
            api_record = {
                'endpoint': endpoint,
                'method': method,
                'response_time': response_time,
                'status_code': status_code,
                'timestamp': datetime.utcnow().isoformat(),
                'user_agent': user_agent,
                'is_mobile': self._is_mobile_request(user_agent)
            }
            
            self.api_metrics[endpoint].append(api_record)
            
            # Track performance metrics
            self.performance_data['api_response_times'].append(response_time)
            
        except Exception as e:
            logger.error(f"Failed to track API usage: {e}")
    
    def track_driver_performance(self, driver_id: str, metrics: Dict[str, Any]) -> None:
        """Track driver performance metrics"""
        try:
            driver_record = {
                'driver_id': driver_id,
                'timestamp': datetime.utcnow().isoformat(),
                'location_accuracy': metrics.get('location_accuracy'),
                'speed': metrics.get('speed'),
                'route_deviation': metrics.get('route_deviation'),
                'stops_completed': metrics.get('stops_completed'),
                'time_at_stop': metrics.get('time_at_stop'),
                'fuel_efficiency': metrics.get('fuel_efficiency'),
                'customer_rating': metrics.get('customer_rating')
            }
            
            self.driver_metrics[driver_id].append(driver_record)
            logger.debug(f"Driver performance tracked: {driver_id}")
            
        except Exception as e:
            logger.error(f"Failed to track driver performance: {e}")
    
    def track_route_optimization(self, route_data: Dict[str, Any]) -> None:
        """Track route optimization performance and results"""
        try:
            route_record = {
                'route_id': route_data.get('route_id'),
                'algorithm': route_data.get('algorithm'),
                'stores_count': len(route_data.get('stores', [])),
                'optimization_time': route_data.get('optimization_time'),
                'total_distance': route_data.get('total_distance'),
                'total_time': route_data.get('total_time'),
                'improvement_percentage': route_data.get('improvement_percentage'),
                'timestamp': datetime.utcnow().isoformat(),
                'success': route_data.get('success', False),
                'traffic_aware': route_data.get('traffic_aware', False)
            }
            
            self.route_analytics.append(route_record)
            
            # Track optimization performance
            if route_record['optimization_time']:
                self.performance_data['optimization_times'].append(route_record['optimization_time'])
            
        except Exception as e:
            logger.error(f"Failed to track route optimization: {e}")
    
    def track_system_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Track system events for monitoring and debugging"""
        try:
            event_record = {
                'event_id': str(uuid.uuid4()),
                'event_type': event_type,
                'timestamp': datetime.utcnow().isoformat(),
                'data': event_data,
                'severity': event_data.get('severity', 'info')
            }
            
            self.system_events.append(event_record)
            
            # Log important events
            if event_data.get('severity') in ['error', 'critical']:
                logger.error(f"System event: {event_type} - {event_data}")
            
        except Exception as e:
            logger.error(f"Failed to track system event: {e}")
    
    def get_mobile_analytics(self, timeframe: str = '24h') -> Dict[str, Any]:
        """Get mobile app usage analytics"""
        try:
            cutoff_time = self._get_cutoff_time(timeframe)
            
            # Filter recent sessions
            recent_sessions = [
                session for session in self.mobile_sessions.values()
                if datetime.fromisoformat(session['started_at']) >= cutoff_time
            ]
            
            if not recent_sessions:
                return self._empty_analytics_response()
            
            # Calculate metrics
            total_sessions = len(recent_sessions)
            device_types = Counter(session['device_type'] for session in recent_sessions)
            app_versions = Counter(session['app_version'] for session in recent_sessions)
            
            # API usage statistics
            total_api_calls = sum(session['api_calls'] for session in recent_sessions)
            avg_api_calls = total_api_calls / total_sessions if total_sessions > 0 else 0
            
            # Feature usage
            all_features = []
            for session in recent_sessions:
                all_features.extend(session['features_used'])
            feature_usage = Counter(all_features)
            
            return {
                'timeframe': timeframe,
                'total_sessions': total_sessions,
                'unique_devices': len(set(session['device_id'] for session in recent_sessions)),
                'device_types': dict(device_types),
                'app_versions': dict(app_versions),
                'total_api_calls': total_api_calls,
                'avg_api_calls_per_session': round(avg_api_calls, 2),
                'feature_usage': dict(feature_usage),
                'most_used_features': feature_usage.most_common(5)
            }
            
        except Exception as e:
            logger.error(f"Failed to get mobile analytics: {e}")
            return self._empty_analytics_response()
    
    def get_driver_analytics(self, timeframe: str = '24h') -> Dict[str, Any]:
        """Get driver performance analytics"""
        try:
            cutoff_time = self._get_cutoff_time(timeframe)
            
            # Aggregate driver metrics
            recent_metrics = []
            for driver_id, metrics_list in self.driver_metrics.items():
                driver_recent = [
                    metric for metric in metrics_list
                    if datetime.fromisoformat(metric['timestamp']) >= cutoff_time
                ]
                recent_metrics.extend(driver_recent)
            
            if not recent_metrics:
                return {'timeframe': timeframe, 'total_drivers': 0}
            
            # Calculate performance statistics
            location_accuracies = [m['location_accuracy'] for m in recent_metrics if m['location_accuracy']]
            speeds = [m['speed'] for m in recent_metrics if m['speed']]
            customer_ratings = [m['customer_rating'] for m in recent_metrics if m['customer_rating']]
            
            return {
                'timeframe': timeframe,
                'total_drivers': len(set(m['driver_id'] for m in recent_metrics)),
                'total_location_updates': len(recent_metrics),
                'avg_location_accuracy': round(mean(location_accuracies), 2) if location_accuracies else 0,
                'avg_speed': round(mean(speeds), 2) if speeds else 0,
                'avg_customer_rating': round(mean(customer_ratings), 2) if customer_ratings else 0,
                'top_performers': self._get_top_performing_drivers(timeframe),
                'performance_trends': self._get_driver_performance_trends(timeframe)
            }
            
        except Exception as e:
            logger.error(f"Failed to get driver analytics: {e}")
            return {'timeframe': timeframe, 'error': str(e)}
    
    def get_route_analytics(self, timeframe: str = '24h') -> Dict[str, Any]:
        """Get route optimization analytics"""
        try:
            cutoff_time = self._get_cutoff_time(timeframe)
            
            # Filter recent routes
            recent_routes = [
                route for route in self.route_analytics
                if datetime.fromisoformat(route['timestamp']) >= cutoff_time
            ]
            
            if not recent_routes:
                return {'timeframe': timeframe, 'total_routes': 0}
            
            # Calculate route statistics
            successful_routes = [r for r in recent_routes if r['success']]
            optimization_times = [r['optimization_time'] for r in recent_routes if r['optimization_time']]
            total_distances = [r['total_distance'] for r in recent_routes if r['total_distance']]
            improvements = [r['improvement_percentage'] for r in recent_routes if r['improvement_percentage']]
            
            algorithm_usage = Counter(route['algorithm'] for route in recent_routes)
            
            return {
                'timeframe': timeframe,
                'total_routes': len(recent_routes),
                'successful_routes': len(successful_routes),
                'success_rate': round(len(successful_routes) / len(recent_routes) * 100, 2),
                'avg_optimization_time': round(mean(optimization_times), 3) if optimization_times else 0,
                'avg_total_distance': round(mean(total_distances), 2) if total_distances else 0,
                'avg_improvement': round(mean(improvements), 2) if improvements else 0,
                'algorithm_usage': dict(algorithm_usage),
                'traffic_aware_routes': len([r for r in recent_routes if r['traffic_aware']]),
                'performance_metrics': {
                    'median_optimization_time': round(median(optimization_times), 3) if optimization_times else 0,
                    'max_optimization_time': max(optimization_times) if optimization_times else 0,
                    'min_optimization_time': min(optimization_times) if optimization_times else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get route analytics: {e}")
            return {'timeframe': timeframe, 'error': str(e)}
    
    def get_api_analytics(self, timeframe: str = '24h') -> Dict[str, Any]:
        """Get API usage and performance analytics"""
        try:
            cutoff_time = self._get_cutoff_time(timeframe)
            
            # Aggregate API metrics
            recent_api_calls = []
            for endpoint, calls_list in self.api_metrics.items():
                endpoint_recent = [
                    call for call in calls_list
                    if datetime.fromisoformat(call['timestamp']) >= cutoff_time
                ]
                recent_api_calls.extend(endpoint_recent)
            
            if not recent_api_calls:
                return {'timeframe': timeframe, 'total_requests': 0}
            
            # Calculate API statistics
            endpoint_usage = Counter(call['endpoint'] for call in recent_api_calls)
            status_codes = Counter(call['status_code'] for call in recent_api_calls)
            response_times = [call['response_time'] for call in recent_api_calls]
            mobile_requests = len([call for call in recent_api_calls if call['is_mobile']])
            
            # Error rate calculation
            error_requests = len([call for call in recent_api_calls if call['status_code'] >= 400])
            error_rate = (error_requests / len(recent_api_calls)) * 100 if recent_api_calls else 0
            
            return {
                'timeframe': timeframe,
                'total_requests': len(recent_api_calls),
                'mobile_requests': mobile_requests,
                'mobile_percentage': round((mobile_requests / len(recent_api_calls)) * 100, 2),
                'endpoint_usage': dict(endpoint_usage.most_common(10)),
                'status_codes': dict(status_codes),
                'error_rate': round(error_rate, 2),
                'performance': {
                    'avg_response_time': round(mean(response_times), 3) if response_times else 0,
                    'median_response_time': round(median(response_times), 3) if response_times else 0,
                    'p95_response_time': round(np.percentile(response_times, 95), 3) if response_times else 0,
                    'max_response_time': max(response_times) if response_times else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get API analytics: {e}")
            return {'timeframe': timeframe, 'error': str(e)}
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        try:
            # Recent performance data
            recent_response_times = self.performance_data['api_response_times'][-1000:]
            recent_optimization_times = self.performance_data['optimization_times'][-100:]
            
            # Recent system events
            recent_events = self.system_events[-100:]
            error_events = [e for e in recent_events if e['severity'] in ['error', 'critical']]
            
            # Health score calculation (0-100)
            health_score = self._calculate_health_score(recent_response_times, error_events)
            
            return {
                'health_score': health_score,
                'status': self._get_health_status(health_score),
                'uptime': '99.9%',  # In production, calculate actual uptime
                'performance': {
                    'avg_api_response_time': round(mean(recent_response_times), 3) if recent_response_times else 0,
                    'avg_optimization_time': round(mean(recent_optimization_times), 3) if recent_optimization_times else 0
                },
                'recent_errors': len(error_events),
                'active_sessions': len(self.mobile_sessions),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def generate_analytics_report(self, timeframe: str = '24h') -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        try:
            return {
                'report_id': str(uuid.uuid4()),
                'generated_at': datetime.utcnow().isoformat(),
                'timeframe': timeframe,
                'mobile_analytics': self.get_mobile_analytics(timeframe),
                'driver_analytics': self.get_driver_analytics(timeframe),
                'route_analytics': self.get_route_analytics(timeframe),
                'api_analytics': self.get_api_analytics(timeframe),
                'system_health': self.get_system_health()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate analytics report: {e}")
            return {'error': str(e)}
    
    # Helper methods
    def _get_cutoff_time(self, timeframe: str) -> datetime:
        """Get cutoff time for timeframe filtering"""
        now = datetime.utcnow()
        
        if timeframe == '1h':
            return now - timedelta(hours=1)
        elif timeframe == '24h':
            return now - timedelta(hours=24)
        elif timeframe == '7d':
            return now - timedelta(days=7)
        elif timeframe == '30d':
            return now - timedelta(days=30)
        else:
            return now - timedelta(hours=24)  # Default to 24h
    
    def _is_mobile_request(self, user_agent: str) -> bool:
        """Detect if request is from mobile device"""
        if not user_agent:
            return False
        
        mobile_indicators = ['mobile', 'iphone', 'android', 'ios', 'tablet', 'ipad']
        return any(indicator in user_agent.lower() for indicator in mobile_indicators)
    
    def _empty_analytics_response(self) -> Dict[str, Any]:
        """Return empty analytics response"""
        return {
            'total_sessions': 0,
            'unique_devices': 0,
            'device_types': {},
            'app_versions': {},
            'total_api_calls': 0,
            'avg_api_calls_per_session': 0,
            'feature_usage': {},
            'most_used_features': []
        }
    
    def _get_top_performing_drivers(self, timeframe: str) -> List[Dict[str, Any]]:
        """Get top performing drivers for timeframe"""
        try:
            cutoff_time = self._get_cutoff_time(timeframe)
            driver_scores = {}
            
            for driver_id, metrics_list in self.driver_metrics.items():
                recent_metrics = [
                    m for m in metrics_list
                    if datetime.fromisoformat(m['timestamp']) >= cutoff_time
                ]
                
                if recent_metrics:
                    # Simple scoring based on customer ratings and efficiency
                    ratings = [m['customer_rating'] for m in recent_metrics if m['customer_rating']]
                    avg_rating = mean(ratings) if ratings else 0
                    
                    driver_scores[driver_id] = {
                        'driver_id': driver_id,
                        'avg_rating': round(avg_rating, 2),
                        'total_updates': len(recent_metrics)
                    }
            
            # Return top 5 drivers
            return sorted(driver_scores.values(), key=lambda x: x['avg_rating'], reverse=True)[:5]
            
        except Exception as e:
            logger.error(f"Failed to get top performing drivers: {e}")
            return []
    
    def _get_driver_performance_trends(self, timeframe: str) -> Dict[str, Any]:
        """Get driver performance trends"""
        # Simplified trend analysis
        return {
            'improving_drivers': 0,
            'declining_drivers': 0,
            'stable_drivers': 0
        }
    
    def _calculate_health_score(self, response_times: List[float], error_events: List[Dict]) -> int:
        """Calculate system health score (0-100)"""
        try:
            base_score = 100
            
            # Penalize for slow response times
            if response_times:
                avg_response_time = mean(response_times)
                if avg_response_time > 1.0:  # More than 1 second
                    base_score -= min(30, int(avg_response_time * 10))
            
            # Penalize for errors
            error_penalty = min(40, len(error_events) * 5)
            base_score -= error_penalty
            
            return max(0, base_score)
            
        except Exception:
            return 50  # Default moderate health score
    
    def _get_health_status(self, health_score: int) -> str:
        """Get health status based on score"""
        if health_score >= 90:
            return 'excellent'
        elif health_score >= 75:
            return 'good'
        elif health_score >= 50:
            return 'fair'
        else:
            return 'poor'
