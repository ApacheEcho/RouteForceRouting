import os
import tempfile
import pytest
from utils import encryption
from cryptography.fernet import Fernet

def test_encrypt_decrypt_roundtrip():
    key = Fernet.generate_key().decode()
    os.environ["AUDIT_LOG_ENCRYPTION_KEY"] = key
    data = b'{"foo": "bar"}'
    token = encryption.encrypt_data(data)
    assert isinstance(token, str)
    out = encryption.decrypt_data(token)
    assert out == data.decode()

def test_decrypt_audit_log(tmp_path):
    key = Fernet.generate_key().decode()
    os.environ["AUDIT_LOG_ENCRYPTION_KEY"] = key
    f = Fernet(key)
    lines = [f.encrypt(b'{"a":1}').decode(), f.encrypt(b'{"b":2}').decode()]
    log_path = tmp_path / "audit.log"
    with open(log_path, "w") as fobj:
        for line in lines:
            fobj.write(line + "\n")
    # Capture output
    from io import StringIO
    import sys
    old = sys.stdout
    sys.stdout = mystdout = StringIO()
    encryption.decrypt_audit_log(str(log_path))
    sys.stdout = old
    output = mystdout.getvalue()
    assert '{"a":1}' in output and '{"b":2}' in output

def test_encrypt_data_no_key():
    if "AUDIT_LOG_ENCRYPTION_KEY" in os.environ:
        del os.environ["AUDIT_LOG_ENCRYPTION_KEY"]
    data = b'hello'
    assert encryption.encrypt_data(data) is None

def test_decrypt_data_no_key():
    if "AUDIT_LOG_ENCRYPTION_KEY" in os.environ:
        del os.environ["AUDIT_LOG_ENCRYPTION_KEY"]
    with pytest.raises(ValueError):
        encryption.decrypt_data("sometoken")

def test_decrypt_data_invalid_token():
    key = Fernet.generate_key().decode()
    os.environ["AUDIT_LOG_ENCRYPTION_KEY"] = key
    with pytest.raises(ValueError):
        encryption.decrypt_data("notbase64")
