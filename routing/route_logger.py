"""Route logging functionality for tracking and debugging route generation."""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional


def log_route_score(route_data: Dict[str, Any], log_file: Optional[str] = None) -> None:
    """
    Log route scoring data for analysis and debugging.
    
    Args:
        route_data: Dictionary containing route information and scores
        log_file: Optional path to log file, defaults to timestamped log
    """
    if log_file is None:
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"route_scores_{timestamp}.json")
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Prepare log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "route_data": route_data
    }
    
    # Write to log file
    try:
        # Read existing data if file exists
        existing_data = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                try:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
                except json.JSONDecodeError:
                    existing_data = []
        
        # Append new entry
        existing_data.append(log_entry)
        
        # Write back to file
        with open(log_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
            
    except Exception as e:
        print(f"Warning: Failed to write to log file {log_file}: {e}")


def get_route_logs(log_file: str) -> list:
    """
    Read route logs from a log file.
    
    Args:
        log_file: Path to the log file
        
    Returns:
        List of log entries
    """
    try:
        with open(log_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
