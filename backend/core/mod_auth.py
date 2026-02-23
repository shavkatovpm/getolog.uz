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
