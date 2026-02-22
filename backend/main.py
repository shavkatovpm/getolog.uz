import asyncio
import logging
import sys

import sentry_sdk
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from config import config
from core.bot_manager import BotManager
from core.scheduler import SchedulerService
from core.webhook_server import create_webhook_app
from bot.handlers import get_main_bot_router
from bot.middlewares.ban_check import BanCheckMiddleware
from bot.middlewares.rate_limit import RateLimitMiddleware
from moderator.handlers import get_moderator_router
from user_bot.handlers import get_user_bot_router
from user_bot.middlewares.ad_inject import AdInjectMiddleware
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
    logger.info("Redis connected")

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")

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

    # Set webhook for main bot
    main_webhook_url = f"{config.webhook_url}/main"
    await main_bot.set_webhook(main_webhook_url)
    logger.info(f"Main bot webhook: {main_webhook_url}")

    # Register all existing active bots
    await on_startup(bot_manager)

    # Scheduler
    scheduler = SchedulerService(bot_manager)
    scheduler.start()

    # Webhook server
    app = create_webhook_app(bot_manager, main_bot, main_dp)

    # Run
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", config.webhook_port)
    await site.start()

    logger.info(f"Server started on port {config.webhook_port}")

    try:
        await asyncio.Event().wait()  # Run forever
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


if __name__ == "__main__":
    asyncio.run(main())
