from cryptography.fernet import Fernet

from config import config

_fernet = Fernet(config.encryption_key.encode()) if config.encryption_key else None


def encrypt_token(token: str) -> str:
    if not _fernet:
        raise RuntimeError("ENCRYPTION_KEY is not set")
    return _fernet.encrypt(token.encode()).decode()


def decrypt_token(encrypted: str) -> str:
    if not _fernet:
        raise RuntimeError("ENCRYPTION_KEY is not set")
    return _fernet.decrypt(encrypted.encode()).decode()


def encrypt_card(card: str) -> str:
    if not _fernet:
        raise RuntimeError("ENCRYPTION_KEY is not set")
    return _fernet.encrypt(card.encode()).decode()


def decrypt_card(encrypted: str) -> str:
    """Decrypt card number. Returns as-is if not encrypted (legacy data)."""
    if not _fernet:
        raise RuntimeError("ENCRYPTION_KEY is not set")
    try:
        return _fernet.decrypt(encrypted.encode()).decode()
    except Exception:
        # Legacy plain-text card — return as-is
        return encrypted
