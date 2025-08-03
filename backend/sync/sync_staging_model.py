from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class SyncStaging(Base):
    __tablename__ = 'sync_staging'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    encrypted_payload = Column(LargeBinary, nullable=False)
    last_sync = Column(DateTime, default=datetime.datetime.utcnow)
    dirty = Column(Boolean, default=True)

class SyncStatusLog(Base):
    __tablename__ = 'sync_status_log'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    failure_reason = Column(String)
    attempts = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
