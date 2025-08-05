"""
Route logging functionality for RouteForce Routing
"""

import json
import os
from datetime import datetime
from typing import Any, Dict


def log_route_score(score_result: Dict[str, Any], log_file: str) -> None:
    """
    Log route scoring results to a specified file.

    Args:
        score_result: Dictionary containing route scoring information
        log_file: Path to the log file
    """
    timestamp = datetime.now().isoformat()

    log_entry = {"timestamp": timestamp, "score_result": score_result}

    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Append to log file
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
