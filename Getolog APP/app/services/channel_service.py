"""Kanal bilan bog'liq Telegram amallari: huquq tekshirish, taklif havolasi, chiqarish."""

from aiogram import Bot
from aiogram.types import ChatMemberAdministrator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot import registry
from app.db.models import Bot as BotModel, Channel

# Bot kanalda obuna boshqaruvini to'liq bajarishi uchun zarur huquqlar:
# a'zo qo'shish (invite havola yaratish), a'zo chiqarish (ban/unban),
# post joylash va postni o'chirish (avto-post funksiyasi uchun, keyingi bosqich).
REQUIRED_RIGHTS = (
    "can_invite_users",
    "can_restrict_members",
    "can_post_messages",
    "can_delete_messages",
)


def has_required_rights(member: ChatMemberAdministrator) -> bool:
    """Bot kanalda kerakli barcha admin huquqlariga ega ekanini tekshiradi."""
    return all(getattr(member, right, False) for right in REQUIRED_RIGHTS)


def missing_rights(member: ChatMemberAdministrator) -> list[str]:
    """Yetishmayotgan huquqlar ro'yxatini qaytaradi (adminga xabar berish uchun)."""
    return [right for right in REQUIRED_RIGHTS if not getattr(member, right, False)]


async def create_single_use_invite_link(bot: Bot, chat_id: int) -> str:
    """Bir marta ishlatiladigan, faqat bitta odam kira oladigan taklif havolasi yaratadi.

    Bu Telegram cheklovlari doirasidagi yagona to'g'ri usul — Bot API orqali
    odamni kanalga to'g'ridan-to'g'ri qo'shib bo'lmaydi, faqat shunday havola
    orqali taklif qilish mumkin.
    """
    link = await bot.create_chat_invite_link(chat_id=chat_id, member_limit=1)
    return link.invite_link


async def remove_subscriber(bot: Bot, chat_id: int, user_id: int) -> None:
    """Obunachini kanaldan chiqaradi.

    `ban` + darrov `unban` — shunda obunachi kelajakda yangi taklif havolasi
    orqali qayta kira olishi mumkin (butunlay bloklanmaydi).
    """
    await bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
    await bot.unban_chat_member(chat_id=chat_id, user_id=user_id)


async def get_bot_for_channel(session: AsyncSession, channel_id: int) -> tuple[Channel, Bot | None]:
    """Kanalga tegishli aiogram Bot obyektini topib beradi (registrdan, xotiradan).

    Bot topilmasa (masalan server hozirgina qayta ishga tushgan bo'lsa) `None`
    qaytaradi — chaqiruvchi tomon buni yumshoq holat sifatida hisobga olishi kerak.
    """
    channel_result = await session.execute(select(Channel).where(Channel.id == channel_id))
    channel = channel_result.scalar_one()
    bot_row_result = await session.execute(select(BotModel).where(BotModel.id == channel.bot_id))
    bot_row = bot_row_result.scalar_one()
    return channel, registry.get_bot_by_telegram_id(bot_row.telegram_bot_id)
