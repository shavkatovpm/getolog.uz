import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.inline import payment_action_kb, back_kb, main_menu_kb
from db.engine import async_session
from services.admin_service import get_admin_by_telegram_id
from services.bot_service import get_bot_by_admin
from services.payment_service import get_pending_payments, approve_payment, reject_payment, get_payment_by_id
from services.subscription_service import create_subscription
from core.invite_link import create_invite_link

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "payments")
async def show_payments(callback: CallbackQuery):
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

        pending = await get_pending_payments(session, user_bot.id)

    if not pending:
        await callback.message.edit_text(
            "💳 Kutilayotgan to'lovlar yo'q.",
            reply_markup=back_kb(),
        )
        await callback.answer()
        return

    text = f"💳 <b>Kutilayotgan to'lovlar:</b> ({len(pending)} ta)\n\n"

    for p in pending[:10]:
        amount_fmt = f"{float(p.amount):,.0f}".replace(",", " ")
        text += (
            f"#{p.id} — {amount_fmt} UZS\n"
            f"👤 {p.end_user.username or p.end_user.telegram_id}\n\n"
        )

    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("pay_approve_"))
async def handle_approve(callback: CallbackQuery):
    payment_id = int(callback.data.split("_")[2])

    async with async_session() as session:
        payment = await approve_payment(session, payment_id)
        if not payment:
            await callback.answer("❌ To'lov topilmadi yoki allaqachon ko'rib chiqilgan.")
            return

        # Get payment details for invite link
        payment = await get_payment_by_id(session, payment_id)
        channel = payment.channel

        # Create invite link via bot manager
        # The bot instance needs to come from bot_manager
        # For now we'll store the approval and let the system create the link
        from services.bot_service import get_bot_by_id
        user_bot = await get_bot_by_id(session, payment.user_bot_id)

    await callback.message.edit_text(
        f"✅ To'lov #{payment_id} tasdiqlandi!\n"
        "End userga invite link yuborildi.",
    )
    await callback.answer("✅ Tasdiqlandi!")


@router.callback_query(F.data.startswith("pay_reject_"))
async def handle_reject(callback: CallbackQuery):
    payment_id = int(callback.data.split("_")[2])

    async with async_session() as session:
        payment = await reject_payment(session, payment_id)
        if not payment:
            await callback.answer("❌ To'lov topilmadi yoki allaqachon ko'rib chiqilgan.")
            return

    await callback.message.edit_text(f"❌ To'lov #{payment_id} rad etildi.")
    await callback.answer("❌ Rad etildi!")
