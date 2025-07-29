from typing import Any


def should_reject_route(score_result: Any) -> bool:
    """
    Reject route if score is below a threshold or has other issues.
    """
    try:
        # Example: reject if score is negative or None
        score = getattr(score_result, "score", None)
        if score is None or score < 0:
            return True
        return False
    except Exception:
        return True
