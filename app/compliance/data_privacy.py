from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import json
import hashlib
from flask import current_app
from app.models import User, AuditLog
from app import db

class DataPrivacyManager:
    """GDPR/CCPA compliant data management"""
    
    def __init__(self):
        encryption_key = current_app.config.get('ENCRYPTION_KEY')
        if not encryption_key:
            encryption_key = Fernet.generate_key()
        self.cipher = Fernet(encryption_key)
    
    def encrypt_pii(self, data):
        """Encrypt personally identifiable information"""
        if isinstance(data, dict):
            data = json.dumps(data)
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_pii(self, encrypted_data):
        """Decrypt PII when authorized"""
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return json.loads(decrypted.decode())
    
    def anonymize_user_data(self, user_data):
        """Anonymize data for analytics while preserving utility"""
        anonymized = user_data.copy()
        
        # Hash identifiers
        if 'user_id' in anonymized:
            anonymized['user_id'] = hashlib.sha256(
                str(user_data['user_id']).encode()
            ).hexdigest()[:16]
        
        # Remove direct identifiers
        pii_fields = ['name', 'email', 'phone', 'ssn', 'license_number']
        for field in pii_fields:
            if field in anonymized:
                del anonymized[field]
        
        # Generalize location data
        if 'address' in anonymized:
            # Keep only postal code prefix
            postal_code = anonymized['address'].split()[-1]
            anonymized['postal_code'] = postal_code[:3] + 'XX'
            del anonymized['address']
        
        # Generalize dates
        if 'birth_date' in anonymized:
            birth_year = datetime.fromisoformat(anonymized['birth_date']).year
            anonymized['age_group'] = self._get_age_group(birth_year)
            del anonymized['birth_date']
        
        return anonymized
    
    def handle_data_request(self, user_id, request_type):
        """Handle GDPR/CCPA data requests"""
        # Log the request
        AuditLog.create(
            user_id=user_id,
            action=f'data_request_{request_type}',
            details={'request_type': request_type}
        )
        
        if request_type == 'access':
            return self._export_user_data(user_id)
        elif request_type == 'delete':
            return self._delete_user_data(user_id)
        elif request_type == 'portability':
            return self._export_portable_data(user_id)
        elif request_type == 'rectification':
            return self._get_rectification_form(user_id)
    
    def _export_user_data(self, user_id):
        """Export all user data for GDPR access request"""
        user = User.query.get(user_id)
        if not user:
            return None
        
        # Collect all user data
        user_data = {
            'profile': user.to_dict(),
            'routes': [route.to_dict() for route in user.routes],
            'deliveries': [delivery.to_dict() for delivery in user.deliveries],
            'audit_logs': [log.to_dict() for log in user.audit_logs],
            'consent_records': [consent.to_dict() for consent in user.consent_records]
        }
        
        # Include data retention information
        user_data['data_retention'] = {
            'profile': '3 years after account closure',
            'routes': '1 year after completion',
            'audit_logs': '7 years for compliance'
        }
        
        return user_data
    
    def _delete_user_data(self, user_id):
        """Delete user data per GDPR right to erasure"""
        user = User.query.get(user_id)
        if not user:
            return {'status': 'error', 'message': 'User not found'}
        
        # Check if deletion is allowed
        if self._has_legal_hold(user_id):
            return {
                'status': 'error',
                'message': 'Cannot delete due to legal obligations'
            }
        
        # Anonymize instead of hard delete for audit trail
        user.email = f"deleted_{user_id}@example.com"
        user.name = "Deleted User"
        user.phone = None
        user.address = None
        user.is_active = False
        user.deleted_at = datetime.utcnow()
        
        db.session.commit()
        
        return {
            'status': 'success',
            'message': 'User data anonymized',
            'deleted_at': user.deleted_at.isoformat()
        }
    
    def _export_portable_data(self, user_id):
        """Export data in portable format (JSON/CSV)"""
        data = self._export_user_data(user_id)
        
        # Convert to standardized format
        portable_data = {
            'format_version': '1.0',
            'export_date': datetime.utcnow().isoformat(),
            'user_data': data
        }
        
        return portable_data
    
    def _get_age_group(self, birth_year):
        """Convert birth year to age group"""
        current_year = datetime.utcnow().year
        age = current_year - birth_year
        
        if age < 25:
            return '18-24'
        elif age < 35:
            return '25-34'
        elif age < 45:
            return '35-44'
        elif age < 55:
            return '45-54'
        elif age < 65:
            return '55-64'
        else:
            return '65+'
    
    def _has_legal_hold(self, user_id):
        """Check if user data must be retained for legal reasons"""
        # Check for active investigations, disputes, etc.
        # This is a placeholder - implement based on business rules
        return False
