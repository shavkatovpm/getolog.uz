from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

from bot.middlewares.i18n import get_text
from core.cache import cache_get, cache_set
from db.engine import async_session
from db.models import UserBot, AdminSubscription
from sqlalchemy import select, and_
from utils.constants import PlanName, SubStatus


class BrandingMiddleware(BaseMiddleware):
    """Show Getolog branding for bots on free/standard plan.

    Plan logic:
    - free & standard: show branding text
    - premium: no branding
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        result = await handler(event, data)

        # Only inject branding for /start messages
        if isinstance(event, Message) and event.text and event.text.startswith("/start"):
            try:
                bot_info = await event.bot.get_me()

                # Check cache first (120s TTL — plan rarely changes)
                cache_key = f"premium:{bot_info.username}"
                cached = await cache_get(cache_key)
                if cached is not None:
                    if not cached.get("is_premium"):
                        await event.answer(get_text("branding_text", "uz"))
                    return result

                async with async_session() as session:
                    bot_result = await session.execute(
                        select(UserBot).where(UserBot.bot_username == bot_info.username)
                    )
                    user_bot = bot_result.scalar_one_or_none()

                    is_premium = False
                    if user_bot:
                        sub_result = await session.execute(
                            select(AdminSubscription).where(
                                and_(
                                    AdminSubscription.user_admin_id == user_bot.user_admin_id,
                                    AdminSubscription.status == SubStatus.ACTIVE,
                                    AdminSubscription.plan == PlanName.PREMIUM,
                                )
                            )
                        )
                        is_premium = sub_result.scalar_one_or_none() is not None

                    await cache_set(cache_key, {"is_premium": is_premium}, ttl=120)

                    if not is_premium:
                        await event.answer(get_text("branding_text", "uz"))
            except Exception:
                pass

        return result
