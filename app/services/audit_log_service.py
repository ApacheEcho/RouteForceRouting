
import os
from app.middleware.audit_logger import log_audit_event

def record_sync_event(user_id, store_count, region):
    try:
        log_audit_event("sync", user_id, {
            "store_count": store_count,
            "region": region,
        })
    except Exception as e:
        # Logging should never break the route
        if os.getenv("AUDIT_LOG_ENCRYPTED", "true").lower() == "true":
            print(f"[WARN] Audit log failed (encryption or write error): {e}. Fallback to plaintext.")

def record_scoring_event(user_id, score, preset, route_id=None):
    try:
        log_audit_event("scoring", user_id, {
            "score": score,
            "preset": preset,
            "route_id": route_id,
        })
    except Exception as e:
        if os.getenv("AUDIT_LOG_ENCRYPTED", "true").lower() == "true":
            print(f"[WARN] Audit log failed (encryption or write error): {e}. Fallback to plaintext.")
