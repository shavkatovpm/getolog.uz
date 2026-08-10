"""Fon vazifasi: eslatmalar va muddati tugagan obunachilarni chiqarish.

Interval asosida ishlaydi (har necha soniyada bir marta tekshiradi). Server
vaqtincha to'xtab qolsa ham keyingi ishga tushishda hech kim o'tkazib
yuborilmaydi — chunki shartlar aniq vaqtga emas, holatga (flag / end_date)
qaraydi. Shu "catch-up" mantiq tufayli qayta ishga tushirish xavfsiz.

Eslatma chegaralari obunaning umumiy uzunligiga (`duration_minutes`) qarab
moslashadi: oddiy oylik tariflarda "3 kun/1 kun" oldin, juda qisqa (masalan
test uchun 5 daqiqalik) tariflarda esa umumiy muddatga nisbatan foiz asosida
hisoblanadi — aks holda "3 kun oldin" degan chegara hech qachon ishlamas edi.

Muddati tugab, obunachi haqiqatan HAM kanaldan chiqarilgan payt uchun alohida,
aniq xabar bor (`_kick_expired_subscribers` ichida) — oldindan ogohlantirish
("tez orada tugaydi") bilan chalkashtirilmasligi uchun ular ikkita mustaqil
bosqich: oldindan (uzoq/yaqin) va chiqarilgan payt (kick).
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot import registry
from app.bot.keyboards import TARIFF_LABELS, plan_choice_keyboard
from app.config import settings
from app.db.base import async_session_factory
from app.db.models import Admin, ChatType, Subscriber, SubscriberStatus, SubscriptionPlan
from app.services.channel_service import get_bot_for_channel, remove_subscriber
from app.services.subscription_service import TARIFF_LIMITS, count_billable_subscribers

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 60  # har daqiqada bir tekshiradi (qisqa test tariflar ham o'z vaqtida ishlashi uchun)


def _reminder_thresholds(duration_minutes: int) -> tuple[timedelta, timedelta]:
    """(uzoq, yaqin) — oldindan ogohlantirish uchun "necha vaqt qoldi" chegaralari."""
    total = timedelta(minutes=duration_minutes)
    if total >= timedelta(days=4):
        return timedelta(days=3), timedelta(days=1)
    # Juda qisqa (test) tariflar uchun umumiy muddatga nisbatan foizli chegaralar.
    return total * 0.6, total * 0.2


async def run_scheduler_loop() -> None:
    """Server ishlab turgan davomida to'xtovsiz aylanadigan fon tsikli."""
    while True:
        try:
            await _send_due_reminders()
            await _kick_expired_subscribers()
            await _check_tariff_limits()
        except Exception:  # noqa: BLE001 — fon vazifasi hech qachon to'liq to'xtamasligi kerak
            logger.exception("Scheduler tsiklida xatolik yuz berdi")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


async def _send_due_reminders() -> None:
    async with async_session_factory() as session:
        now = datetime.now(timezone.utc)
        result = await session.execute(
            select(Subscriber).where(
                Subscriber.status == SubscriberStatus.active, Subscriber.end_date.is_not(None)
            )
        )
        subscribers = result.scalars().all()

        for sub in subscribers:
            time_left = sub.end_date - now
            far, near = _reminder_thresholds(sub.duration_minutes)

            if time_left <= near and not sub.reminder_1d_sent:
                stage = "tez orada tugaydi. Vaqtida uzaytirib qo'ying!"
                flag = "reminder_1d_sent"
            elif time_left <= far and not sub.reminder_3d_sent:
                stage = "muddati yaqinlashmoqda. Vaqtida uzaytirib qo'ying!"
                flag = "reminder_3d_sent"
            else:
                continue

            channel, bot = await get_bot_for_channel(session, sub.channel_id)
            if bot is not None:
                kind = "guruhi" if channel.chat_type == ChatType.group else "kanali"
                text = f"«{channel.title}» {kind} bo'yicha obunangiz {stage}"
                # Eslatma ostida tarif tugmalari — obunachi shu yerdan uzaytirishni
                # bosib, mavjud "choose_plan" oqimi orqali (chek -> admin tasdig'i)
                # to'lov qila oladi. `approve_payment` bu holatda muddatni HOZIRGI
                # tugash sanasiga qo'shib hisoblaydi (yo'qotmasdan uzaytiradi).
                plans_result = await session.execute(
                    select(SubscriptionPlan).where(
                        SubscriptionPlan.channel_id == sub.channel_id,
                        SubscriptionPlan.active.is_(True),
                    )
                )
                plans = plans_result.scalars().all()
                try:
                    await bot.send_message(
                        sub.user_id,
                        text,
                        reply_markup=plan_choice_keyboard(plans) if plans else None,
                    )
                except Exception:  # noqa: BLE001 — bitta obunachiga yetkazilmasa ham davom etadi
                    logger.warning("Obunachi %s ga eslatma yuborib bo'lmadi", sub.user_id)
            setattr(sub, flag, True)

        await session.commit()


