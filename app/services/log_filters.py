import json
from datetime import datetime

def filter_by_route_id(logs, route_id):
    return [log for log in logs if log.get('metadata', {}).get('route_id') == route_id]

def filter_by_user(logs, user_id):
    return [log for log in logs if log.get('actor') == user_id]

def filter_by_time_range(logs, start=None, end=None):
    def in_range(log):
        ts = log.get('timestamp')
        if not ts:
            return False
        dt = datetime.fromisoformat(ts)
        if start and dt < start:
            return False
        if end and dt > end:
            return False
        return True
    return [log for log in logs if in_range(log)]

def apply_filters(logs, route_id=None, user_id=None, start=None, end=None):
    if route_id:
        logs = filter_by_route_id(logs, route_id)
    if user_id:
        logs = filter_by_user(logs, user_id)
    if start or end:
        logs = filter_by_time_range(logs, start, end)
    return logs
