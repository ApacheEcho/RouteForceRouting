def log_audit_event(event_type, actor, metadata):


import logging
import json
from datetime import datetime
import os
from utils import encryption
from utils import redaction

def log_audit_event(event_type, actor, metadata):
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        "actor": actor,
        "metadata": metadata,
    }
    log_str = json.dumps(log)
    # Redact if enabled
    if redaction.is_redaction_enabled():
        log_str = redaction.redact_all(log_str)
    encrypted = None
    fernet_key = os.getenv("AUDIT_LOG_ENCRYPTION_KEY")
    if fernet_key:
        try:
            encrypted = encryption.encrypt_data(log_str.encode())
        except Exception as e:
            print(f"[WARN] Audit log encryption failed: {e}. Writing plaintext.")
    if encrypted:
        logging.getLogger("audit").info(encrypted)
    else:
        logging.getLogger("audit").info(log_str)

# Ensure audit log file handler is set up
os.makedirs("logs", exist_ok=True)
audit_handler = logging.FileHandler("logs/audit.log")
audit_handler.setLevel(logging.INFO)
logging.getLogger("audit").addHandler(audit_handler)
