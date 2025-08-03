import os
import pytest
from unittest import mock
import app.services.log_scheduler as log_scheduler

def test_scheduler_initializes(monkeypatch):
    monkeypatch.setenv("LOG_EXPORT_SCHEDULE_ENABLED", "true")
    monkeypatch.setenv("LOG_EXPORT_SCHEDULE_INTERVAL", "1")
    with mock.patch("schedule.every") as mock_every:
        with mock.patch("app.services.log_scheduler.run_exporter") as mock_run:
            mock_every.return_value.minutes.do.return_value = None
            # Only run main up to the first schedule.run_pending()
            with mock.patch("schedule.run_pending", side_effect=KeyboardInterrupt):
                try:
                    log_scheduler.main()
                except KeyboardInterrupt:
                    pass
            mock_every.assert_called_once()
