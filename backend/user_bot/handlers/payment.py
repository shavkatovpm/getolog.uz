import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.keyboards.inline import payment_action_kb
from bot.middlewares.i18n import get_text
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


async def _get_end_user_lang(bot_username: str, telegram_id: int) -> str:
    """Get end user language from DB."""
    async with async_session() as session:
        result = await session.execute(
            select(EndUser).join(UserBot).where(
                EndUser.telegram_id == telegram_id,
                UserBot.bot_username == bot_username,
            )
        )
        eu = result.scalar_one_or_none()
        return (eu.language if eu else "uz") or "uz"


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
            await callback.answer(get_text("error", "uz"))
            return

        lang = end_user.language or "uz"
        _ = lambda key: get_text(key, lang)

        # Check if already has active subscription
        existing = await get_active_subscription(session, end_user.id, channel.id)
        if existing:
            await callback.message.edit_text(_("subscription_active"))
            await callback.answer()
            return

    price_fmt = f"{float(channel.price):,.0f}".replace(",", " ")
    duration_text = {
        0: _("duration_lifetime"), 1: _("duration_1m"),
        6: _("duration_6m"), 12: _("duration_12m"),
    }.get(channel.duration_months, f"{channel.duration_months}")

    await state.update_data(
        channel_id=channel_id,
        end_user_id=end_user.id,
        user_bot_id=user_bot.id,
    )

    text = _("channel_info").format(
        title=channel.title, price=price_fmt, duration=duration_text
    ) + _("payment_select_method")
    await callback.message.edit_text(text, reply_markup=payment_method_kb(lang=lang))
    await callback.answer()


@router.callback_query(F.data == "pay_card")
async def pay_card(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bot_info = await callback.bot.get_me()
    lang = await _get_end_user_lang(bot_info.username, callback.from_user.id)
    _ = lambda key: get_text(key, lang)

    async with async_session() as session:
        result = await session.execute(
            select(UserBot).where(UserBot.id == data["user_bot_id"])
        )
        user_bot = result.scalar_one_or_none()

    if not user_bot or not user_bot.card_number:
        await callback.message.edit_text(_("payment_settings_missing"))
        await state.clear()
        await callback.answer()
        return

    card = decrypt_card(user_bot.card_number)
    await callback.message.edit_text(
        _("payment_card_info").format(card=card),
    )
    await state.set_state(PaymentStates.waiting_screenshot)
    await callback.answer()


@router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback: CallbackQuery, state: FSMContext):
    bot_info = await callback.bot.get_me()
    lang = await _get_end_user_lang(bot_info.username, callback.from_user.id)
    await state.clear()
    await callback.message.edit_text(get_text("payment_cancelled", lang))
    await callback.answer()


@router.message(PaymentStates.waiting_screenshot, F.photo)
async def process_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    photo = message.photo[-1]
    bot_info = await message.bot.get_me()
    lang = await _get_end_user_lang(bot_info.username, message.from_user.id)
    _ = lambda key: get_text(key, lang)

    async with async_session() as session:
        result = await session.execute(
            select(Channel).where(Channel.id == data["channel_id"])
        )
        channel = result.scalar_one_or_none()

        payment = await create_payment(
            session,
            end_user_id=data["end_user_id"],
            user_bot_id=data["user_bot_id"],
            channel_id=data["channel_id"],
            amount=float(channel.price),
            payment_method="card",
            screenshot_file_id=photo.file_id,
        )

        result = await session.execute(
            select(UserBot).where(UserBot.id == data["user_bot_id"])
        )
        user_bot = result.scalar_one_or_none()

    await message.answer(_("payment_received"))

    # Notify admin + collaborators — use admin's language
    admin_lang = user_bot.admin.language or "uz"
    amount_fmt = f"{float(channel.price):,.0f}".replace(",", " ")
    caption = get_text("new_payment_notification", admin_lang).format(
        username=message.from_user.username or '—',
        amount=amount_fmt,
        channel=channel.title,
        id=payment.id,
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
                reply_markup=payment_action_kb(payment.id, lang=admin_lang),
            )
        except Exception as e:
            logger.error(f"Failed to notify {notify_id}: {e}")

    await state.clear()


@router.message(PaymentStates.waiting_screenshot, Command("cancel"))
async def cancel_screenshot(message: Message, state: FSMContext):
    bot_info = await message.bot.get_me()
    lang = await _get_end_user_lang(bot_info.username, message.from_user.id)
    await state.clear()
    await message.answer(get_text("payment_cancelled", lang))


@router.message(PaymentStates.waiting_screenshot)
async def wrong_screenshot(message: Message):
    bot_info = await message.bot.get_me()
    lang = await _get_end_user_lang(bot_info.username, message.from_user.id)
    await message.answer(get_text("send_photo_only", lang))
