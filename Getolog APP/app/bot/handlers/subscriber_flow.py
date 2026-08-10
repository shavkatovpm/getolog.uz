"""Obunachi oqimi (adminning shaxsiy boti): /start -> tarif tanlash -> chek yuborish.

Chek rasmi bazada `receipt_file_id` sifatida saqlanadi (dashboard uni keyinroq
shu bot orqali on-demand ko'rsatadi — `app/api/routes.py`). Admin bu haqda
rasm shaklida (chek + obunachi ma'lumotlari + tezkor tasdiqlash/rad etish
tugmalari bilan) bildirishnoma oladi, u ham **bosh bot** orqali
(`app/bot/handlers/payment_review.py`).
"""

from html import escape

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, ChatMemberUpdated, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot import registry
from app.bot.keyboards import payment_review_keyboard, plan_choice_keyboard
from app.bot.states import SubscriberPaymentStates
from app.db.models import (
    Admin,
    Bot as BotModel,
    Channel,
    ChatType,
    Payment,
    PaymentCard,
    PaymentStatus,
    SubscriptionPlan,
)
from app.services.formatting import format_amount
from app.services.subscription_service import plan_duration_label

router = Router(name="subscriber_flow")

# Barcha adminlarning obunachilariga (tarifidan qat'i nazar) Getolog brendi ko'rsatiladi.
BRANDING_FOOTER = "🤖 Getolog (getolog.uz) orqali ishlaydi"


def _kind_word(channel: Channel, *, izafet_dative: bool = False) -> str:
    """Kanal/guruh so'zini to'g'ri grammatik shaklda qaytaradi (matnlarda ishlatish uchun)."""
    is_group = channel.chat_type == ChatType.group
    if izafet_dative:
        return "guruhiga" if is_group else "kanaliga"
    return "guruh" if is_group else "kanal"


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

    admin_result = await session.execute(select(Admin).where(Admin.id == bot_row.admin_id))
    admin = admin_result.scalar_one_or_none()
    if admin is None:
        return

    parts = (message.text or "").split(maxsplit=1)
    payload = parts[1] if len(parts) > 1 else None
    channel = await _resolve_channel(session, bot_row.id, payload)

    if channel is None:
        await message.answer(
            "Qaysi kanal yoki guruhga obuna bo'lmoqchi ekaningizni aniqlay olmadim. "
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
        await message.answer(f"Bu {_kind_word(channel)} uchun hozircha tarif narxlari sozlanmagan.")
        return

    intro = f"{channel.welcome_message}\n\n" if channel.welcome_message else ""
    await message.answer(
        f"{intro}«{channel.title}» {_kind_word(channel, izafet_dative=True)} obuna bo'lish uchun tarifni tanlang:"
        f"\n\n{BRANDING_FOOTER}",
        reply_markup=plan_choice_keyboard(plans),
    )


@router.callback_query(F.data.startswith("choose_plan:"))
async def choose_plan(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    plan_id = int(callback.data.split(":", 1)[1])
    result = await session.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id))
    plan = result.scalar_one()

    channel_result = await session.execute(select(Channel).where(Channel.id == plan.channel_id))
    channel = channel_result.scalar_one()

    cards_result = await session.execute(
        select(PaymentCard).where(PaymentCard.channel_id == channel.id).order_by(PaymentCard.id)
    )
    cards = cards_result.scalars().all()
    if cards:
        # Karta raqami <code> ichida — Telegram'da bosib nusxalash qulay bo'lishi uchun.
        cards_text = "\n\n".join(
            f"💳 {escape(card.bank_name)}\n<code>{escape(card.card_number)}</code>\n"
            f"{escape(card.owner_name)}"
            for card in cards
        )
    else:
        cards_text = "Karta ma'lumotlari hali kiritilmagan — admin bilan bog'laning."

    await state.update_data(plan_id=plan.id)
    await state.set_state(SubscriberPaymentStates.waiting_for_receipt)
    await callback.message.edit_text(
        f"Tanlandi: {plan_duration_label(plan)} — {format_amount(plan.price)} {plan.currency}\n\n"
        f"Ushbu kartaga to'lov qilib, chekni menga (rasm sifatida) yuboring:\n\n{cards_text}",
        parse_mode="HTML",
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
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        amount=plan.price,
        method="manual",
        receipt_file_id=message.photo[-1].file_id,
    )
    session.add(payment)
    await session.commit()
    await state.clear()

    admin_result = await session.execute(select(Admin).where(Admin.id == plan.admin_id))
    admin = admin_result.scalar_one()

    channel_result = await session.execute(select(Channel).where(Channel.id == plan.channel_id))
    channel = channel_result.scalar_one()

    subscriber_user = message.from_user
    username_part = f"@{subscriber_user.username}" if subscriber_user.username else "username yo'q"

    # `file_id` botlar orasida ishlamaydi — chek shu (bolalar) bot orqali
    # yuklab olinib, bosh botga qayta yuklanadi (BufferedInputFile sifatida).
    receipt_file = await message.bot.get_file(message.photo[-1].file_id)
    receipt_bytes = await message.bot.download_file(receipt_file.file_path)

    main_bot = registry.get_main_bot()
    await main_bot.send_photo(
        admin.telegram_id,
        photo=BufferedInputFile(receipt_bytes.read(), filename="chek.jpg"),
        caption=(
            "Yangi to'lov keldi 💳\n\n"
            f"Obunachi: {subscriber_user.full_name} ({username_part})\n"
            f"{_kind_word(channel).capitalize()}: {channel.title}\n"
            f"Tarif: {plan_duration_label(plan)} — {format_amount(plan.price)} {plan.currency}"
        ),
        reply_markup=payment_review_keyboard(payment.id),
    )

    await message.answer(
        f"Chekingiz adminga yuborildi. Tasdiqlangach, {_kind_word(channel)}ga kirish havolasini olasiz."
    )


