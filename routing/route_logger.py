"""
Route logging functionality for RouteForce.
Handles logging of route scores and performance metrics.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional


def log_route_score(route_data: Dict[str, Any], score: float,
                    metadata: Optional[Dict[str, Any]] = None) -> None:
    """
    Log route score data for analysis and debugging.

    Args:
        route_data: Dictionary containing route information
        score: Calculated route score
        metadata: Optional additional metadata
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "route_data": route_data,
        "score": score,
        "metadata": metadata or {}
    }

    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Log to file
    log_file = os.path.join(log_dir, "route_scores.log")
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def get_route_score_logs(limit: int = 100) -> list:
    """
    Retrieve recent route score logs.

    Args:
        limit: Maximum number of logs to return

    Returns:
        List of log entries
    """
    log_file = os.path.join("logs", "route_scores.log")
    if not os.path.exists(log_file):
        return []

    logs = []
    with open(log_file, "r") as f:
        for line in f:
            try:
                logs.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue

    return logs[-limit:] if logs else []


def clear_route_score_logs() -> None:
    """Clear all route score logs."""
    log_file = os.path.join("logs", "route_scores.log")
    if os.path.exists(log_file):
        os.remove(log_file)
