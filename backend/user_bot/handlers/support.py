from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.middlewares.i18n import get_text
from db.engine import async_session
from db.models import EndUser, UserBot
from utils.constants import SupportStates
from sqlalchemy import select

router = Router()


async def _get_eu_lang(bot_username: str, telegram_id: int) -> str:
    async with async_session() as session:
        result = await session.execute(
            select(EndUser).join(UserBot).where(
                EndUser.telegram_id == telegram_id,
                UserBot.bot_username == bot_username,
            )
        )
        eu = result.scalar_one_or_none()
        return (eu.language if eu else "uz") or "uz"


@router.callback_query(F.data == "support")
async def start_support(callback: CallbackQuery, state: FSMContext):
    bot_info = await callback.bot.get_me()
    lang = await _get_eu_lang(bot_info.username, callback.from_user.id)
    await callback.message.edit_text(get_text("support_header", lang))
    await state.set_state(SupportStates.waiting_message)
    await callback.answer()


@router.message(SupportStates.waiting_message)
async def forward_to_admin(message: Message, state: FSMContext):
    bot_info = await message.bot.get_me()
    lang = await _get_eu_lang(bot_info.username, message.from_user.id)

    async with async_session() as session:
        result = await session.execute(
            select(UserBot).where(UserBot.bot_username == bot_info.username)
        )
        user_bot = result.scalar_one_or_none()

    if not user_bot:
        await message.answer(get_text("support_error", lang))
        await state.clear()
        return

    # Forward message to admin — use admin's language
    admin_lang = user_bot.admin.language or "uz"
    try:
        await message.bot.send_message(
            user_bot.admin.telegram_id,
            get_text("support_forwarded", admin_lang).format(
                username=message.from_user.username or '—',
                user_id=message.from_user.id,
                bot=user_bot.bot_username,
                text=message.text or '[media]',
            ),
        )
    except Exception:
        pass

    await message.answer(get_text("support_sent", lang))
    await state.clear()
