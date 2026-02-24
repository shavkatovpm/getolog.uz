from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.helpers import require_bot
from bot.keyboards.inline import back_bot_kb
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

    def fmt(n: float) -> str:
        return f"{n:,.0f}".replace(",", " ")

    total_users = stats["total_users"]
    total_payments = stats["total_payments"]
    conversion = round(total_payments / total_users * 100) if total_users > 0 else 0
    avg_check = stats["total_revenue"] / total_payments if total_payments > 0 else 0

    text = f"📊 <b>Statistika</b> — @{user_bot.bot_username}\n"

    # Daromad bloki
    text += (
        f"\n💰 <b>Daromad</b>\n"
        f"├ Bugun: {fmt(stats['today_revenue'])} UZS\n"
        f"├ Bu oy: {fmt(stats['month_revenue'])} UZS\n"
        f"└ Jami: {fmt(stats['total_revenue'])} UZS\n"
    )

    # Foydalanuvchilar bloki
    text += (
        f"\n👥 <b>Foydalanuvchilar</b>\n"
        f"├ Jami: {total_users}\n"
        f"├ Aktiv obunalar: {stats['active_subs']}\n"
        f"└ Konversiya: {conversion}%\n"
    )

    # To'lovlar bloki
    text += (
        f"\n💳 <b>To'lovlar</b>\n"
        f"├ Tasdiqlangan: {total_payments}\n"
        f"├ Kutilayotgan: {stats['pending_payments']}\n"
        f"├ Rad etilgan: {stats['rejected_payments']}\n"
        f"└ O'rtacha chek: {fmt(avg_check)} UZS\n"
    )

    # Ogohlantirishlar
    if stats["expiring_soon"] > 0:
        text += (
            f"\n⚠️ <b>{stats['expiring_soon']}</b> ta obuna 3 kun ichida tugaydi\n"
        )

    if stats["pending_payments"] > 0:
        text += (
            f"\n⏳ <b>{stats['pending_payments']}</b> ta to'lov tasdiqlash kutmoqda\n"
        )

    await callback.message.edit_text(text, reply_markup=back_bot_kb())
    await callback.answer()
