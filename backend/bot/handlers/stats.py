from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.inline import back_kb, main_menu_kb
from db.engine import async_session
from services.admin_service import get_admin_by_telegram_id
from services.bot_service import get_bot_by_admin
from services.stats_service import get_admin_stats

router = Router()


@router.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery):
    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, callback.from_user.id)
        user_bot = await get_bot_by_admin(session, admin.id)

        if not user_bot:
            await callback.message.edit_text(
                "⚠️ Sizda hali bot yo'q.",
                reply_markup=main_menu_kb(),
            )
            await callback.answer()
            return

        stats = await get_admin_stats(session, user_bot.id)

    revenue_fmt = f"{stats['total_revenue']:,.0f}".replace(",", " ")
    text = (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: {stats['total_users']}\n"
        f"💳 Tasdiqlangan to'lovlar: {stats['total_payments']}\n"
        f"💰 Umumiy tushum: {revenue_fmt} UZS\n"
        f"⏳ Kutilayotgan to'lovlar: {stats['pending_payments']}\n"
    )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()
