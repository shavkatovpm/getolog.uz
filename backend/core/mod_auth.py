"""Moderator password management — file-based persistent storage."""

import hashlib
import json
import os

_PASSWORD_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "mod_password.json")
_DEFAULT_PASSWORD = "1234"


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _ensure_file():
    os.makedirs(os.path.dirname(_PASSWORD_FILE), exist_ok=True)
    if not os.path.exists(_PASSWORD_FILE):
        with open(_PASSWORD_FILE, "w") as f:
            json.dump({"password_hash": _hash(_DEFAULT_PASSWORD)}, f)


def verify_password(password: str) -> bool:
    _ensure_file()
    with open(_PASSWORD_FILE) as f:
        data = json.load(f)
    return data["password_hash"] == _hash(password)


def change_password(new_password: str):
    _ensure_file()
    with open(_PASSWORD_FILE, "w") as f:
        json.dump({"password_hash": _hash(new_password)}, f)


# ── Redis session management ──

async def create_mod_session(telegram_id: int, ttl: int = 86400) -> bool:
    """Store moderator session in Redis after password verification. 24h TTL."""
    from core.cache import _redis
    if not _redis:
        return False
    try:
        await _redis.setex(f"mod_session:{telegram_id}", ttl, "1")
        return True
    except Exception:
        return False


async def check_mod_session(telegram_id: int) -> bool:
    """Check if moderator has an active session in Redis."""
    from core.cache import _redis
    if not _redis:
        return False
    try:
        result = await _redis.get(f"mod_session:{telegram_id}")
        return result is not None
    except Exception:
        return False


async def delete_mod_session(telegram_id: int):
    """Remove moderator session from Redis (logout)."""
    from core.cache import _redis
    if not _redis:
        return
    try:
        await _redis.delete(f"mod_session:{telegram_id}")
    except Exception:
        pass
