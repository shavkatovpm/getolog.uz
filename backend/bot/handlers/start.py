from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.keyboards.inline import main_menu_kb
from db.engine import async_session
from services.admin_service import get_or_create_admin
from config import config

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    async with async_session() as session:
        admin, is_new = await get_or_create_admin(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            language="uz",
        )

    if admin.banned:
        await message.answer("⛔ Sizning akkauntingiz bloklangan.")
        return

    if is_new:
        # Notify moderators
        for mod_id in config.moderator_ids:
            try:
                await message.bot.send_message(
                    mod_id,
                    f"🆕 Yangi admin ro'yxatdan o'tdi:\n"
                    f"👤 {message.from_user.full_name}\n"
                    f"🔗 @{message.from_user.username or '—'}",
                )
            except Exception:
                pass

    text = (
        f"👋 Salom, {message.from_user.first_name}!\n\n"
        "🤖 <b>Getolog</b> — Telegram kanalingizni pullik qilish platformasi.\n\n"
        "Bot tokeningizni yuboring, biz avtomatlashtirilgan sotuvchi bot yaratamiz.\n\n"
        "Quyidagi menyudan tanlang:"
    )
    await message.answer(text, reply_markup=main_menu_kb())


@router.callback_query(F.data == "back_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        f"👋 {callback.from_user.first_name}, menyuga qaytdingiz.\n\n"
        "Quyidagi menyudan tanlang:"
    )
    await callback.message.edit_text(text, reply_markup=main_menu_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("pick_"))
async def pick_bot_for_action(callback: CallbackQuery, state: FSMContext):
    """Handle bot selection when admin has multiple bots."""
    parts = callback.data.split("_")
    # Format: pick_{action}_{bot_id}
    action = parts[1]
    bot_id = int(parts[2])
    await state.update_data(selected_bot_id=bot_id)

    if action == "settings":
        from bot.handlers.settings import show_settings
        await show_settings(callback, state)
    elif action == "stats":
        from bot.handlers.stats import show_stats
        await show_stats(callback, state)
    elif action == "users":
        from bot.handlers.manage_users import show_users
        await show_users(callback, state)
    elif action == "payments":
        from bot.handlers.payments import show_payments
        await show_payments(callback, state)
