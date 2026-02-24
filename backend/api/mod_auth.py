"""Moderator API authentication — validates initData + Redis session."""

from aiohttp import web

from api.auth import validate_init_data
from config import config
from core.mod_auth import check_mod_session


async def get_authenticated_moderator(request: web.Request) -> int | None:
    """
    Validate request and return moderator telegram_id or None.
    Frontend sends: Authorization: tma <initData>
    Requires both valid initData AND an active Redis session from /modlog.
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

    if telegram_id not in config.moderator_ids:
        return None

    if not await check_mod_session(telegram_id):
        return None

    return telegram_id
