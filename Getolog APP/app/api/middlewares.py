"""aiohttp middleware'lari: DB sessiyasi, CORS va JWT autentifikatsiya (faqat /api/* uchun).

Webhook yo'llari (`/webhook/{token}`) bu middleware'lardan ta'sirlanmaydi —
har biri o'z yo'lini `request.path` orqali tekshiradi.
"""

from aiohttp import web

from app.api.auth import decode_jwt
from app.config import settings
from app.db.base import async_session_factory

PUBLIC_API_PATHS = {"/api/auth/telegram-code", "/api/auth/telegram-webapp"}

# Dashboard prod manzilidan tashqari, mahalliy Next.js dev serveridan ham
# so'rov yuborish mumkin bo'lishi uchun (haqiqiy origin reflect qilinadi,
# wildcard emas — bu standart xavfsiz CORS pattern).
ALLOWED_ORIGINS = {settings.dashboard_origin, "http://localhost:3000"}


@web.middleware
async def db_session_middleware(request: web.Request, handler):
    async with async_session_factory() as session:
        request["session"] = session
        return await handler(request)


@web.middleware
async def cors_middleware(request: web.Request, handler):
    is_api = request.path.startswith("/api/")

    if is_api and request.method == "OPTIONS":
        response: web.StreamResponse = web.Response()
    else:
        try:
            response = await handler(request)
        except web.HTTPException as exc:
            response = exc

    if is_api:
        origin = request.headers.get("Origin")
        if origin in ALLOWED_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
    return response


@web.middleware
async def auth_middleware(request: web.Request, handler):
    if not request.path.startswith("/api/") or request.path in PUBLIC_API_PATHS:
        return await handler(request)
    if request.method == "OPTIONS":
        return await handler(request)

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise web.HTTPUnauthorized(text="Token kerak")

    token = auth_header.removeprefix("Bearer ")
    try:
        claims = decode_jwt(token)
    except Exception as exc:
        raise web.HTTPUnauthorized(text="Token yaroqsiz") from exc

    request["auth"] = claims
    return await handler(request)
