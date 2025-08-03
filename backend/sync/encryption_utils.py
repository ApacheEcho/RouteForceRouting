import os
from cryptography.fernet import Fernet

# Fernet key should be unique per user/device and rotateable
FERNET_KEY = os.environ.get("FERNET_KEY", Fernet.generate_key())
fernet = Fernet(FERNET_KEY)

def encrypt_data(data: bytes) -> bytes:
    """Encrypt bytes using Fernet symmetric encryption."""
    return fernet.encrypt(data)

def decrypt_data(token: bytes) -> bytes:
    """Decrypt bytes using Fernet symmetric encryption."""
    return fernet.decrypt(token)

def rotate_key(new_key: bytes):
    """Rotate Fernet key (admin/ops only)."""
    global fernet
    fernet = Fernet(new_key)
