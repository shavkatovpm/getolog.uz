import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.keyboards.inline import payment_action_kb
from db.engine import async_session
from db.models import EndUser, UserBot, Channel
from services.payment_service import create_payment, approve_payment, get_payment_by_id
from services.subscription_service import create_subscription, get_active_subscription
from core.encryption import decrypt_card
from core.invite_link import create_invite_link
from user_bot.keyboards.inline import payment_method_kb
from utils.constants import PaymentStates
from sqlalchemy import select

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith("buy_ch_"))
async def buy_channel(callback: CallbackQuery, state: FSMContext):
    channel_id = int(callback.data.split("_")[2])

    bot_info = await callback.bot.get_me()
    async with async_session() as session:
        result = await session.execute(
            select(UserBot).where(UserBot.bot_username == bot_info.username)
        )
        user_bot = result.scalar_one_or_none()

        result = await session.execute(
            select(EndUser).where(
                EndUser.telegram_id == callback.from_user.id,
                EndUser.user_bot_id == user_bot.id,
            )
        )
        end_user = result.scalar_one_or_none()

        result = await session.execute(
            select(Channel).where(Channel.id == channel_id)
        )
        channel = result.scalar_one_or_none()

        if not channel or not end_user:
            await callback.answer("❌ Xatolik yuz berdi.")
            return

        # Check if already has active subscription
        existing = await get_active_subscription(session, end_user.id, channel.id)
        if existing:
            await callback.message.edit_text(
                "✅ Sizda allaqachon aktiv obuna mavjud!"
            )
            await callback.answer()
            return

    price_fmt = f"{float(channel.price):,.0f}".replace(",", " ")
    duration_text = {0: "umrbod", 1: "1 oy", 6: "6 oy", 12: "12 oy"}.get(
        channel.duration_months, f"{channel.duration_months} oy"
    )

    await state.update_data(
        channel_id=channel_id,
        end_user_id=end_user.id,
        user_bot_id=user_bot.id,
    )

    text = (
        f"📢 <b>{channel.title}</b>\n\n"
        f"💰 Narx: {price_fmt} UZS\n"
        f"📅 Muddat: {duration_text}\n\n"
        "To'lov usulini tanlang:"
    )
    await callback.message.edit_text(text, reply_markup=payment_method_kb())
    await callback.answer()


@router.callback_query(F.data == "pay_card")
async def pay_card(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    async with async_session() as session:
        result = await session.execute(
            select(UserBot).where(UserBot.id == data["user_bot_id"])
        )
        user_bot = result.scalar_one_or_none()

    card = decrypt_card(user_bot.card_number) if user_bot.card_number else "—"
    await callback.message.edit_text(
        f"💳 <b>Karta orqali to'lov</b>\n\n"
        f"Quyidagi karta raqamiga pul o'tkazing:\n\n"
        f"<code>{card}</code>\n\n"
        "✅ O'tkazgandan keyin <b>chek rasmini</b> yuboring (screenshot)."
    )
    await state.set_state(PaymentStates.waiting_screenshot)
    await callback.answer()


@router.message(PaymentStates.waiting_screenshot, F.photo)
async def process_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    photo = message.photo[-1]  # Highest resolution

    async with async_session() as session:
        result = await session.execute(
            select(Channel).where(Channel.id == data["channel_id"])
        )
        channel = result.scalar_one_or_none()

        # Create payment
        payment = await create_payment(
            session,
            end_user_id=data["end_user_id"],
            user_bot_id=data["user_bot_id"],
            channel_id=data["channel_id"],
            amount=float(channel.price),
            payment_method="card",
            screenshot_file_id=photo.file_id,
        )

        # Get user_bot for admin notification
        result = await session.execute(
            select(UserBot).where(UserBot.id == data["user_bot_id"])
        )
        user_bot = result.scalar_one_or_none()

    await message.answer(
        "✅ To'lov ma'lumotlari qabul qilindi!\n\n"
        "⏳ Admin tasdiqlashini kuting. Tasdiqlanganidan keyin invite link yuboriladi."
    )

    # Notify admin + collaborators
    amount_fmt = f"{float(channel.price):,.0f}".replace(",", " ")
    caption = (
        f"💳 <b>Yangi to'lov!</b>\n\n"
        f"👤 @{message.from_user.username or '—'}\n"
        f"💰 {amount_fmt} UZS\n"
        f"📢 {channel.title}\n"
        f"#{payment.id}"
    )
    notify_ids = [user_bot.admin.telegram_id]
    for collab in user_bot.collaborators:
        notify_ids.append(collab.telegram_id)

    for notify_id in notify_ids:
        try:
            await message.bot.send_photo(
                notify_id,
                photo=photo.file_id,
                caption=caption,
                reply_markup=payment_action_kb(payment.id),
            )
        except Exception as e:
            logger.error(f"Failed to notify {notify_id}: {e}")

    await state.clear()


@router.message(PaymentStates.waiting_screenshot)
async def wrong_screenshot(message: Message):
    await message.answer(
        "❌ Iltimos, <b>rasm</b> (screenshot) yuboring.\n"
        "Matnli xabar qabul qilinmaydi."
    )
