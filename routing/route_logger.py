"""
Route Logging Module
Provides logging functionality for route scoring and analysis
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional


def setup_route_logger() -> logging.Logger:
    """Setup and configure route logger"""
    logger = logging.getLogger('route_logger')
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def log_route_score(
    route_data: Dict[str, Any], 
    score: float, 
    details: Optional[Dict[str, Any]] = None
) -> None:
    """Log route scoring information"""
    logger = setup_route_logger()
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'route_id': route_data.get('id', 'unknown'),
        'score': score,
        'route_length': len(route_data.get('stops', [])),
        'details': details or {}
    }
    
    logger.info(f"Route scored: {json.dumps(log_entry)}")


def log_route_analysis(
    route_id: str,
    analysis_type: str,
    results: Dict[str, Any]
) -> None:
    """Log route analysis results"""
    logger = setup_route_logger()
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'route_id': route_id,
        'analysis_type': analysis_type,
        'results': results
    }
    
    logger.info(f"Route analysis completed: {json.dumps(log_entry)}")