async def _kick_expired_subscribers() -> None:
    async with async_session_factory() as session:
        now = datetime.now(timezone.utc)
        result = await session.execute(
            select(Subscriber).where(
                Subscriber.status == SubscriberStatus.active,
                Subscriber.end_date.is_not(None),
                Subscriber.end_date <= now,
            )
        )
        expired = result.scalars().all()

        for sub in expired:
            channel, bot = await get_bot_for_channel(session, sub.channel_id)
            if bot is None:
                continue
            already_gone = False
            try:
                await remove_subscriber(bot, channel.telegram_channel_id, sub.user_id)
            except TelegramBadRequest as exc:
                if "USER_NOT_PARTICIPANT" not in str(exc):
                    logger.warning("Obunachi %s ni kanaldan chiqarib bo'lmadi: %s", sub.user_id, exc)
                    continue
                # Obunachi allaqachon kanal/guruhda emas (masalan o'zi chiqib ketgan) —
                # bu ham muvaffaqiyat hisoblanadi, aks holda har daqiqa qayta-qayta
                # urinib, hech qachon holati yopilmasdi.
                already_gone = True
            except Exception as exc:  # noqa: BLE001 — bitta obunachida xato bo'lsa ham davom etadi
                logger.warning("Obunachi %s ni kanaldan chiqarib bo'lmadi: %s", sub.user_id, exc)
                continue
            sub.status = SubscriberStatus.expired

            plans_result = await session.execute(
                select(SubscriptionPlan).where(
                    SubscriptionPlan.channel_id == sub.channel_id,
                    SubscriptionPlan.active.is_(True),
                )
            )
            plans = plans_result.scalars().all()
            try:
                if already_gone:
                    text = "Obunangiz muddati tugadi.\n\nQayta kirish uchun tarifni tanlang:"
                else:
                    kind = "guruhidan" if channel.chat_type == ChatType.group else "kanalidan"
                    text = (
                        f"Siz «{channel.title}» {kind} chiqarildingiz.\n\n"
                        "Qayta kirish uchun tarifni tanlang:"
                    )
                await bot.send_message(
                    sub.user_id,
                    text,
                    reply_markup=plan_choice_keyboard(plans) if plans else None,
                )
            except Exception:  # noqa: BLE001 — xabar yetmasa ham obunachi allaqachon chiqarilgan
                logger.warning("Obunachi %s ga chiqarilganlik xabarini yuborib bo'lmadi", sub.user_id)

        await session.commit()


async def _notify_admin(admin: Admin, text: str) -> None:
    main_bot = registry.get_main_bot()
    try:
        await main_bot.send_message(admin.telegram_id, text)
    except Exception:  # noqa: BLE001 — bitta adminga yetmasa ham davom etadi
        logger.warning("Admin %s ga tarif ogohlantirishini yuborib bo'lmadi", admin.id)


async def _check_tariff_limits() -> None:
    """Har bir adminning faol obunachilar soni joriy tarif limitidan oshib
    ketganini kuzatadi — bu FAQAT ESLATMA: bot/obunachi qabul qilish hech qachon
    bloklanmaydi, faqat dashboard'da ogohlantirish ko'rinadi va limitdan birinchi
    marta oshganda adminga bir martalik xabar yuboriladi (`Admin.limit_exceeded_at`).
    Obunachi soni limit ostiga qaytsa (yoki tarif oshirilsa), belgi tozalanadi —
    keyingi safar yana oshsa, yangi eslatma qayta yuboriladi."""
    async with async_session_factory() as session:
        result = await session.execute(select(Admin))
        admins = result.scalars().all()
        today = datetime.now(timezone.utc).date()

        for admin in admins:
            limit = TARIFF_LIMITS[admin.tariff_plan]
            if limit is None:
                continue
            active = await count_billable_subscribers(session, admin.id)

            if active <= limit:
                if admin.limit_exceeded_at is not None:
                    admin.limit_exceeded_at = None
                continue

            if admin.limit_exceeded_at is None:
                admin.limit_exceeded_at = today
                await _notify_admin(
                    admin,
                    f"⚠️ Faol obunachilar soni ({active}) {TARIFF_LABELS[admin.tariff_plan]} "
                    f"tarifidagi limitdan ({limit}) oshib ketdi.\n\n"
                    "Bot ishlashda davom etadi — bu shunchaki eslatma. Ko'proq "
                    "obunachi qabul qilish uchun tarifingizni oshirishingiz mumkin: "
                    f"@{settings.support_username} ga yozing.",
                )

        await session.commit()
