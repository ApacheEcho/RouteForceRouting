import os
import json
from utils import encryption

def load_logs(log_path):
    logs = []
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Try decrypt, fallback to plaintext
            try:
                log_str = encryption.decrypt_data(line)
            except Exception:
                log_str = line
            try:
                logs.append(json.loads(log_str))
            except Exception:
                continue
    return logs
