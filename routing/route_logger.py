from datetime import datetime
from typing import Any


def log_route_score(score_result: Any, log_file: str) -> None:
    """
    Log route score result to a file.
    
    Args:
        score_result: Object with score attribute and other route metrics
        log_file: Path to the log file
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        score = getattr(score_result, "score", 0)
        
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - Route Score: {score:.2f}\n")
            
            # Log additional details if available
            if hasattr(score_result, "details"):
                f.write(f"  Details: {score_result.details}\n")
            if hasattr(score_result, "issues"):
                f.write(f"  Issues: {score_result.issues}\n")
            f.write("\n")
            
    except Exception as e:
        print(f"Warning: Failed to log route score: {e}")
