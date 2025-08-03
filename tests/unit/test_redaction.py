import pytest
from utils import redaction

def test_redact_email():
    s = 'Contact: alice@example.com, bob@foo.org.'
    out = redaction.redact_email(s)
    assert out == 'Contact: ***@***.com, ***@***.com'

def test_redact_ip():
    s = 'Login from 192.168.1.1 and 8.8.8.8.'
    out = redaction.redact_ip(s)
    assert out == 'Login from ***.***.***.*** and ***.***.***.***.'

def test_redact_token():
    s = 'Token: abcdef1234567890abcdef1234567890'
    out = redaction.redact_token(s)
    assert '[REDACTED_TOKEN]' in out
    # Should not redact short strings
    s2 = 'Short: 12345abcde'
    assert redaction.redact_token(s2) == s2

def test_redact_all():
    s = 'alice@example.com 10.0.0.1 token: 1234567890abcdef1234567890abcdef'
    out = redaction.redact_all(s)
    assert '***@***.com' in out
    assert '***.***.***.***' in out
    assert '[REDACTED_TOKEN]' in out

def test_is_redaction_enabled(monkeypatch):
    monkeypatch.setenv('AUDIT_LOG_REDACTION_ENABLED', 'true')
    assert redaction.is_redaction_enabled()
    monkeypatch.setenv('AUDIT_LOG_REDACTION_ENABLED', 'false')
    assert not redaction.is_redaction_enabled()
