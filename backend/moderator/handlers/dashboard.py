from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import config
from db.engine import async_session
from moderator.keyboards.inline import mod_menu_kb, mod_back_kb
from services.stats_service import get_moderator_stats

router = Router()


def is_moderator(user_id: int) -> bool:
    return user_id in config.moderator_ids


@router.message(Command("mod"))
async def mod_panel(message: Message):
    if not is_moderator(message.from_user.id):
        return

    await message.answer(
        "🛡 <b>Moderator Panel</b>\n\nQuyidagi menyudan tanlang:",
        reply_markup=mod_menu_kb(),
    )


@router.callback_query(F.data == "mod_menu")
async def mod_menu(callback: CallbackQuery):
    if not is_moderator(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q.")
        return

    await callback.message.edit_text(
        "🛡 <b>Moderator Panel</b>\n\nQuyidagi menyudan tanlang:",
        reply_markup=mod_menu_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "mod_stats")
async def mod_stats(callback: CallbackQuery):
    if not is_moderator(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q.")
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
