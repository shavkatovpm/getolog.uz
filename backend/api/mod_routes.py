"""Moderator Mini App API endpoints."""

from aiohttp import web
from sqlalchemy import select

from api.mod_auth import get_authenticated_moderator
from core.cache import cache_get, cache_set
from core.mod_auth import verify_password, change_password
from db.engine import async_session
from db.models import UserAdmin, UserBot
from services.stats_service import get_moderator_stats
from services.admin_service import get_all_admins, ban_admin, unban_admin
from utils.constants import SubStatus


async def mod_get_stats(request: web.Request):
    """GET /api/mod/stats"""
    if not await get_authenticated_moderator(request):
        return web.json_response({"error": "unauthorized"}, status=401)

    cached = await cache_get("mod_stats")
    if cached:
        return web.json_response(cached)

    async with async_session() as session:
        stats = await get_moderator_stats(session)

    await cache_set("mod_stats", stats, ttl=30)
    return web.json_response(stats)


async def mod_list_admins(request: web.Request):
    """GET /api/mod/admins"""
    if not await get_authenticated_moderator(request):
        return web.json_response({"error": "unauthorized"}, status=401)

    async with async_session() as session:
        admins = await get_all_admins(session)
        data = []
        for a in admins:
            active_sub = next(
                (s for s in a.subscriptions if s.status == SubStatus.ACTIVE),
                None,
            )
            data.append({
                "id": a.id,
                "telegram_id": a.telegram_id,
                "username": a.username,
                "full_name": a.full_name,
                "banned": a.banned,
                "plan": active_sub.plan if active_sub else "free",
                "bot_count": len([b for b in a.bots if b.is_active]),
                "created_at": a.created_at.isoformat() if a.created_at else None,
            })

    return web.json_response({"admins": data})


async def mod_ban_admin(request: web.Request):
    """POST /api/mod/admins/{id}/ban"""
    if not await get_authenticated_moderator(request):
        return web.json_response({"error": "unauthorized"}, status=401)

    admin_id = int(request.match_info["id"])
    async with async_session() as session:
        ok = await ban_admin(session, admin_id)
    if not ok:
        return web.json_response({"error": "not_found"}, status=404)
    return web.json_response({"ok": True})


async def mod_unban_admin(request: web.Request):
    """POST /api/mod/admins/{id}/unban"""
    if not await get_authenticated_moderator(request):
        return web.json_response({"error": "unauthorized"}, status=401)

    admin_id = int(request.match_info["id"])
    async with async_session() as session:
        ok = await unban_admin(session, admin_id)
    if not ok:
        return web.json_response({"error": "not_found"}, status=404)
    return web.json_response({"ok": True})


async def mod_list_bots(request: web.Request):
    """GET /api/mod/bots"""
    if not await get_authenticated_moderator(request):
        return web.json_response({"error": "unauthorized"}, status=401)

    async with async_session() as session:
        result = await session.execute(
            select(UserBot)
            .where(UserBot.is_active == True)
            .order_by(UserBot.created_at.desc())
        )
        bots = result.scalars().all()
        data = []
        for b in bots:
            channels_info = [
                {"title": ch.title, "price": float(ch.price)}
                for ch in b.channels
            ]
            data.append({
                "id": b.id,
                "bot_username": b.bot_username,
                "owner_username": b.admin.username if b.admin else None,
                "owner_telegram_id": b.admin.telegram_id if b.admin else None,
                "channels": channels_info,
                "created_at": b.created_at.isoformat() if b.created_at else None,
            })

    return web.json_response({"bots": data})


async def mod_change_password(request: web.Request):
    """POST /api/mod/password"""
    if not await get_authenticated_moderator(request):
        return web.json_response({"error": "unauthorized"}, status=401)

    body = await request.json()
    current = body.get("current_password", "")
    new_pwd = body.get("new_password", "")

    if not verify_password(current):
        return web.json_response({"error": "wrong_password"}, status=400)
    if len(new_pwd) < 4:
        return web.json_response({"error": "too_short"}, status=400)

    change_password(new_pwd)
    return web.json_response({"ok": True})
