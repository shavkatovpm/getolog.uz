from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db.engine import async_session
from db.models import EndUser, UserBot
from utils.constants import SupportStates
from sqlalchemy import select

router = Router()


@router.callback_query(F.data == "support")
async def start_support(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📩 <b>Support</b>\n\n"
        "Xabaringizni yozing, admin tez orada javob beradi."
    )
    await state.set_state(SupportStates.waiting_message)
    await callback.answer()


@router.message(SupportStates.waiting_message)
async def forward_to_admin(message: Message, state: FSMContext):
    bot_info = await message.bot.get_me()

    async with async_session() as session:
        result = await session.execute(
            select(UserBot).where(UserBot.bot_username == bot_info.username)
        )
        user_bot = result.scalar_one_or_none()

    if not user_bot:
        await message.answer("❌ Xatolik.")
        await state.clear()
        return

    # Forward message to admin
    try:
        await message.bot.send_message(
            user_bot.admin.telegram_id,
            f"📩 <b>Support xabar</b>\n"
            f"👤 @{message.from_user.username or '—'} (ID: {message.from_user.id})\n"
            f"🤖 @{user_bot.bot_username}\n\n"
            f"{message.text or '[media]'}",
        )
    except Exception:
        pass

    await message.answer("✅ Xabaringiz adminga yuborildi!")
    await state.clear()
