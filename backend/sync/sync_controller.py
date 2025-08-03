from .sync_staging_model import SyncStaging, SyncStatusLog
from sqlalchemy.orm import Session
from datetime import datetime

def flush_sync(session: Session, user_id: str):
    """Flushes all dirty records for a user as synced (last-write-wins)."""
    records = session.query(SyncStaging).filter_by(user_id=user_id, dirty=True).all()
    for rec in records:
        rec.dirty = False
        rec.last_sync = datetime.utcnow()
    session.commit()

def log_sync_failure(session: Session, user_id: str, reason: str):
    log = SyncStatusLog(user_id=user_id, status='failure', failure_reason=reason, attempts=1)
    session.add(log)
    session.commit()

def get_sync_logs(session: Session, user_id: str = None):
    query = session.query(SyncStatusLog)
    if user_id:
        query = query.filter_by(user_id=user_id)
    return query.order_by(SyncStatusLog.timestamp.desc()).all()
