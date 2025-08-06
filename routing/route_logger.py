"""Route logging functionality for RouteForce routing system."""

import os
from datetime import datetime
from typing import Any, Optional


def log_route_score(score_result: Any, log_file: Optional[str] = None) -> None:
    """
    Log route scoring results to a file.
    
    Args:
        score_result: The result object from route scoring
        log_file: Optional path to log file. If None, creates default log file.
    """
    if log_file is None:
        log_file = f"route_scores_{datetime.now().strftime('%Y%m%d')}.log"
    
    timestamp = datetime.now().isoformat()
    
    # Create log entry
    score = getattr(score_result, 'score', None)
    log_entry = f"[{timestamp}] Score: {score if score is not None else 'N/A'}"
    
    # Add additional details if available
    if hasattr(score_result, 'details'):
        log_entry += f", Details: {score_result.details}"
    
    log_entry += "\n"
    
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    os.makedirs(log_dir if log_dir else '.', exist_ok=True)
    
    # Write to log file
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)
