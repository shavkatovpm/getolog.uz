"""GETOLOG serverining kirish nuqtasi.

Ishga tushganda:
1. GETOLOG bosh botini va bazadagi barcha admin botlarini registrga yuklaydi
   hamda ularning webhook manzilini (qayta) o'rnatadi — server qayta ishga
   tushganda ham hamma bot ishonchli tarzda ulangan bo'lishi uchun.
2. Eslatma/chiqarish fon vazifasini (scheduler) ishga tushiradi.
3. Barcha botlar uchun umumiy webhook serverini ko'taradi.
"""

import asyncio
import logging

from aiogram import Bot
from aiohttp import web
from sqlalchemy import select

from app.bot import registry
from app.bot.webhook_server import create_app
from app.config import settings
from app.db.base import async_session_factory
from app.db.models import Bot as BotModel
from app.services.encryption import decrypt_token
from app.services.scheduler import run_scheduler_loop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def _load_and_connect_bots() -> None:
    main_bot = Bot(token=settings.main_bot_token)
    registry.register_bot(main_bot)
    await main_bot.set_webhook(
        url=f"{settings.webhook_base_url}/webhook/{settings.main_bot_token}"
    )
    me = await main_bot.get_me()
    logger.info("Bosh bot ulandi: @%s", me.username)

    async with async_session_factory() as session:
        result = await session.execute(select(BotModel).where(BotModel.is_main.is_(False)))
        bot_rows = result.scalars().all()

    for bot_row in bot_rows:
        token = decrypt_token(bot_row.token_encrypted)
        bot = Bot(token=token)
        registry.register_bot(bot)
        try:
            await bot.set_webhook(url=f"{settings.webhook_base_url}/webhook/{token}")
        except Exception:  # noqa: BLE001 — bitta admin boti muammosi boshqalarga xalaqit bermasin
            logger.exception("Admin boti @%s uchun webhook o'rnatilmadi", bot_row.username)

    logger.info("Jami %d ta admin boti yuklandi", len(bot_rows))


async def main() -> None:
    await _load_and_connect_bots()

    scheduler_task = asyncio.create_task(run_scheduler_loop())

    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=settings.webhook_server_port)
    await site.start()
    logger.info("Webhook server %s portda ishga tushdi", settings.webhook_server_port)

    try:
        await asyncio.Event().wait()  # server abadiy ishlab turadi
    finally:
        scheduler_task.cancel()
        for bot in registry.all_bots():
            await bot.session.close()
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
