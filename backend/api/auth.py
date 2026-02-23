import hashlib
import hmac
import json
import time
from urllib.parse import parse_qs, unquote

from aiohttp import web

from config import config
from db.engine import async_session
from services.admin_service import get_admin_by_telegram_id
from services.bot_service import get_bot_by_admin


def validate_init_data(init_data: str, bot_token: str) -> dict | None:
    """
    Validate Telegram WebApp initData using HMAC-SHA256.
    Returns parsed user data or None if invalid.
    """
    parsed = parse_qs(init_data, keep_blank_values=True)

    received_hash = parsed.get("hash", [None])[0]
    if not received_hash:
        return None

    # Check auth_date freshness (24h window)
    auth_date = parsed.get("auth_date", [None])[0]
    if auth_date and (time.time() - int(auth_date)) > 86400:
        return None

    # Build data-check-string (sorted, excluding hash)
    items = []
    for key, values in sorted(parsed.items()):
        if key == "hash":
            continue
        items.append(f"{key}={values[0]}")
    data_check_string = "\n".join(items)

    # Compute HMAC
    secret_key = hmac.new(
        b"WebAppData", bot_token.encode(), hashlib.sha256
    ).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return None

    user_data = parsed.get("user", [None])[0]
    if user_data:
        return json.loads(unquote(user_data))
    return None


async def get_authenticated_admin(request: web.Request) -> tuple[int, int] | None:
    """
    Validate request and return (admin_id, user_bot_id) or None.
    Frontend sends: Authorization: tma <initData>
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("tma "):
        return None

    init_data = auth_header[4:]
    user_data = validate_init_data(init_data, config.bot_token)
    if not user_data:
        return None

    telegram_id = user_data.get("id")
    if not telegram_id:
        return None

    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, telegram_id)
        if not admin or admin.banned:
            return None

        user_bot = await get_bot_by_admin(session, admin.id)
        if not user_bot:
            return None

        return admin.id, user_bot.id
