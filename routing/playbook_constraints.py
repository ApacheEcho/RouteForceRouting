from typing import Any, Dict


def enforce_playbook_constraints(route: Dict[str, Any]) -> bool:
    """
    Enforce playbook constraints on a route. Returns True if route passes constraints.
    """
    constraints = route.get("constraints", {})
    # Example: reject routes with 'no_sundays' constraint on Sundays
    import datetime

    if constraints.get("no_sundays"):
        if datetime.datetime.today().weekday() == 6:  # Sunday
            return False
    return True
