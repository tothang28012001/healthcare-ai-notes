import os
import json
from cryptography.fernet import Fernet
from fastapi import HTTPException

# Load Key (Fail fast if missing)
ENCRYPTION_KEY = os.getenv("STORAGE_ENCRYPTION_KEY")

# In-memory cipher instance
_cipher = None

def get_cipher():
    global _cipher
    if _cipher:
        return _cipher
    
    if not ENCRYPTION_KEY:
        # Critical startup failure if key is missing (Configuration Hardening)
        raise RuntimeError("FATAL: STORAGE_ENCRYPTION_KEY is missing. System cannot start safely.")
    
    try:
        _cipher = Fernet(ENCRYPTION_KEY.encode())
        return _cipher
    except Exception as e:
        raise RuntimeError(f"FATAL: Invalid STORAGE_ENCRYPTION_KEY. {e}")

# --- Secure File Operations ---

def secure_write_bytes(path: str, data: bytes):
    """Encrypts data before writing to disk."""
    cipher = get_cipher()
    encrypted_data = cipher.encrypt(data)
    with open(path, "wb") as f:
        f.write(encrypted_data)

def secure_read_bytes(path: str) -> bytes:
    """Reads file and decrypts it. Falls back to plain text if decryption fails (migration support)."""
    cipher = get_cipher()
    with open(path, "rb") as f:
        raw_data = f.read()
    
    try:
        return cipher.decrypt(raw_data)
    except Exception:
        # Check if file is valid JSON or plain text (legacy/unencrypted)
        # In a strict environment, we might reject this. For Phase 9 transition, we allow it.
        return raw_data

def secure_write_json(path: str, data: dict):
    """Encrypts a JSON object and writes it."""
    json_str = json.dumps(data, indent=2)
    secure_write_bytes(path, json_str.encode('utf-8'))

def secure_read_json(path: str) -> dict:
    """Reads and decrypts a JSON object."""
    decrypted_bytes = secure_read_bytes(path)
    return json.loads(decrypted_bytes.decode('utf-8'))