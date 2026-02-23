from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db.engine import async_session
from db.models import EndUser, UserBot
from user_bot.keyboards.inline import language_kb, channel_select_kb
from services.bot_service import get_channels_by_bot
from sqlalchemy import select

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    # Clear any active FSM state (e.g. payment flow)
    await state.clear()

    # Find which user_bot this is
    bot_info = await message.bot.get_me()
    async with async_session() as session:
        result = await session.execute(
            select(UserBot).where(UserBot.bot_username == bot_info.username)
        )
        user_bot = result.scalar_one_or_none()
        if not user_bot:
            await message.answer("❌ Bot sozlanmagan.")
            return

        # Get or create end user
        result = await session.execute(
            select(EndUser).where(
                EndUser.telegram_id == message.from_user.id,
                EndUser.user_bot_id == user_bot.id,
            )
        )
        end_user = result.scalar_one_or_none()

        if not end_user:
            # New user — show language selection
            end_user = EndUser(
                telegram_id=message.from_user.id,
                user_bot_id=user_bot.id,
                username=message.from_user.username,
            )
            session.add(end_user)
            await session.commit()

            # Notify admin + collaborators about new user
            notify_text = (
                f"🆕 Yangi foydalanuvchi: @{message.from_user.username or '—'}\n"
                f"Bot: @{user_bot.bot_username}"
            )
            notify_ids = [user_bot.admin.telegram_id]
            for collab in user_bot.collaborators:
                notify_ids.append(collab.telegram_id)
            for notify_id in notify_ids:
                try:
                    await message.bot.send_message(notify_id, notify_text)
                except Exception:
                    pass

            await message.answer(
                "🌐 Tilni tanlang / Выберите язык / Choose language:",
                reply_markup=language_kb(),
            )
            return

        if end_user.banned:
            await message.answer("⛔ Siz bloklangansiz.")
            return

        # Existing user — show welcome + channels
        welcome = user_bot.welcome_message or "Assalomu alaykum! Pullik kanalga kirish uchun quyidagi tugmani bosing."
        channels = await get_channels_by_bot(session, user_bot.id)

    await message.answer(welcome)
    if channels:
        await message.answer(
            "📢 Mavjud kanallar:",
            reply_markup=channel_select_kb(channels),
        )


@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
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
        if end_user:
            end_user.language = lang
            await session.commit()

        welcome = user_bot.welcome_message or "Assalomu alaykum! Pullik kanalga kirish uchun quyidagi tugmani bosing."
        channels = await get_channels_by_bot(session, user_bot.id)

    await callback.message.edit_text(f"✅ Til tanlandi!")
    await callback.message.answer(welcome)
    if channels:
        await callback.message.answer(
            "📢 Mavjud kanallar:",
            reply_markup=channel_select_kb(channels),
        )
    await callback.answer()
