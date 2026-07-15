"""Bosh bot oqimi: /start -> ism -> bot tokeni -> webhook -> kanalga ulash + huquq tekshirish.

Bu faylda ikkita alohida router bor, chunki ikki xil bot ularni ishlatadi:
- `main_router` — GETOLOG bosh boti bilan suhbatda (admin ro'yxatdan o'tadi).
- `child_router` — adminning shaxsiy boti bilan bog'liq (kanalga admin qilib
  qo'shilganini aniqlash uchun `my_chat_member` hodisasini tinglaydi).
"""

import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Chat,
    ChatMemberAdministrator,
    ChatMemberUpdated,
    Message,
    MessageOriginChannel,
)
from aiogram.utils.token import TokenValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot import registry
from app.bot.states import OnboardingStates
from app.config import settings
from app.db.models import Admin, Bot as BotModel, Channel
from app.services import channel_service
from app.services.encryption import encrypt_token
from app.services.login_codes import generate_login_code

logger = logging.getLogger(__name__)

main_router = Router(name="onboarding_main")
child_router = Router(name="onboarding_child")


async def _get_admin(session: AsyncSession, telegram_id: int) -> Admin | None:
    result = await session.execute(select(Admin).where(Admin.telegram_id == telegram_id))
    return result.scalar_one_or_none()


@main_router.message(CommandStart())
async def cmd_start(
    message: Message, command: CommandObject, state: FSMContext, session: AsyncSession
) -> None:
    if command.args == "login":
        code = generate_login_code(message.from_user.id)
        await message.answer(
            f"Dashboard'ga kirish kodingiz:\n\n<code>{code}</code>\n\n"
            f"Bu kodni {settings.dashboard_origin} saytidagi kirish oynasiga kiriting. "
            "Kod 5 daqiqa amal qiladi va faqat bir marta ishlatiladi.",
            parse_mode="HTML",
        )
        return

    admin = await _get_admin(session, message.from_user.id)

    if admin is None:
        await message.answer(
            "Assalomu alaykum! GETOLOG — yopiq Telegram kanalingiz uchun "
            "obuna boshqaruvi platformasi.\n\n"
            "Boshlash uchun to'liq ismingizni yuboring:"
        )
        await state.set_state(OnboardingStates.waiting_for_name)
        return

    bot_row = await _get_admin_bot(session, admin.id)
    if bot_row is None:
        await message.answer(
            "Xush kelibsiz, siz allaqachon ro'yxatdan o'tgansiz.\n\n"
            "BotFather (@BotFather) orqali yangi bot yarating va uning "
            "tokenini shu yerga yuboring:"
        )
        await state.set_state(OnboardingStates.waiting_for_bot_token)
        return

    channel_row = await _get_bot_channel(session, bot_row.id)
    if channel_row is None:
        await message.answer(
            f"@{bot_row.username} boti ulangan, lekin hali hech qanday kanalga "
            "admin qilib qo'shilmagan.\n\n"
            "Botni kanalingizga admin sifatida qo'shing (a'zo qo'shish/chiqarish, "
            "post yuborish/o'chirish huquqlari bilan) — GETOLOG buni avtomatik aniqlaydi.\n\n"
            "Agar bir necha daqiqadan so'ng ham xabar kelmasa, kanaldagi istalgan "
            "postni shu yerga forward qiling — tekshirib darhol javob beraman."
        )
        return

    await message.answer(
        f"Hammasi tayyor ✅\nBot: @{bot_row.username}\nKanal: {channel_row.title}\n\n"
        "Endi /narx komandasi orqali obunachilar uchun tarif narxlarini belgilashingiz mumkin."
    )


