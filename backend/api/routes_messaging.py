import logging

from aiohttp import web
from sqlalchemy import select

from api.auth import get_authenticated_admin
from db.engine import async_session
from db.models import EndUser

logger = logging.getLogger(__name__)


async def send_message(request: web.Request):
    """POST /api/users/{id}/message — send message to specific end user."""
    auth = await get_authenticated_admin(request)
    if not auth:
        return web.json_response({"error": "unauthorized"}, status=401)

    admin_id, user_bot_id = auth
    user_id = int(request.match_info["id"])

    body = await request.json()
    text = body.get("text", "").strip()
    if not text:
        return web.json_response({"error": "empty_message"}, status=400)
    if len(text) > 4000:
        return web.json_response({"error": "message_too_long"}, status=400)

    async with async_session() as session:
        result = await session.execute(
            select(EndUser).where(
                EndUser.id == user_id, EndUser.user_bot_id == user_bot_id
            )
        )
        end_user = result.scalar_one_or_none()
        if not end_user:
            return web.json_response({"error": "not_found"}, status=404)

    bot_manager = request.app.get("bot_manager")
    bot_instance = bot_manager.bots.get(user_bot_id) if bot_manager else None
    if not bot_instance:
        return web.json_response({"error": "bot_not_running"}, status=503)

    try:
        await bot_instance.send_message(
            end_user.telegram_id,
            f"📩 <b>Admin xabari:</b>\n\n{text}",
        )
    except Exception as e:
        logger.error(f"Failed to send message to user {user_id}: {e}")
        return web.json_response({"error": "send_failed"}, status=500)

    return web.json_response({"ok": True})


async def broadcast(request: web.Request):
    """POST /api/broadcast — send message to all end users."""
    auth = await get_authenticated_admin(request)
    if not auth:
        return web.json_response({"error": "unauthorized"}, status=401)

    admin_id, user_bot_id = auth

    body = await request.json()
    text = body.get("text", "").strip()
    if not text:
        return web.json_response({"error": "empty_message"}, status=400)
    if len(text) > 4000:
        return web.json_response({"error": "message_too_long"}, status=400)

    bot_manager = request.app.get("bot_manager")
    bot_instance = bot_manager.bots.get(user_bot_id) if bot_manager else None
    if not bot_instance:
        return web.json_response({"error": "bot_not_running"}, status=503)

    async with async_session() as session:
        result = await session.execute(
            select(EndUser).where(
                EndUser.user_bot_id == user_bot_id,
                EndUser.banned == False,
            )
        )
        users = result.scalars().all()

    sent = 0
    failed = 0
    for user in users:
        try:
            await bot_instance.send_message(
                user.telegram_id,
                f"📢 <b>Admin xabari:</b>\n\n{text}",
            )
            sent += 1
        except Exception:
            failed += 1

    return web.json_response({"ok": True, "sent": sent, "failed": failed})
