import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from redis.asyncio import Redis


class RateLimitMiddleware(BaseMiddleware):
    """Rate limit: max 3 requests per second per user."""

    def __init__(self, redis: Redis, limit: int = 3, window: int = 1):
        self.redis = redis
        self.limit = limit
        self.window = window

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
            key = f"rate:{user_id}"
            current = await self.redis.incr(key)
            if current == 1:
                await self.redis.expire(key, self.window)
            if current > self.limit:
                return  # Silently drop

        return await handler(event, data)
