"""Fon vazifasi: eslatmalar (3/1/0 kun) va muddati tugagan obunachilarni chiqarish.

Interval asosida ishlaydi (har necha daqiqada bir marta tekshiradi). Server
vaqtincha to'xtab qolsa ham keyingi ishga tushishda hech kim o'tkazib
yuborilmaydi — chunki shartlar aniq vaqtga emas, holatga (flag / end_date)
qaraydi. Shu "catch-up" mantiq tufayli qayta ishga tushirish xavfsiz.
"""

import asyncio
import logging
from datetime import date, datetime

from sqlalchemy import select

from app.db.base import async_session_factory
from app.db.models import Subscriber, SubscriberStatus
from app.services.channel_service import get_bot_for_channel, remove_subscriber

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 600  # har 10 daqiqada bir tekshiradi
KICK_HOUR = 23
KICK_MINUTE = 55  # shu vaqtdan keyin kunlik "chiqarish" tekshiruvi ishlaydi


async def run_scheduler_loop() -> None:
    """Server ishlab turgan davomida to'xtovsiz aylanadigan fon tsikli."""
    while True:
        try:
            await _send_due_reminders()
            await _kick_expired_subscribers_if_time()
        except Exception:  # noqa: BLE001 — fon vazifasi hech qachon to'liq to'xtamasligi kerak
            logger.exception("Scheduler tsiklida xatolik yuz berdi")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


async def _send_due_reminders() -> None:
    async with async_session_factory() as session:
        today = date.today()
        result = await session.execute(
            select(Subscriber).where(Subscriber.status == SubscriberStatus.active)
        )
        subscribers = result.scalars().all()

        for sub in subscribers:
            days_left = (sub.end_date - today).days

            if days_left == 3 and not sub.reminder_3d_sent:
                text = "GETOLOG: obunangiz 3 kundan keyin tugaydi. Vaqtida uzaytirib qo'ying!"
                flag = "reminder_3d_sent"
            elif days_left == 1 and not sub.reminder_1d_sent:
                text = "GETOLOG: obunangiz ertaga tugaydi. Vaqtida uzaytirib qo'ying!"
                flag = "reminder_1d_sent"
            elif days_left <= 0 and not sub.reminder_0d_sent:
                text = "GETOLOG: obunangiz bugun tugaydi."
                flag = "reminder_0d_sent"
            else:
                continue

            _, bot = await get_bot_for_channel(session, sub.channel_id)
            if bot is not None:
                try:
                    await bot.send_message(sub.user_id, text)
                except Exception:  # noqa: BLE001 — bitta obunachiga yetkazilmasa ham davom etadi
                    logger.warning("Obunachi %s ga eslatma yuborib bo'lmadi", sub.user_id)
            setattr(sub, flag, True)

        await session.commit()


async def _kick_expired_subscribers_if_time() -> None:
    now = datetime.now()
    if (now.hour, now.minute) < (KICK_HOUR, KICK_MINUTE):
        return  # hali vaqti kelmagan — keyingi tsiklda qayta tekshiriladi

    async with async_session_factory() as session:
        today = date.today()
        result = await session.execute(
            select(Subscriber).where(
                Subscriber.status == SubscriberStatus.active, Subscriber.end_date <= today
            )
        )
        expired = result.scalars().all()

        for sub in expired:
            channel, bot = await get_bot_for_channel(session, sub.channel_id)
            if bot is None:
                continue
            try:
                await remove_subscriber(bot, channel.telegram_channel_id, sub.user_id)
            except Exception:  # noqa: BLE001 — bitta obunachida xato bo'lsa ham davom etadi
                logger.warning("Obunachi %s ni kanaldan chiqarib bo'lmadi", sub.user_id)
                continue
            sub.status = SubscriberStatus.expired

        await session.commit()
