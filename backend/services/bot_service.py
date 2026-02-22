import logging

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.encryption import encrypt_token, decrypt_token
from db.models import UserBot, Channel

logger = logging.getLogger(__name__)


async def validate_token(token: str) -> dict | None:
    """Validate a bot token by calling Telegram API. Returns bot info or None."""
    try:
        bot = Bot(token=token)
        info = await bot.get_me()
        await bot.session.close()
        return {
            "id": info.id,
            "username": info.username,
            "first_name": info.first_name,
        }
    except Exception:
        return None


async def create_bot(
    session: AsyncSession,
    user_admin_id: int,
    token: str,
    bot_username: str,
) -> UserBot:
    """Create a new bot record with encrypted token."""
    user_bot = UserBot(
        user_admin_id=user_admin_id,
        bot_token=encrypt_token(token),
        bot_username=bot_username,
    )
    session.add(user_bot)
    await session.commit()
    return user_bot


async def get_bot_by_admin(session: AsyncSession, admin_id: int) -> UserBot | None:
    result = await session.execute(
        select(UserBot).where(
            UserBot.user_admin_id == admin_id,
            UserBot.is_active == True,
        )
    )
    return result.scalar_one_or_none()


async def get_bot_by_id(session: AsyncSession, bot_id: int) -> UserBot | None:
    result = await session.execute(
        select(UserBot).where(UserBot.id == bot_id)
    )
    return result.scalar_one_or_none()


async def get_all_active_bots(session: AsyncSession) -> list[UserBot]:
    result = await session.execute(
        select(UserBot).where(UserBot.is_active == True)
    )
    return list(result.scalars().all())


async def deactivate_bot(session: AsyncSession, bot_id: int) -> bool:
    result = await session.execute(
        select(UserBot).where(UserBot.id == bot_id)
    )
    user_bot = result.scalar_one_or_none()
    if not user_bot:
        return False
    user_bot.is_active = False
    await session.commit()
    return True


async def update_bot_settings(
    session: AsyncSession,
    bot_id: int,
    welcome_message: str | None = None,
    payment_method: str | None = None,
    card_number: str | None = None,
) -> UserBot | None:
    result = await session.execute(
        select(UserBot).where(UserBot.id == bot_id)
    )
    user_bot = result.scalar_one_or_none()
    if not user_bot:
        return None

    if welcome_message is not None:
        user_bot.welcome_message = welcome_message
    if payment_method is not None:
        user_bot.payment_method = payment_method
    if card_number is not None:
        user_bot.card_number = card_number

    await session.commit()
    return user_bot


async def add_channel(
    session: AsyncSession,
    user_bot_id: int,
    telegram_chat_id: int,
    chat_type: str,
    title: str,
    price: float,
    duration_months: int,
) -> Channel:
    channel = Channel(
        user_bot_id=user_bot_id,
        telegram_chat_id=telegram_chat_id,
        type=chat_type,
        title=title,
        price=price,
        duration_months=duration_months,
    )
    session.add(channel)
    await session.commit()
    return channel


async def get_channels_by_bot(session: AsyncSession, bot_id: int) -> list[Channel]:
    result = await session.execute(
        select(Channel).where(Channel.user_bot_id == bot_id)
    )
    return list(result.scalars().all())
