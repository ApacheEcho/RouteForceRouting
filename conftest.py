import logging
import os
import shutil

import pytest

log_dir = "logs/2025-07-XX/"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, "test_hangs.log"), level=logging.INFO
)
quarantine_logger = logging.getLogger("quarantine")
quarantine_handler = logging.FileHandler(os.path.join(log_dir, "quarantined_tests.log"))
quarantine_logger.addHandler(quarantine_handler)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    # Disabled forced retry/fail logic for normal test runs
    pass


@pytest.fixture(autouse=True)
def timeout_management(request):
    yield
    if hasattr(request.node, "retry_count") and request.node.retry_count > 0:
        logging.info(
            f"Test {request.node.nodeid} completed after {request.node.retry_count + 1} attempts."
        )
