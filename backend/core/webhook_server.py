import logging
import os

from aiohttp import web

from api import setup_api_routes
from api.middleware import cors_middleware, rate_limit_middleware

logger = logging.getLogger(__name__)


def create_webhook_app(bot_manager, main_bot, main_dp) -> web.Application:
    """Create aiohttp app for handling webhooks, API, and Mini App."""
    app = web.Application(middlewares=[cors_middleware, rate_limit_middleware])

    # Store bot_manager for API routes
    app["bot_manager"] = bot_manager

    async def main_bot_webhook(request: web.Request):
        """Handle updates for the main Getolog bot."""
        from aiogram.types import Update

        try:
            data = await request.json()
            update = Update(**data)
            await main_dp.feed_update(main_bot, update)
        except Exception as e:
            logger.error(f"Main bot webhook error: {e}")
        return web.Response(status=200)

    async def user_bot_webhook(request: web.Request):
        """Handle updates for User Admin bots (routed by secret hash, not token)."""
        secret = request.match_info["secret"]
        try:
            data = await request.json()
            await bot_manager.handle_update(secret, data)
        except Exception as e:
            logger.error(f"User bot webhook error: {e}")
        return web.Response(status=200)

    async def health(request: web.Request):
        """Health check endpoint."""
        return web.json_response({
            "status": "ok",
            "active_bots": bot_manager.active_count,
        })

    # Webhook routes
    app.router.add_post("/webhook/main", main_bot_webhook)
    app.router.add_post("/webhook/{secret}", user_bot_webhook)
    app.router.add_get("/health", health)

    # API routes for Mini App
    setup_api_routes(app)

    # Serve Mini App static files
    webapp_dir = os.path.join(os.path.dirname(__file__), "..", "webapp")
    webapp_dir = os.path.abspath(webapp_dir)

    async def webapp_index(request: web.Request):
        return web.FileResponse(os.path.join(webapp_dir, "index.html"))

    app.router.add_get("/webapp", webapp_index)
    app.router.add_get("/webapp/", webapp_index)
    app.router.add_static("/webapp/", webapp_dir)

    return app
