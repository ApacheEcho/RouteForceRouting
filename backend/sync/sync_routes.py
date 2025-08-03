
from flask import Blueprint, request, jsonify
from .encryption_utils import decrypt_data, encrypt_data
from .sync_staging_model import SyncStaging, SyncStatusLog
from sqlalchemy.orm import Session
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.services.audit_log_service import record_sync_event

sync_bp = Blueprint('sync', __name__, url_prefix='/sync')

@sync_bp.route('/push', methods=['POST'])
@jwt_required()
def push_sync():
    user_id = get_jwt_identity()
    encrypted_payload = request.data
    # RBAC: Only allow rep's own data (add role check as needed)
    session: Session = request.environ['db_session']
    staging = SyncStaging(user_id=user_id, encrypted_payload=encrypted_payload, last_sync=datetime.utcnow(), dirty=True)
    session.add(staging)
    session.commit()
    log = SyncStatusLog(user_id=user_id, status='success', attempts=1)
    session.add(log)
    session.commit()
    # Audit log event
    # For demo, region is hardcoded; in real use, extract from payload or user profile
    record_sync_event(user_id, store_count=1, region="N/A")
    return jsonify({'status': 'ok'})

@sync_bp.route('/pull', methods=['GET'])
@jwt_required()
def pull_sync():
    user_id = get_jwt_identity()
    last_sync = request.args.get('last_sync')
    session: Session = request.environ['db_session']
    query = session.query(SyncStaging).filter_by(user_id=user_id)
    if last_sync:
        query = query.filter(SyncStaging.last_sync > last_sync)
    results = query.all()
    payloads = [s.encrypted_payload for s in results]
    return jsonify({'payloads': payloads})
