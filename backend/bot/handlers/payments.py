import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.helpers import require_bot
from bot.keyboards.inline import back_kb, main_menu_kb
from db.engine import async_session
from services.payment_service import get_pending_payments, approve_payment, reject_payment, get_payment_by_id
from services.subscription_service import create_subscription
from utils.constants import PaymentStatus
from core.cache import cache_delete
from core.invite_link import create_invite_link

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "payments")
async def show_payments(callback: CallbackQuery, state: FSMContext):
    user_bot, admin = await require_bot(callback, state, "payments")
    if not user_bot:
        return

    async with async_session() as session:
        pending = await get_pending_payments(session, user_bot.id)

    if not pending:
        await callback.message.edit_text(
            f"💳 <b>To'lovlar</b> — @{user_bot.bot_username}\n\n"
            "Kutilayotgan to'lovlar yo'q.",
            reply_markup=back_kb(),
        )
        await callback.answer()
        return

    text = (
        f"💳 <b>Kutilayotgan to'lovlar</b> — @{user_bot.bot_username}"
        f" ({len(pending)} ta)\n\n"
    )

    buttons = []
    for p in pending[:10]:
        amount_fmt = f"{float(p.amount):,.0f}".replace(",", " ")
        username = p.end_user.username or p.end_user.telegram_id
        text += f"#{p.id} — {amount_fmt} UZS — @{username}\n"
        buttons.append([
            InlineKeyboardButton(
                text=f"✅ #{p.id} tasdiqlash",
                callback_data=f"pay_approve_{p.id}",
            ),
            InlineKeyboardButton(
                text=f"❌ #{p.id} rad etish",
                callback_data=f"pay_reject_{p.id}",
            ),
        ])

    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_menu")])

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pay_approve_"))
async def handle_approve(callback: CallbackQuery):
    payment_id = int(callback.data.split("_")[2])

    async with async_session() as session:
        # Get payment details FIRST (without approving)
        payment = await get_payment_by_id(session, payment_id)
        if not payment or payment.status != PaymentStatus.PENDING:
            await callback.answer("❌ To'lov topilmadi yoki allaqachon ko'rib chiqilgan.")
            return

        channel = payment.channel
        end_user = payment.end_user

        from services.bot_service import get_bot_by_id
        from core.encryption import decrypt_token
        user_bot = await get_bot_by_id(session, payment.user_bot_id)
        if not user_bot:
            await callback.answer("❌ Bot topilmadi.")
            return

        # Create invite link BEFORE approving payment
        try:
            token = decrypt_token(user_bot.bot_token)
            temp_bot = Bot(token=token)
            invite_link = await create_invite_link(temp_bot, channel.telegram_chat_id)
            await temp_bot.session.close()
        except Exception as e:
            logger.error(f"Failed to create invite link: {e}")
            await callback.message.edit_text(
                f"⚠️ Invite link yaratishda xatolik! To'lov tasdiqlanmadi.\n"
                f"Xatolik: {e}\n\n"
                f"Bot kanalda admin ekanligini tekshiring.",
                reply_markup=back_kb(),
            )
            await callback.answer("⚠️ Invite link xatolik!")
            return

        # Invite link ready — now approve payment
        payment = await approve_payment(session, payment_id)
        if not payment:
            await callback.answer("❌ To'lov allaqachon ko'rib chiqilgan.")
            return

        # Create subscription
        sub = await create_subscription(
            session,
            end_user_id=end_user.id,
            channel_id=channel.id,
            payment_id=payment.id,
            invite_link=invite_link,
            duration_months=channel.duration_months,
        )

    # Notify end user with invite link
    notify_failed = False
    try:
        duration_text = {0: "umrbod", 1: "1 oy", 6: "6 oy", 12: "12 oy"}.get(
            channel.duration_months, f"{channel.duration_months} oy"
        )
        await callback.bot.send_message(
            end_user.telegram_id,
            f"✅ <b>To'lov tasdiqlandi!</b>\n\n"
            f"📢 {channel.title}\n"
            f"📅 Muddat: {duration_text}\n\n"
            f"🔗 Kanalga kirish uchun quyidagi linkni bosing:\n"
            f"{invite_link}\n\n"
            f"⚠️ Bu link faqat 1 marta ishlaydi!",
        )
    except Exception as e:
        logger.error(f"Failed to notify end user: {e}")
        notify_failed = True

    # Invalidate stats cache
    await cache_delete(f"stats:{payment.user_bot_id}")

    result_text = (
        f"✅ To'lov #{payment_id} tasdiqlandi!\n"
        f"👤 @{end_user.username or end_user.telegram_id} ga invite link yuborildi."
    )
    if notify_failed:
        result_text += (
            f"\n\n⚠️ Foydalanuvchiga xabar yuborib bo'lmadi. "
            f"Invite link:\n{invite_link}"
        )

    await callback.message.edit_text(result_text, reply_markup=back_kb())
    await callback.answer("✅ Tasdiqlandi!")


@router.callback_query(F.data.startswith("pay_reject_"))
async def handle_reject(callback: CallbackQuery):
    payment_id = int(callback.data.split("_")[2])

    async with async_session() as session:
        payment = await reject_payment(session, payment_id)
        if not payment:
            await callback.answer("❌ To'lov topilmadi yoki allaqachon ko'rib chiqilgan.")
            return

        payment = await get_payment_by_id(session, payment_id)
        end_user = payment.end_user
        channel = payment.channel

    # Notify end user
    try:
        await callback.bot.send_message(
            end_user.telegram_id,
            f"❌ <b>To'lov rad etildi</b>\n\n"
            f"📢 {channel.title}\n\n"
            f"To'lov tasdiqlana olmadi. Iltimos, to'g'ri summani o'tkazing va qayta urinib ko'ring.",
        )
    except Exception as e:
        logger.error(f"Failed to notify end user about rejection: {e}")

    await callback.message.edit_text(
        f"❌ To'lov #{payment_id} rad etildi.\n"
        f"👤 @{end_user.username or end_user.telegram_id} ga xabar yuborildi.",
        reply_markup=back_kb(),
    )
    await callback.answer("❌ Rad etildi!")
