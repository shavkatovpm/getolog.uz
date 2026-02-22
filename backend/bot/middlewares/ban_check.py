from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from db.engine import async_session
from services.admin_service import get_admin_by_telegram_id


class BanCheckMiddleware(BaseMiddleware):
    """Check if user admin is banned before processing."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id = None
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        if user_id:
            async with async_session() as session:
                admin = await get_admin_by_telegram_id(session, user_id)
                if admin and admin.banned:
                    if isinstance(event, Message):
                        await event.answer("⛔ Sizning akkauntingiz bloklangan.")
                    elif isinstance(event, CallbackQuery):
                        await event.answer("⛔ Bloklangan.", show_alert=True)
                    return

        return await handler(event, data)
