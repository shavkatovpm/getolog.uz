from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.helpers import require_bot
from bot.keyboards.inline import back_kb
from db.engine import async_session
from services.stats_service import get_admin_stats

router = Router()


@router.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery, state: FSMContext):
    user_bot, admin = await require_bot(callback, state, "stats")
    if not user_bot:
        return

    async with async_session() as session:
        stats = await get_admin_stats(session, user_bot.id)

    revenue_fmt = f"{stats['total_revenue']:,.0f}".replace(",", " ")
    text = (
        f"📊 <b>Statistika</b> — @{user_bot.bot_username}\n\n"
        f"👥 Jami foydalanuvchilar: {stats['total_users']}\n"
        f"💳 Tasdiqlangan to'lovlar: {stats['total_payments']}\n"
        f"💰 Umumiy tushum: {revenue_fmt} UZS\n"
        f"⏳ Kutilayotgan to'lovlar: {stats['pending_payments']}\n"
    )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()
