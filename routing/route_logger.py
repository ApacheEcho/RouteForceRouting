import os
from typing import Any


def log_route_score(score_result: Any, log_file: str) -> None:
    """
    Log the route score result to a file.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "a") as f:
        f.write(f"{getattr(score_result, 'score', score_result)}\n")
