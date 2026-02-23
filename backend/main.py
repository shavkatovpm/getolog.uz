import asyncio
import logging
import sys

import sentry_sdk
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import MenuButtonWebApp, WebAppInfo
from redis.asyncio import Redis

from config import config
from core.bot_manager import BotManager
from core.cache import init_cache
from core.scheduler import SchedulerService
from core.webhook_server import create_webhook_app
from bot.handlers import get_main_bot_router
from bot.middlewares.ban_check import BanCheckMiddleware
from bot.middlewares.rate_limit import RateLimitMiddleware
from moderator.handlers import get_moderator_router
from user_bot.handlers import get_user_bot_router
from db.engine import async_session, engine
from db.base import Base
from services.bot_service import get_all_active_bots

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def on_startup(bot_manager: BotManager):
    """Register all active bots on startup."""
    async with async_session() as session:
        active_bots = await get_all_active_bots(session)

    logger.info(f"Registering {len(active_bots)} active bots...")
    for user_bot in active_bots:
        result = await bot_manager.register_bot(user_bot.id, user_bot.bot_token)
        if result:
            logger.info(f"  ✅ @{user_bot.bot_username}")
        else:
            logger.warning(f"  ❌ @{user_bot.bot_username} — failed")

    logger.info(f"Bot registration complete: {bot_manager.active_count} active")


async def main():
    # Sentry
    if config.sentry_dsn:
        sentry_sdk.init(dsn=config.sentry_dsn, traces_sample_rate=0.1)
        logger.info("Sentry initialized")

    # Redis
    redis = Redis.from_url(config.redis_url, decode_responses=True)
    storage = RedisStorage(redis)
    init_cache(redis)
    logger.info("Redis connected")

    # Create database tables (dev fallback; use `alembic upgrade head` in production)
    if not config.is_production:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables ensured (dev mode)")

    # Main Getolog bot
    main_bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    main_dp = Dispatcher(storage=storage)

    # Include main bot routers
    main_dp.include_router(get_main_bot_router())
    main_dp.include_router(get_moderator_router())

    # Add middlewares to main bot
    main_dp.message.middleware(RateLimitMiddleware(redis))
    main_dp.message.middleware(BanCheckMiddleware())

    # User bot router (shared by all user bots)
    user_bot_router = get_user_bot_router()

    # Bot Manager
    bot_manager = BotManager(user_bot_router, storage)

    # Make bot_manager accessible in handlers via dispatcher data
    main_dp["bot_manager"] = bot_manager

    # Set Menu Button for Mini App (left side of input field)
    if config.server_url.startswith("https://"):
        try:
            await main_bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(
                    text="Dashboard",
                    web_app=WebAppInfo(url=f"{config.server_url}/webapp"),
                )
            )
            logger.info("Menu button set for Mini App")
        except Exception as e:
            logger.warning(f"Failed to set menu button: {e}")

    if config.is_production:
        # === PRODUCTION: Webhook mode ===
        main_webhook_url = f"{config.webhook_url}/main"
        await main_bot.set_webhook(main_webhook_url)
        logger.info(f"Main bot webhook: {main_webhook_url}")

        await on_startup(bot_manager)

        scheduler = SchedulerService(bot_manager)
        scheduler.start()

        app = create_webhook_app(bot_manager, main_bot, main_dp)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", config.webhook_port)
        await site.start()

        logger.info(f"Webhook server started on port {config.webhook_port}")

        try:
            await asyncio.Event().wait()
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            logger.info("Shutting down...")
            scheduler.stop()
            await bot_manager.shutdown()
            await main_bot.delete_webhook()
            await main_bot.session.close()
            await runner.cleanup()
            await redis.close()
            await engine.dispose()
            logger.info("Shutdown complete")
    else:
        # === DEVELOPMENT: Polling + Mini App server ===
        await main_bot.delete_webhook(drop_pending_updates=True)

        # Start webapp/API server in dev mode too
        app = create_webhook_app(bot_manager, main_bot, main_dp)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", config.webhook_port)
        await site.start()
        logger.info(f"Dev server started: http://localhost:{config.webhook_port}/webapp")

        # Register existing user bots
        await on_startup(bot_manager)

        # Start scheduler in dev mode too
        scheduler = SchedulerService(bot_manager)
        scheduler.start()

        # Run polling in parallel with the web server
        logger.info("Development mode: polling started")

        try:
            await main_dp.start_polling(main_bot)
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            scheduler.stop()
            await bot_manager.shutdown()
            await runner.cleanup()
            await main_bot.session.close()
            await redis.close()
            await engine.dispose()
            logger.info("Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