@main_router.message(OnboardingStates.waiting_for_name, ~F.text.startswith("/"))
async def process_name(message: Message, state: FSMContext, session: AsyncSession) -> None:
    full_name = (message.text or "").strip()
    if not full_name:
        await message.answer("Iltimos, ismingizni matn ko'rinishida yuboring.")
        return

    admin = Admin(telegram_id=message.from_user.id, full_name=full_name, language="uz")
    session.add(admin)
    await session.commit()

    await message.answer(
        f"Rahmat, {full_name}!\n\n"
        "Endi @BotFather orqali yangi bot yarating (/newbot) va u bergan "
        "tokenni shu yerga yuboring:"
    )
    await state.set_state(OnboardingStates.waiting_for_bot_token)


@main_router.message(OnboardingStates.waiting_for_bot_token, ~F.text.startswith("/"))
async def process_token(message: Message, state: FSMContext, session: AsyncSession) -> None:
    token = (message.text or "").strip()
    admin = await _get_admin(session, message.from_user.id)
    if admin is None:
        # Nazariy jihatdan bo'lmasligi kerak, lekin FSM holati saqlanib qolgan
        # bo'lsa-yu, admin yozuvi topilmasa — boshidan boshlash so'raladi.
        await message.answer("Xatolik yuz berdi, iltimos /start bosing.")
        await state.clear()
        return

    try:
        temp_bot = Bot(token=token)
        me = await temp_bot.get_me()
    except (TokenValidationError, TelegramAPIError):
        await message.answer(
            "Bu token noto'g'ri ko'rinadi. @BotFather'dan olgan tokenni "
            "to'g'ridan-to'g'ri, o'zgartirmasdan yuboring."
        )
        return
    except Exception:  # noqa: BLE001 — kutilmagan xato ham foydalanuvchiga tushunarli xabar bersin
        logger.exception("Bot tokenini tekshirishda kutilmagan xato")
        await message.answer("Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
        return

    bot_row = BotModel(
        admin_id=admin.id,
        is_main=False,
        telegram_bot_id=me.id,
        token_encrypted=encrypt_token(token),
        username=me.username,
    )
    session.add(bot_row)
    await session.commit()

    registry.register_bot(temp_bot)
    webhook_url = f"{settings.webhook_base_url}/webhook/{token}"
    await temp_bot.set_webhook(url=webhook_url)

    await message.answer(
        f"Bot ulandi: @{me.username} ✅\n\n"
        "Endi shu botni kanalingizga admin sifatida qo'shing. Unga quyidagi "
        "huquqlarni bering: a'zolarni qo'shish/chiqarish, post yuborish/o'chirish.\n\n"
        "Botni admin qilib qo'shishingiz bilan GETOLOG buni avtomatik aniqlab, "
        "sizga xabar beradi.\n\n"
        "Agar bir necha daqiqadan so'ng ham xabar kelmasa, kanaldagi istalgan "
        "postni shu yerga forward qiling — tekshirib darhol javob beraman."
    )
    await state.clear()


async def _get_admin_bot(session: AsyncSession, admin_id: int) -> BotModel | None:
    result = await session.execute(
        select(BotModel).where(BotModel.admin_id == admin_id, BotModel.is_main.is_(False))
    )
    return result.scalar_one_or_none()


async def _get_bot_channel(session: AsyncSession, bot_id: int) -> Channel | None:
    result = await session.execute(select(Channel).where(Channel.bot_id == bot_id))
    return result.scalar_one_or_none()


async def _confirm_channel_admin_status(
    session: AsyncSession,
    bot_row: BotModel,
    bot_username: str,
    chat: Chat,
    member: ChatMemberAdministrator,
) -> None:
    """Bot kanalda admin ekanini tasdiqlagandan keyingi umumiy qadam: huquqni
    tekshirish, `Channel` yozuvini yangilash va adminga xabar berish.

    Ikkala manbadan ham chaqiriladi — `my_chat_member` hodisasidan (avtomatik)
    va kanaldan forward qilingan postdan (qo'lda tekshirish, agar avtomatik
    xabar biror sababga ko'ra kelmay qolsa).
    """
    permissions_ok = channel_service.has_required_rights(member)

    channel_row = await _get_bot_channel(session, bot_row.id)
    if channel_row is None:
        channel_row = Channel(
            bot_id=bot_row.id,
            telegram_channel_id=chat.id,
            title=chat.title or "",
            permissions_ok=permissions_ok,
        )
        session.add(channel_row)
    else:
        channel_row.title = chat.title or channel_row.title
        channel_row.permissions_ok = permissions_ok
    await session.commit()

    admin_result = await session.execute(select(Admin).where(Admin.id == bot_row.admin_id))
    admin = admin_result.scalar_one()
    main_bot = registry.get_main_bot()

    if permissions_ok:
        await main_bot.send_message(
            admin.telegram_id,
            f"Kanal muvaffaqiyatli ulandi: {channel_row.title} ✅\n\n"
            f"Muhim: @{bot_username} botiga shaxsan /start bosing — shunda "
            "obunachilarning to'lov cheklari shu bot orqali sizga kelishi mumkin bo'ladi.\n\n"
            "Keyin /narx komandasi orqali obunachilar uchun tarif narxlarini belgilang.",
        )
    else:
        missing = ", ".join(channel_service.missing_rights(member))
        await main_bot.send_message(
            admin.telegram_id,
            f"Bot kanalga qo'shildi, lekin yetarli huquqlar berilmagan.\n"
            f"Yetishmayotgan huquqlar: {missing}\n\n"
            "Iltimos, botga barcha kerakli huquqlarni bering.",
        )


@child_router.my_chat_member()
async def on_bot_status_changed_in_chat(event: ChatMemberUpdated, session: AsyncSession) -> None:
    """Admin o'z botini kanalga admin qilib qo'shganda shu hodisa keladi."""
    if event.chat.type != "channel":
        return
    if event.new_chat_member.status != "administrator":
        return

    result = await session.execute(
        select(BotModel).where(BotModel.telegram_bot_id == event.bot.id)
    )
    bot_row = result.scalar_one_or_none()
    if bot_row is None:
        return

    member = event.new_chat_member
    assert isinstance(member, ChatMemberAdministrator)
    await _confirm_channel_admin_status(session, bot_row, event.bot.username, event.chat, member)


@main_router.message(F.forward_origin)
async def process_forwarded_channel_post(message: Message, session: AsyncSession) -> None:
    """Avtomatik `my_chat_member` xabari kelmay qolsa — admin kanaldan forward
    qilgan postdan foydalanib, bot holatini qo'lda (faol) tekshiramiz.
    """
    if not isinstance(message.forward_origin, MessageOriginChannel):
        return

    admin = await _get_admin(session, message.from_user.id)
    if admin is None:
        return

    bot_row = await _get_admin_bot(session, admin.id)
    if bot_row is None:
        await message.answer(
            "Avval o'z botingizni ulang: @BotFather orqali yangi bot yarating "
            "va uning tokenini shu yerga yuboring."
        )
        return

    channel_chat = message.forward_origin.chat
    child_bot = registry.get_bot_by_telegram_id(bot_row.telegram_bot_id)
    if child_bot is None:
        await message.answer(
            "Server hozirgina qayta ishga tushgan bo'lishi mumkin — bir necha "
            "soniyadan so'ng postni qayta forward qilib ko'ring."
        )
        return

    try:
        member = await child_bot.get_chat_member(chat_id=channel_chat.id, user_id=child_bot.id)
    except TelegramAPIError:
        await message.answer(
            f"@{bot_row.username} boti \"{channel_chat.title}\" kanalida topilmadi. "
            "Botni kanalga admin sifatida qo'shganingizga ishonch hosil qiling."
        )
        return

    if member.status != "administrator":
        await message.answer(
            f"@{bot_row.username} boti \"{channel_chat.title}\" kanaliga hali "
            "admin qilib qo'shilmagan."
        )
        return

    assert isinstance(member, ChatMemberAdministrator)
    await _confirm_channel_admin_status(session, bot_row, bot_row.username, channel_chat, member)
