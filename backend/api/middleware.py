import time
from collections import defaultdict

from aiohttp import web

from config import config

# Telegram WebApp always sends Origin: https://web.telegram.org
_ALLOWED_ORIGINS = {
    "https://web.telegram.org",
}

# In development, also allow local origins
if not config.is_production:
    _ALLOWED_ORIGINS.update({
        f"http://localhost:{config.webhook_port}",
        f"https://localhost:{config.webhook_port}",
        config.server_url,
    })


@web.middleware
async def cors_middleware(request, handler):
    origin = request.headers.get("Origin", "")

    if request.method == "OPTIONS":
        response = web.Response()
    else:
        response = await handler(request)

    if origin in _ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

    return response


# Simple in-memory rate limiter for API endpoints
_rate_buckets: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT = 30  # requests
_RATE_WINDOW = 60  # seconds


@web.middleware
async def rate_limit_middleware(request, handler):
    # Only rate-limit /api/ routes
    if not request.path.startswith("/api/"):
        return await handler(request)

    # Key by IP (or forwarded IP)
    ip = request.headers.get("X-Forwarded-For", request.remote) or "unknown"
    key = f"{ip}"
    now = time.monotonic()

    # Clean old entries
    bucket = _rate_buckets[key]
    _rate_buckets[key] = [t for t in bucket if now - t < _RATE_WINDOW]

    if len(_rate_buckets[key]) >= _RATE_LIMIT:
        return web.json_response(
            {"error": "Too many requests. Try again later."},
            status=429,
        )

    _rate_buckets[key].append(now)
    return await handler(request)
