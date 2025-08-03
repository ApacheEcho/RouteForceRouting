import re
import os

def redact_email(text):
    return re.sub(r"[\w\.-]+@[\w\.-]+", "***@***.com", text)

def redact_ip(text):
    return re.sub(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", "***.***.***.***", text)

def redact_token(text):
    # Heuristic: 32+ alphanum chars, not part of a word
    return re.sub(r"\b[a-zA-Z0-9]{32,}\b", "[REDACTED_TOKEN]", text)

def redact_all(text):
    text = redact_email(text)
    text = redact_ip(text)
    text = redact_token(text)
    return text

def is_redaction_enabled():
    return os.getenv("AUDIT_LOG_REDACTION_ENABLED", "true").lower() == "true"

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3 and sys.argv[1] == "preview":
        with open(sys.argv[2]) as f:
            for line in f:
                print(redact_all(line.strip()))
    else:
        print("Usage: python utils/redaction.py preview <logfile>")
