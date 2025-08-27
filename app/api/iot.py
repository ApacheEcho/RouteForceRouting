"""
IoT Device Integration API for RouteForceRouting
Endpoints for device registration and telemetry ingestion
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid

# In-memory device registry for demo (replace with DB in production)
IOT_DEVICES = {}

IOT_TELEMETRY = []


iot_api = Blueprint('iot_api', __name__, url_prefix='/api/iot')

# Simple push notification abstraction (stub for APNs/FCM)
def send_push_notification(device_id, title, body, data=None):
    # In production, integrate with FCM (Android) or APNs (iOS)
    # Here, just log and simulate success
    if device_id not in IOT_DEVICES:
        return False, "Device not registered"
    # Simulate sending
    print(f"[Push] To: {device_id} | Title: {title} | Body: {body} | Data: {data}")
    return True, None

@iot_api.route('/notify', methods=['POST'])
def push_notification():
    data = request.get_json()
    device_id = data.get('device_id')
    title = data.get('title')
    body = data.get('body')
    extra = data.get('data', {})
    if not device_id or not title or not body:
        return jsonify({'success': False, 'error': 'device_id, title, and body required'}), 400
    ok, err = send_push_notification(device_id, title, body, extra)
    if not ok:
        return jsonify({'success': False, 'error': err or 'Notification failed'}), 400
    return jsonify({'success': True, 'message': 'Notification sent'}), 200

@iot_api.route('/register', methods=['POST'])
def register_device():
    data = request.get_json()
    device_id = data.get('device_id') or str(uuid.uuid4())
    device_type = data.get('device_type', 'unknown')
    owner = data.get('owner', None)
    if not device_id:
        return jsonify({'success': False, 'error': 'device_id required'}), 400
    IOT_DEVICES[device_id] = {
        'device_id': device_id,
        'device_type': device_type,
        'owner': owner,
        'registered_at': datetime.utcnow().isoformat()
    }
    return jsonify({'success': True, 'device_id': device_id, 'registered_at': IOT_DEVICES[device_id]['registered_at']}), 201

@iot_api.route('/telemetry', methods=['POST'])
def ingest_telemetry():
    data = request.get_json()
    device_id = data.get('device_id')
    telemetry = data.get('telemetry')
    if not device_id or not telemetry:
        return jsonify({'success': False, 'error': 'device_id and telemetry required'}), 400
    if device_id not in IOT_DEVICES:
        return jsonify({'success': False, 'error': 'Device not registered'}), 404
    entry = {
        'device_id': device_id,
        'telemetry': telemetry,
        'received_at': datetime.utcnow().isoformat()
    }
    IOT_TELEMETRY.append(entry)
    return jsonify({'success': True, 'received_at': entry['received_at']}), 200

@iot_api.route('/devices', methods=['GET'])
def list_devices():
    return jsonify({'success': True, 'devices': list(IOT_DEVICES.values())})

@iot_api.route('/telemetry', methods=['GET'])
def list_telemetry():
    return jsonify({'success': True, 'telemetry': IOT_TELEMETRY})
