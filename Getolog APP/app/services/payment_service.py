"""To'lovni tasdiqlash/rad etish — bitta joyda, chunki buni ikki joydan
chaqirishadi: dashboard (`app/api/routes.py`) va bosh botdagi tezkor tugmalar
(`app/bot/handlers/payment_review.py`). Ikkalasi ham bir xil natijaga olib
kelishi (obunachi holati, invite havola, rad etish xabari) shart."""

from datetime import datetime, timezone

from aiogram.exceptions import TelegramAPIError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import channel_invite_keyboard
from app.db.models import (
    ChatType,
    Payment,
    PaymentStatus,
    Subscriber,
    SubscriberStatus,
    SubscriptionPlan,
)
from app.services.channel_service import create_join_request_link, get_bot_for_channel
from app.services.subscription_service import plan_duration


class PaymentReviewError(Exception):
    """To'lovni tasdiqlash/rad etib bo'lmaganda (masalan allaqachon ko'rib chiqilgan
    yoki bot hozircha ulanmagan) ko'tariladi."""


async def approve_payment(session: AsyncSession, payment: Payment) -> None:
    if payment.status != PaymentStatus.pending:
        raise PaymentReviewError("Bu to'lov allaqachon ko'rib chiqilgan")

    plan_result = await session.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == payment.plan_id)
    )
    plan = plan_result.scalar_one()
    channel, bot = await get_bot_for_channel(session, payment.channel_id)
    if bot is None:
        raise PaymentReviewError("Bot hozircha ulanmagan, birozdan keyin urinib ko'ring")

    now = datetime.now(timezone.utc)
    duration = plan_duration(plan)  # `None` = umrbod (lifetime) reja
    duration_minutes = int(duration.total_seconds() // 60) if duration is not None else 0

    sub_result = await session.execute(
        select(Subscriber).where(
            Subscriber.channel_id == payment.channel_id, Subscriber.user_id == payment.user_id
        )
    )
    subscriber = sub_result.scalar_one_or_none()
    # Hali kanalda faol turgan obunachi uzaytirsa (kanaldan chiqmasdan) — muddat
    # yo'qotilmasin: yangi muddat "hozir"dan emas, HOZIRGI tugash sanasidan
    # qo'shib hisoblanadi. Yangi yoki avval chiqarilgan/tugagan obunachi uchun
    # esa "hozir"dan boshlanadi va invite havola yuboriladi (u kanalda emas).
    is_renewal = subscriber is not None and subscriber.status == SubscriberStatus.active

    if subscriber is None:
        end_date = None if plan.is_lifetime else now + duration
        subscriber = Subscriber(
            channel_id=payment.channel_id,
            user_id=payment.user_id,
            username=payment.username,
            full_name=payment.full_name,
            end_date=end_date,
            duration_minutes=duration_minutes,
        )
        session.add(subscriber)
    else:
        # Ism/username o'zgargan bo'lishi mumkin — eng so'nggi to'lovdagisi bilan yangilaymiz.
        subscriber.username = payment.username
        subscriber.full_name = payment.full_name
        if plan.is_lifetime:
            end_date = None
        else:
            # Avvalgi obunachi allaqachon umrbod bo'lsa (`end_date is None`) —
            # muddatli rejaga "pasaytirilmaydi", "hozir"dan boshlab hisoblanadi.
            base = now if subscriber.end_date is None else max(subscriber.end_date, now)
            end_date = base + duration
        subscriber.status = SubscriberStatus.active
        subscriber.end_date = end_date
        subscriber.duration_minutes = duration_minutes
        subscriber.reminder_3d_sent = False
        subscriber.reminder_1d_sent = False
        subscriber.reminder_0d_sent = False

    payment.status = PaymentStatus.approved
    payment.approved_at = now
    await session.commit()

    if is_renewal:
        await bot.send_message(
            payment.user_id,
            "Obunangiz uzaytirildi ✅\n\n"
            + (
                "Endi obunangiz umrbod (muddatsiz)."
                if end_date is None
                else f"Yangi amal qilish muddati: {end_date.strftime('%d.%m.%Y %H:%M')} sanagacha."
            ),
        )
        return

    # Obunachi ilgari (bot orqali muddati tugab yoki admin tomonidan qo'lda)
    # kanaldan chiqarilgan bo'lishi mumkin — Telegram bunday odamni yangi
    # taklif havolasi orqali ham kiritmaydi ("havola muddati tugagan" deb
    # ko'rsatadi), shuning uchun invite havola yaratishdan oldin har doim
    # avval unban qilib qo'yamiz (banned bo'lmasa — hech narsa bo'lmaydi).
    try:
        await bot.unban_chat_member(
            chat_id=channel.telegram_channel_id, user_id=payment.user_id, only_if_banned=True
        )
    except TelegramAPIError:
        pass

    invite_link = await create_join_request_link(bot, channel.telegram_channel_id)
    is_group = channel.chat_type == ChatType.group
    kind = "guruhga" if is_group else "kanalga"
    expiry_line = (
        "Amal qilish muddati: Umrbod (muddatsiz)"
        if end_date is None
        else f"Amal qilish muddati: {end_date.strftime('%d.%m.%Y %H:%M')} sanagacha"
    )
    sent = await bot.send_message(
        payment.user_id,
        "To'lovingiz tasdiqlandi ✅\n\n"
        f"{expiry_line}\n\n"
        f"Pastdagi tugma orqali {kind} kiring. Tugmani bosgach so'rovingiz "
        "avtomatik tasdiqlanadi.\n\n"
        "Havola faqat sizga biriktirilgan — boshqa odamga bersangiz u kira olmaydi.",
        reply_markup=channel_invite_keyboard(invite_link, is_group=is_group),
    )
    # Xabar ID'si saqlanadi — obunachi haqiqatan ham qo'shilganda (Telegram'dan
    # kelgan `chat_member` hodisasi bilan tasdiqlangach) shu xabar "qo'shildingiz"
    # matniga tahrirlanadi (`on_member_joined`).
    payment.invite_message_id = sent.message_id
    await session.commit()


async def reject_payment(session: AsyncSession, payment: Payment, comment: str | None = None) -> None:
    if payment.status != PaymentStatus.pending:
        raise PaymentReviewError("Bu to'lov allaqachon ko'rib chiqilgan")

    payment.status = PaymentStatus.rejected
    await session.commit()

    _, bot = await get_bot_for_channel(session, payment.channel_id)
    if bot is None:
        return

    text = "Afsuski, to'lovingiz tasdiqlanmadi."
    text += f"\n\nAdmin izohi: {comment}" if comment else " Admin bilan bog'lanib ko'ring."
    await bot.send_message(payment.user_id, text)
