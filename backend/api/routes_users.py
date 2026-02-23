from aiohttp import web
from sqlalchemy import select

from api.auth import get_authenticated_admin
from db.engine import async_session
from db.models import EndUser


async def list_users(request: web.Request):
    """GET /api/users"""
    auth = await get_authenticated_admin(request)
    if not auth:
        return web.json_response({"error": "unauthorized"}, status=401)

    admin_id, user_bot_id = auth

    async with async_session() as session:
        result = await session.execute(
            select(EndUser)
            .where(EndUser.user_bot_id == user_bot_id)
            .order_by(EndUser.created_at.desc())
            .limit(100)
        )
        users = result.scalars().all()
        data = [{
            "id": u.id,
            "telegram_id": u.telegram_id,
            "username": u.username,
            "language": u.language,
            "banned": u.banned,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        } for u in users]

    return web.json_response({"users": data})


async def ban_user(request: web.Request):
    """POST /api/users/{id}/ban"""
    auth = await get_authenticated_admin(request)
    if not auth:
        return web.json_response({"error": "unauthorized"}, status=401)

    admin_id, user_bot_id = auth
    user_id = int(request.match_info["id"])

    async with async_session() as session:
        result = await session.execute(
            select(EndUser).where(
                EndUser.id == user_id, EndUser.user_bot_id == user_bot_id
            )
        )
        end_user = result.scalar_one_or_none()
        if not end_user:
            return web.json_response({"error": "not_found"}, status=404)

        end_user.banned = True
        await session.commit()

    # Notify user
    bot_manager = request.app.get("bot_manager")
    bot_instance = bot_manager.bots.get(user_bot_id) if bot_manager else None
    if bot_instance:
        try:
            await bot_instance.send_message(
                end_user.telegram_id,
                "⛔ Siz admin tomonidan <b>bloklangansiz</b>.\n"
                "Botdan foydalana olmaysiz.",
            )
        except Exception:
            pass

    return web.json_response({"ok": True})


async def unban_user(request: web.Request):
    """POST /api/users/{id}/unban"""
    auth = await get_authenticated_admin(request)
    if not auth:
        return web.json_response({"error": "unauthorized"}, status=401)

    admin_id, user_bot_id = auth
    user_id = int(request.match_info["id"])

    async with async_session() as session:
        result = await session.execute(
            select(EndUser).where(
                EndUser.id == user_id, EndUser.user_bot_id == user_bot_id
            )
        )
        end_user = result.scalar_one_or_none()
        if not end_user:
            return web.json_response({"error": "not_found"}, status=404)

        end_user.banned = False
        await session.commit()

    # Notify user
    bot_manager = request.app.get("bot_manager")
    bot_instance = bot_manager.bots.get(user_bot_id) if bot_manager else None
    if bot_instance:
        try:
            await bot_instance.send_message(
                end_user.telegram_id,
                "✅ Siz admin tomonidan <b>blokdan chiqarildingiz</b>.\n"
                "Botdan qayta foydalanishingiz mumkin.",
            )
        except Exception:
            pass

    return web.json_response({"ok": True})
