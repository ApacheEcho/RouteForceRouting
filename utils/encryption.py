import os
import base64
from cryptography.fernet import Fernet, InvalidToken


def get_fernet_key():
    key = os.getenv("AUDIT_LOG_ENCRYPTION_KEY")
    if not key:
        return None
    try:
        return Fernet(key)
    except Exception:
        return None

def encrypt_data(data: bytes) -> str:
    f = get_fernet_key()
    if not f:
        return None
    return f.encrypt(data).decode()

def decrypt_data(token: str) -> str:
    f = get_fernet_key()
    if not f:
        raise ValueError("No valid Fernet key found.")
    try:
        return f.decrypt(token.encode()).decode()
    except InvalidToken:
        raise ValueError("Invalid token or key.")

def decrypt_audit_log(path):
    """Decrypts an encrypted audit log file and prints each line as JSON."""
    f = get_fernet_key()
    if not f:
        print("[WARN] No valid Fernet key found. Cannot decrypt.")
        return
    with open(path) as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue
            try:
                print(f.decrypt(line.encode()).decode())
            except Exception as e:
                print(f"[ERROR] Could not decrypt line: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3 and sys.argv[1] == "decrypt":
        decrypt_audit_log(sys.argv[2])
    else:
        print("Usage: python utils/encryption.py decrypt <logfile>")
