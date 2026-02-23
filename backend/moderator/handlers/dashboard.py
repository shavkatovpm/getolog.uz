from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from core.mod_auth import verify_password, change_password
from db.engine import async_session
from moderator.keyboards.inline import mod_menu_kb, mod_back_kb
from services.stats_service import get_moderator_stats
from utils.constants import ModeratorStates

router = Router()


async def is_mod_authenticated(state: FSMContext) -> bool:
    """Check if user is authenticated as moderator in current session."""
    data = await state.get_data()
    return data.get("mod_authenticated", False)


# ── /modlog — password-based moderator login ──


@router.message(Command("modlog"))
async def modlog_start(message: Message, state: FSMContext):
    if await is_mod_authenticated(state):
        await message.answer(
            "🛡 <b>Moderator Panel</b>\n\nQuyidagi menyudan tanlang:",
            reply_markup=mod_menu_kb(),
        )
        return

    await message.answer("🔐 <b>Moderator kirish</b>\n\nParolni kiriting:")
    await state.set_state(ModeratorStates.waiting_password)


@router.message(ModeratorStates.waiting_password)
async def modlog_check_password(message: Message, state: FSMContext):
    # Delete the password message for security
    try:
        await message.delete()
    except Exception:
        pass

    if verify_password(message.text.strip()):
        await state.set_state(None)
        await state.update_data(mod_authenticated=True)
        await message.answer(
            "✅ Muvaffaqiyatli!\n\n"
            "🛡 <b>Moderator Panel</b>\n\nQuyidagi menyudan tanlang:",
            reply_markup=mod_menu_kb(),
        )
    else:
        await message.answer(
            "❌ Parol noto'g'ri. Qayta urinib ko'ring:\n\n"
            "Bekor qilish uchun /cancel bosing."
        )


@router.message(Command("cancel"), ModeratorStates.waiting_password)
async def cancel_login(message: Message, state: FSMContext):
    await state.set_state(None)
    await message.answer("❌ Kirish bekor qilindi.")


# ── Moderator menu (authenticated via callback) ──


@router.callback_query(F.data == "mod_menu")
async def mod_menu(callback: CallbackQuery, state: FSMContext):
    if not await is_mod_authenticated(state):
        await callback.answer("⛔ Avval /modlog orqali kiring.", show_alert=True)
        return

    await callback.message.edit_text(
        "🛡 <b>Moderator Panel</b>\n\nQuyidagi menyudan tanlang:",
        reply_markup=mod_menu_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "mod_stats")
async def mod_stats(callback: CallbackQuery, state: FSMContext):
    if not await is_mod_authenticated(state):
        await callback.answer("⛔ Avval /modlog orqali kiring.", show_alert=True)
        return

    async with async_session() as session:
        stats = await get_moderator_stats(session)

    revenue_fmt = f"{stats['total_revenue']:,.0f}".replace(",", " ")
    text = (
        "📊 <b>Platforma statistikasi</b>\n\n"
        f"👥 Jami adminlar: {stats['total_admins']}\n"
        f"💎 Pullik adminlar: {stats['paid_admins']}\n"
        f"🤖 Aktiv botlar: {stats['total_bots']}\n"
        f"👤 End userlar: {stats['total_end_users']}\n"
        f"💳 Tasdiqlangan to'lovlar: {stats['total_payments']}\n"
        f"💰 Umumiy tushum: {revenue_fmt} UZS\n"
        f"📱 Aktiv obunalar: {stats['active_subscriptions']}\n"
    )
    await callback.message.edit_text(text, reply_markup=mod_back_kb())
    await callback.answer()


# ── Password change ──


@router.callback_query(F.data == "mod_change_password")
async def ask_new_password(callback: CallbackQuery, state: FSMContext):
    if not await is_mod_authenticated(state):
        await callback.answer("⛔ Avval /modlog orqali kiring.", show_alert=True)
        return

    await callback.message.edit_text(
        "🔑 <b>Parolni o'zgartirish</b>\n\n"
        "Yangi parolni kiriting:",
        reply_markup=mod_back_kb(),
    )
    await state.set_state(ModeratorStates.waiting_new_password)
    await callback.answer()


@router.message(ModeratorStates.waiting_new_password)
async def save_new_password(message: Message, state: FSMContext):
    new_pwd = message.text.strip()

    # Delete the password message for security
    try:
        await message.delete()
    except Exception:
        pass

    if len(new_pwd) < 4:
        await message.answer(
            "❌ Parol kamida 4 ta belgi bo'lishi kerak. Qayta kiriting:"
        )
        return

    change_password(new_pwd)
    await state.set_state(None)
    await message.answer(
        "✅ Parol muvaffaqiyatli o'zgartirildi!",
        reply_markup=mod_menu_kb(),
    )


# ── Moderator logout ──


@router.callback_query(F.data == "mod_logout")
async def mod_logout(callback: CallbackQuery, state: FSMContext):
    await state.update_data(mod_authenticated=False)
    await callback.message.edit_text("👋 Moderator paneldan chiqdingiz.")
    await callback.answer()
