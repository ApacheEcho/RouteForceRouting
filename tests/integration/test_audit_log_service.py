import os
import tempfile
import json
import pytest
import logging
from unittest import mock
from app.services import audit_log_service

# --- Unit Tests: Mock log_audit_event ---
def test_record_sync_event_calls_logger():
    with mock.patch('app.services.audit_log_service.log_audit_event') as mock_log:
        audit_log_service.record_sync_event("abc123", 7, "South")
        mock_log.assert_called_once()
        args, kwargs = mock_log.call_args
        assert args[0] == "sync"
        assert args[1] == "abc123"
        assert args[2]["store_count"] == 7
        assert args[2]["region"] == "South"

def test_record_scoring_event_calls_logger():
    with mock.patch('app.services.audit_log_service.log_audit_event') as mock_log:
        audit_log_service.record_scoring_event("abc123", 87.5, "balanced", route_id="R001")
        mock_log.assert_called_once()
        args, kwargs = mock_log.call_args
        assert args[0] == "scoring"
        assert args[1] == "abc123"
        assert args[2]["score"] == 87.5
        assert args[2]["preset"] == "balanced"
        assert args[2]["route_id"] == "R001"

# --- File Write Tests ---
def test_log_file_write_and_structure(monkeypatch):
    # Patch log file location
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        log_path = tmp.name
    from app.middleware import audit_logger
    logger = logging.getLogger("audit")
    # Remove all handlers
    for h in logger.handlers[:]:
        logger.removeHandler(h)
    # Add temp file handler
    temp_handler = logging.FileHandler(log_path)
    temp_handler.setLevel(logging.INFO)
    logger.addHandler(temp_handler)
    audit_logger.log_audit_event("sync", "abc123", {"store_count": 1, "region": "Test"})
    temp_handler.flush()
    with open(log_path) as f:
        line = f.readline()
        entry = json.loads(line)
        assert entry["event"] == "sync"
        assert entry["actor"] == "abc123"
        assert entry["metadata"]["region"] == "Test"
    logger.removeHandler(temp_handler)
    os.remove(log_path)

def test_log_file_write_failure(monkeypatch):
    # Simulate file write failure
    with mock.patch('logging.FileHandler.emit', side_effect=IOError("disk full")):
        try:
            audit_log_service.record_sync_event("abc123", 1, "FailTest")
        except Exception:
            pytest.fail("Logging failure should not raise")

# --- Edge Case Tests ---
def test_missing_optional_route_id():
    with mock.patch('app.services.audit_log_service.log_audit_event') as mock_log:
        audit_log_service.record_scoring_event("abc123", 99.9, "long_preset_name")
        args, kwargs = mock_log.call_args
        assert "route_id" in args[2]
        assert args[2]["route_id"] is None

def test_long_preset_name():
    long_name = "x" * 1000
    with mock.patch('app.services.audit_log_service.log_audit_event') as mock_log:
        audit_log_service.record_scoring_event("abc123", 1, long_name)
        args, kwargs = mock_log.call_args
        assert args[2]["preset"] == long_name

def test_empty_store_count():
    with mock.patch('app.services.audit_log_service.log_audit_event') as mock_log:
        audit_log_service.record_sync_event("abc123", 0, "Nowhere")
        args, kwargs = mock_log.call_args
        assert args[2]["store_count"] == 0

def test_invalid_score_type():
    with mock.patch('app.services.audit_log_service.log_audit_event') as mock_log:
        audit_log_service.record_scoring_event("abc123", "not_a_number", "balanced")
        args, kwargs = mock_log.call_args
        assert isinstance(args[2]["score"], str)
