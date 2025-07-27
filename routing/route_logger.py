"""
Route logging functionality for RouteForce routing system.
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logger
logger = logging.getLogger(__name__)


def log_route_score(route_data: Dict[str, Any], score: float, breakdown: Optional[Dict[str, Any]] = None) -> None:
    """
    Log route scoring information for analysis and debugging.
    
    Args:
        route_data: Dictionary containing route information
        score: The calculated route score
        breakdown: Optional breakdown of score components
    """
    timestamp = datetime.now().isoformat()
    
    log_entry = {
        "timestamp": timestamp,
        "route_id": route_data.get("id", "unknown"),
        "score": score,
        "breakdown": breakdown or {},
        "route_summary": {
            "origin": route_data.get("origin"),
            "destination": route_data.get("destination"),
            "distance": route_data.get("distance"),
            "duration": route_data.get("duration")
        }
    }
    
    logger.info(f"Route scored: {score:.2f} for route {route_data.get('id', 'unknown')}")
    logger.debug(f"Route scoring details: {log_entry}")


def log_route_error(route_data: Dict[str, Any], error: str) -> None:
    """
    Log route processing errors.
    
    Args:
        route_data: Dictionary containing route information
        error: Error message or description
    """
    timestamp = datetime.now().isoformat()
    
    log_entry = {
        "timestamp": timestamp,
        "route_id": route_data.get("id", "unknown"),
        "error": error,
        "route_data": route_data
    }
    
    logger.error(f"Route processing error for route {route_data.get('id', 'unknown')}: {error}")
    logger.debug(f"Route error details: {log_entry}")


def log_route_metrics(route_data: Dict[str, Any], metrics: Dict[str, Any]) -> None:
    """
    Log route performance and quality metrics.
    
    Args:
        route_data: Dictionary containing route information
        metrics: Dictionary containing various route metrics
    """
    timestamp = datetime.now().isoformat()
    
    log_entry = {
        "timestamp": timestamp,
        "route_id": route_data.get("id", "unknown"),
        "metrics": metrics
    }
    
    logger.info(f"Route metrics logged for route {route_data.get('id', 'unknown')}")
    logger.debug(f"Route metrics: {log_entry}")
