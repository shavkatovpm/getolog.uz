"""Admin bosh botda to'lovni tezkor tasdiqlash/rad etishi — dashboard'ga
kirmasdan ham qila oladigan qisqa yo'l. Haqiqiy ish `app/services/payment_service.py`
ichida — dashboard API ham xuddi shu funksiyalarni chaqiradi, natija ikkalasida
ham bir xil bo'ladi.
"""

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot import keyboards, registry
from app.bot.states import PaymentReviewStates
from app.db.models import Payment, PaymentStatus
from app.services import payment_service

router = Router(name="payment_review")


async def _get_payment(session: AsyncSession, payment_id: int) -> Payment | None:
    result = await session.execute(select(Payment).where(Payment.id == payment_id))
    return result.scalar_one_or_none()


@router.callback_query(F.data.startswith("pay_approve:"))
async def on_approve_pressed(callback: CallbackQuery, session: AsyncSession) -> None:
    payment_id = int(callback.data.split(":", 1)[1])
    payment = await _get_payment(session, payment_id)
    if payment is None:
        await callback.answer("To'lov topilmadi", show_alert=True)
        return

    try:
        await payment_service.approve_payment(session, payment)
    except payment_service.PaymentReviewError as exc:
        await callback.answer(str(exc), show_alert=True)
        return

    assert isinstance(callback.message, Message)
    await callback.message.edit_caption(
        caption=f"{callback.message.caption}\n\n✅ Tasdiqlandi", reply_markup=None
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pay_reject:"))
async def on_reject_pressed(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    payment_id = int(callback.data.split(":", 1)[1])
    payment = await _get_payment(session, payment_id)
    if payment is None or payment.status != PaymentStatus.pending:
        await callback.answer("Bu to'lov allaqachon ko'rib chiqilgan", show_alert=True)
        return

    assert isinstance(callback.message, Message)
    await state.set_state(PaymentReviewStates.waiting_for_reject_comment)
    await state.update_data(
        payment_id=payment_id,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        original_caption=callback.message.caption or "",
    )
    await callback.message.edit_caption(
        caption=f"{callback.message.caption}\n\nIzoh yozing (ixtiyoriy) yoki pastdagi tugmani bosing:",
        reply_markup=keyboards.payment_reject_confirm_keyboard(payment_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pay_reject_skip:"))
async def on_reject_skip_pressed(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    payment_id = int(callback.data.split(":", 1)[1])
    payment = await _get_payment(session, payment_id)
    if payment is None:
        await callback.answer("To'lov topilmadi", show_alert=True)
        return

    try:
        await payment_service.reject_payment(session, payment)
    except payment_service.PaymentReviewError as exc:
        await callback.answer(str(exc), show_alert=True)
        return

    data = await state.get_data()
    await state.clear()

    assert isinstance(callback.message, Message)
    original_caption = data.get("original_caption") or callback.message.caption or ""
    await callback.message.edit_caption(
        caption=f"{original_caption}\n\n❌ Bekor qilindi", reply_markup=None
    )
    await callback.answer()


@router.message(PaymentReviewStates.waiting_for_reject_comment, ~F.text.startswith("/"))
async def on_reject_comment_received(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    data = await state.get_data()
    await state.clear()

    payment_id = data.get("payment_id")
    if payment_id is None:
        return
    payment = await _get_payment(session, payment_id)
    if payment is None:
        return

    comment = (message.text or "").strip()
    try:
        await payment_service.reject_payment(session, payment, comment=comment or None)
    except payment_service.PaymentReviewError as exc:
        await message.answer(str(exc))
        return

    main_bot = registry.get_main_bot()
    original_caption = data.get("original_caption", "")
    try:
        await main_bot.edit_message_caption(
            chat_id=data["chat_id"],
            message_id=data["message_id"],
            caption=f"{original_caption}\n\n❌ Bekor qilindi. Izoh: {comment}",
        )
    except TelegramAPIError:
        pass

    await message.answer("Bekor qilindi, obunachiga izohingiz yuborildi.")
