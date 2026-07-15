"""Obunachi oqimi (adminning shaxsiy boti): /start -> tarif tanlash -> chek yuborish.

Chek rasmi bazada `receipt_file_id` sifatida saqlanadi (dashboard uni keyinroq
shu bot orqali on-demand ko'rsatadi — `app/api/routes.py`). Admin bu haqda
faqat qisqa matnli bildirishnoma oladi, u ham **bosh bot** orqali — chunki
endi barcha boshqaruv (tasdiqlash/rad etish) dashboardda amalga oshadi.
"""

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot import registry
from app.bot.keyboards import plan_choice_keyboard
from app.bot.states import SubscriberPaymentStates
from app.config import settings
from app.db.models import Admin, Bot as BotModel, Channel, Payment, SubscriptionPlan
from app.services.subscription_service import can_accept_new_subscriber

router = Router(name="subscriber_flow")


async def _get_bot_row(session: AsyncSession, telegram_bot_id: int) -> BotModel | None:
    result = await session.execute(
        select(BotModel).where(BotModel.telegram_bot_id == telegram_bot_id)
    )
    return result.scalar_one_or_none()


async def _resolve_channel(
    session: AsyncSession, bot_id: int, payload: str | None
) -> Channel | None:
    """Obunachi qaysi kanalga kirmoqchi ekanini aniqlaydi.

    Agar admin invite havolasini `?start=<channel_id>` ko'rinishida bergan bo'lsa
    aynan o'sha kanal olinadi; aks holda, botda faqat bitta kanal bo'lsa o'shani
    ishlatamiz (ko'p kanalli holatda aniq havola talab qilinadi).
    """
    if payload and payload.isdigit():
        result = await session.execute(
            select(Channel).where(Channel.id == int(payload), Channel.bot_id == bot_id)
        )
        channel = result.scalar_one_or_none()
        if channel is not None:
            return channel

    result = await session.execute(select(Channel).where(Channel.bot_id == bot_id))
    channels = result.scalars().all()
    return channels[0] if len(channels) == 1 else None


@router.message(CommandStart())
async def subscriber_start(message: Message, session: AsyncSession) -> None:
    bot_row = await _get_bot_row(session, message.bot.id)
    if bot_row is None:
        return

    parts = (message.text or "").split(maxsplit=1)
    payload = parts[1] if len(parts) > 1 else None
    channel = await _resolve_channel(session, bot_row.id, payload)

    if channel is None:
        await message.answer(
            "Qaysi kanalga obuna bo'lmoqchi ekaningizni aniqlay olmadim. "
            "Iltimos, admin bergan havola orqali qayta urinib ko'ring."
        )
        return

    result = await session.execute(
        select(SubscriptionPlan).where(
            SubscriptionPlan.channel_id == channel.id, SubscriptionPlan.active.is_(True)
        )
    )
    plans = result.scalars().all()
    if not plans:
        await message.answer("Bu kanal uchun hozircha tarif narxlari sozlanmagan.")
        return

    await message.answer(
        f"«{channel.title}» kanaliga obuna bo'lish uchun tarifni tanlang:",
        reply_markup=plan_choice_keyboard(plans),
    )


@router.callback_query(F.data.startswith("choose_plan:"))
async def choose_plan(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    plan_id = int(callback.data.split(":", 1)[1])
    result = await session.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id))
    plan = result.scalar_one()

    channel_result = await session.execute(select(Channel).where(Channel.id == plan.channel_id))
    channel = channel_result.scalar_one()

    admin_result = await session.execute(select(Admin).where(Admin.id == plan.admin_id))
    admin = admin_result.scalar_one()

    if not await can_accept_new_subscriber(session, admin):
        await callback.message.edit_text(
            "Kechirasiz, hozircha yangi obunachi qabul qilinmayapti. "
            "Admin bilan bog'lanib ko'ring."
        )
        await callback.answer()
        return

    await state.update_data(plan_id=plan.id)
    await state.set_state(SubscriberPaymentStates.waiting_for_receipt)
    await callback.message.edit_text(
        f"Tanlandi: {plan.duration_months} oy — {plan.price:g} {plan.currency}\n\n"
        f"To'lov rekvizitlari:\n{channel.payment_instructions}\n\n"
        "To'lovni amalga oshirgach, chek yoki skrinshotni shu yerga rasm sifatida yuboring."
    )
    await callback.answer()


@router.message(SubscriberPaymentStates.waiting_for_receipt, F.photo)
async def receive_receipt(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    result = await session.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == data["plan_id"])
    )
    plan = result.scalar_one()

    payment = Payment(
        channel_id=plan.channel_id,
        admin_id=plan.admin_id,
        plan_id=plan.id,
        user_id=message.from_user.id,
        amount=plan.price,
        method="manual",
        receipt_file_id=message.photo[-1].file_id,
    )
    session.add(payment)
    await session.commit()
    await state.clear()

    admin_result = await session.execute(select(Admin).where(Admin.id == plan.admin_id))
    admin = admin_result.scalar_one()

    main_bot = registry.get_main_bot()
    await main_bot.send_message(
        admin.telegram_id,
        "Yangi to'lov keldi 💳\n"
        f"Tarif: {plan.duration_months} oy — {plan.price:g} {plan.currency}\n\n"
        f"Ko'rib chiqish uchun dashboardga o'ting: {settings.dashboard_origin}",
    )

    await message.answer(
        "Chekingiz adminga yuborildi. Tasdiqlangach, kanalga kirish havolasini olasiz."
    )


@router.message(SubscriberPaymentStates.waiting_for_receipt)
async def receive_receipt_wrong_type(message: Message) -> None:
    await message.answer("Iltimos, to'lov chekini rasm (screenshot) ko'rinishida yuboring.")
