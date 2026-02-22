import logging

from aiohttp import web

logger = logging.getLogger(__name__)


def create_webhook_app(bot_manager, main_bot, main_dp) -> web.Application:
    """Create aiohttp app for handling webhooks."""
    app = web.Application()

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
        """Handle updates for User Admin bots."""
        token = request.match_info["token"]
        try:
            data = await request.json()
            await bot_manager.handle_update(token, data)
        except Exception as e:
            logger.error(f"User bot webhook error: {e}")
        return web.Response(status=200)

    async def health(request: web.Request):
        """Health check endpoint."""
        return web.json_response({
            "status": "ok",
            "active_bots": bot_manager.active_count,
        })

    app.router.add_post("/webhook/main", main_bot_webhook)
    app.router.add_post("/webhook/{token}", user_bot_webhook)
    app.router.add_get("/health", health)

    return app
