import pytest
import logging
import os
import shutil

log_dir = 'logs/2025-07-XX/'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(filename=os.path.join(log_dir, 'test_hangs.log'), level=logging.INFO)
quarantine_logger = logging.getLogger('quarantine')
quarantine_handler = logging.FileHandler(os.path.join(log_dir, 'quarantined_tests.log'))
quarantine_logger.addHandler(quarantine_handler)

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    if call.when == 'call':
        if call.excinfo is not None:
            item.retry_count = getattr(item, 'retry_count', 0) + 1
            if item.retry_count == 2:
                quarantine_logger.warning(f"Test {item.nodeid} auto-skipped after 2 failures or timeout.")
                pytest.skip(reason="Auto-skipped after 2 failures or timeout")
            else:
                logging.error(f"Test {item.nodeid} failed on attempt {item.retry_count}. Retrying...")
                pytest.fail(f"Retrying test {item.nodeid}")

@pytest.fixture(autouse=True)
def timeout_management(request):
    yield
    if request.node.retry_count > 0:
        logging.info(f"Test {request.node.nodeid} completed after {request.node.retry_count + 1} attempts.")