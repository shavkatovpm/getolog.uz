from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.inline import back_kb, main_menu_kb
from db.engine import async_session
from services.admin_service import get_admin_by_telegram_id, get_active_subscription

router = Router()


@router.callback_query(F.data == "my_subscription")
async def show_subscription(callback: CallbackQuery):
    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, callback.from_user.id)
        sub = await get_active_subscription(session, admin.id)

    if not sub or sub.plan == "free":
        text = (
            "📦 <b>Joriy tarif: Bepul</b>\n\n"
            "Bepul tarifda bot to'liq ishlaydi, lekin end userlarga "
            "Getolog reklamasi ko'rsatiladi.\n\n"
            "Reklamani olib tashlash uchun pullik tarifga o'ting:"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="1 oylik", callback_data="buy_1month")],
            [InlineKeyboardButton(text="6 oylik", callback_data="buy_6month")],
            [InlineKeyboardButton(text="12 oylik", callback_data="buy_12month")],
            [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_menu")],
        ])
    else:
        expires = sub.expires_at.strftime("%d.%m.%Y") if sub.expires_at else "—"
        plan_names = {"1month": "1 oylik", "6month": "6 oylik", "12month": "12 oylik"}
        text = (
            f"📦 <b>Joriy tarif: {plan_names.get(sub.plan, sub.plan)}</b>\n\n"
            f"📅 Tugash sanasi: {expires}\n"
            f"✅ Holati: Aktiv\n"
        )
        kb = back_kb()

    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()
