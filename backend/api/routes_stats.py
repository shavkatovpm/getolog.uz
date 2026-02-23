from aiohttp import web

from api.auth import get_authenticated_admin
from core.cache import cache_get, cache_set
from db.engine import async_session
from services.stats_service import get_admin_stats


async def get_stats(request: web.Request):
    auth = await get_authenticated_admin(request)
    if not auth:
        return web.json_response({"error": "unauthorized"}, status=401)

    admin_id, user_bot_id = auth

    # Try cache first (30 second TTL)
    cache_key = f"stats:{user_bot_id}"
    cached = await cache_get(cache_key)
    if cached:
        return web.json_response(cached)

    async with async_session() as session:
        stats = await get_admin_stats(session, user_bot_id)

    await cache_set(cache_key, stats, ttl=30)
    return web.json_response(stats)
