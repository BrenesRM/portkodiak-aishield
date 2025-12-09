"""
Encryption utilities for PortKodiakAIShield.
Uses cryptography.fernet for symmetric encryption.
"""

from pathlib import Path
from cryptography.fernet import Fernet
from app.config import settings

KEY_FILE = settings.LOG_DIR.parent / "secret.key"

def _get_or_create_key() -> bytes:
    """Load existing key or generate a new one."""
    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()
    
    key = Fernet.generate_key()
    try:
        KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
        KEY_FILE.write_bytes(key)
    except PermissionError:
        # Fallback for dev mode/no admin rights
        return key
        
    return key

# Initialize cipher
try:
    _cipher = Fernet(_get_or_create_key())
except Exception:
    # Fallback if filesystem is readonly or other issues
    _cipher = Fernet(Fernet.generate_key())

def encrypt_data(data: str) -> str:
    """Encrypt string data."""
    if not data:
        return ""
    return _cipher.encrypt(data.encode()).decode()

def decrypt_data(token: str) -> str:
    """Decrypt token to string."""
    if not token:
        return ""
    try:
        return _cipher.decrypt(token.encode()).decode()
    except Exception:
        return ""
