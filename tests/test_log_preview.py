import os
import tempfile
from app.services import log_preview
from utils import encryption

def test_load_logs_plaintext():
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        tmp.write('{"foo": "bar"}\n{"baz": 1}\n')
        tmp.flush()
        logs = log_preview.load_logs(tmp.name)
        assert any(l.get('foo') == 'bar' for l in logs)
        assert any(l.get('baz') == 1 for l in logs)
    os.remove(tmp.name)

def test_load_logs_encrypted(monkeypatch):
    key = encryption.Fernet.generate_key().decode()
    monkeypatch.setenv('AUDIT_LOG_ENCRYPTION_KEY', key)
    f = encryption.Fernet(key)
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        tmp.write(f.encrypt(b'{"foo": "bar"}').decode() + '\n')
        tmp.write(f.encrypt(b'{"baz": 1}').decode() + '\n')
        tmp.flush()
        logs = log_preview.load_logs(tmp.name)
        assert any(l.get('foo') == 'bar' for l in logs)
        assert any(l.get('baz') == 1 for l in logs)
    os.remove(tmp.name)
