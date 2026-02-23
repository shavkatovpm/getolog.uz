from aiohttp import web

from api.auth import get_authenticated_admin
from core.cache import cache_get, cache_set, cache_delete
from core.encryption import decrypt_card
from db.engine import async_session
from services.bot_service import get_bot_by_id, get_channels_by_bot, update_bot_settings


async def get_settings(request: web.Request):
    """GET /api/settings"""
    auth = await get_authenticated_admin(request)
    if not auth:
        return web.json_response({"error": "unauthorized"}, status=401)

    admin_id, user_bot_id = auth

    cache_key = f"settings:{user_bot_id}"
    cached = await cache_get(cache_key)
    if cached:
        return web.json_response(cached)

    async with async_session() as session:
        bot = await get_bot_by_id(session, user_bot_id)
        channels = await get_channels_by_bot(session, user_bot_id)

        channel_data = None
        if channels:
            ch = channels[0]
            channel_data = {
                "id": ch.id,
                "title": ch.title,
                "price": float(ch.price),
                "duration_months": ch.duration_months,
            }

    data = {
        "bot_username": bot.bot_username,
        "welcome_message": bot.welcome_message,
        "card_number": decrypt_card(bot.card_number) if bot.card_number else None,
        "channel": channel_data,
    }
    await cache_set(cache_key, data, ttl=30)
    return web.json_response(data)


async def update_settings(request: web.Request):
    """PUT /api/settings"""
    auth = await get_authenticated_admin(request)
    if not auth:
        return web.json_response({"error": "unauthorized"}, status=401)

    admin_id, user_bot_id = auth
    body = await request.json()

    async with async_session() as session:
        await update_bot_settings(
            session,
            bot_id=user_bot_id,
            welcome_message=body.get("welcome_message"),
            card_number=body.get("card_number"),
        )

        new_price = body.get("price")
        if new_price is not None:
            channels = await get_channels_by_bot(session, user_bot_id)
            if channels:
                channels[0].price = new_price
                await session.commit()

    await cache_delete(f"settings:{user_bot_id}")
    return web.json_response({"ok": True})
