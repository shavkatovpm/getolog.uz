from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

from db.engine import async_session
from db.models import UserBot, AdminSubscription
from sqlalchemy import select, and_


class AdInjectMiddleware(BaseMiddleware):
    """Show Getolog ad for bots on free plan."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        result = await handler(event, data)

        # Only inject ad for /start messages
        if isinstance(event, Message) and event.text and event.text.startswith("/start"):
            try:
                bot_info = await event.bot.get_me()
                async with async_session() as session:
                    bot_result = await session.execute(
                        select(UserBot).where(UserBot.bot_username == bot_info.username)
                    )
                    user_bot = bot_result.scalar_one_or_none()

                    if user_bot:
                        # Check if admin has paid subscription
                        sub_result = await session.execute(
                            select(AdminSubscription).where(
                                and_(
                                    AdminSubscription.user_admin_id == user_bot.user_admin_id,
                                    AdminSubscription.status == "active",
                                    AdminSubscription.plan != "free",
                                )
                            )
                        )
                        has_paid = sub_result.scalar_one_or_none()

                        if not has_paid:
                            await event.answer(
                                "🤖 <i>Getolog yordamida yaratilgan — getolog.uz</i>",
                            )
            except Exception:
                pass

        return result