@router.message(SubscriberPaymentStates.waiting_for_receipt)
async def receive_receipt_wrong_type(message: Message) -> None:
    await message.answer("Iltimos, to'lov chekini rasm (screenshot) ko'rinishida yuboring.")


@router.chat_member()
async def on_member_joined(event: ChatMemberUpdated, session: AsyncSession) -> None:
    """Obunachi invite havola orqali HAQIQATAN HAM kanal/guruhga qo'shilganda keladi
    (Telegram'ning o'zi tasdiqlagan `chat_member` hodisasi) — taxmin bilan emas,
    shundagina "Kirish" xabari "Siz qo'shildingiz ✅"ga tahrirlanadi.
    """
    if event.chat.type not in ("channel", "group", "supergroup"):
        return
    if event.new_chat_member.status != "member":
        return
    if event.old_chat_member.status not in ("left", "kicked"):
        return  # masalan admin bo'lib qolishi kabi boshqa o'zgarish, yangi qo'shilish emas

    bot_row = await _get_bot_row(session, event.bot.id)
    if bot_row is None:
        return
    channel_result = await session.execute(select(Channel).where(Channel.bot_id == bot_row.id))
    channel = channel_result.scalar_one_or_none()
    if channel is None or channel.telegram_channel_id != event.chat.id:
        return

    user_id = event.new_chat_member.user.id
    payment_result = await session.execute(
        select(Payment)
        .where(
            Payment.channel_id == channel.id,
            Payment.user_id == user_id,
            Payment.status == PaymentStatus.approved,
            Payment.invite_message_id.is_not(None),
        )
        .order_by(Payment.approved_at.desc())
        .limit(1)
    )
    payment = payment_result.scalar_one_or_none()
    if payment is None:
        return

    try:
        await event.bot.edit_message_text(
            chat_id=user_id,
            message_id=payment.invite_message_id,
            text=f"✅ Siz «{channel.title}» {_kind_word(channel, izafet_dative=True)} qo'shildingiz!",
        )
    except TelegramAPIError:
        pass
