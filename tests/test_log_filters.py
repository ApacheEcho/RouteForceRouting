import pytest
from app.services import log_filters
from datetime import datetime

def sample_logs():
    return [
        {"timestamp": "2025-08-03T12:00:00", "actor": "u1", "metadata": {"route_id": "R1"}},
        {"timestamp": "2025-08-03T13:00:00", "actor": "u2", "metadata": {"route_id": "R2"}},
        {"timestamp": "2025-08-03T14:00:00", "actor": "u1", "metadata": {"route_id": "R3"}},
    ]

def test_filter_by_route_id():
    logs = sample_logs()
    out = log_filters.filter_by_route_id(logs, "R2")
    assert len(out) == 1 and out[0]["metadata"]["route_id"] == "R2"

def test_filter_by_user():
    logs = sample_logs()
    out = log_filters.filter_by_user(logs, "u1")
    assert len(out) == 2

def test_filter_by_time_range():
    logs = sample_logs()
    start = datetime.fromisoformat("2025-08-03T13:00:00")
    end = datetime.fromisoformat("2025-08-03T14:00:00")
    out = log_filters.filter_by_time_range(logs, start, end)
    assert len(out) == 2

def test_apply_filters():
    logs = sample_logs()
    out = log_filters.apply_filters(logs, route_id="R1", user_id="u1")
    assert len(out) == 1
