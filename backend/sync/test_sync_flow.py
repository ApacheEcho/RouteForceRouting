import pytest
from .encryption_utils import encrypt_data, decrypt_data

def test_encryption_decryption():
    data = b"test data for encryption"
    encrypted = encrypt_data(data)
    decrypted = decrypt_data(encrypted)
    assert decrypted == data

# TODO: Add tests for offline/online transition, race conditions, RBAC, and sync conflict resolution
