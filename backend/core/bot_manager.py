import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Update

from config import config
from core.encryption import decrypt_token

logger = logging.getLogger(__name__)


class BotManager:
    """Manages all User Admin bots via webhooks."""

    def __init__(self, user_bot_router: Router, storage: RedisStorage):
        self.bots: dict[int, Bot] = {}  # user_bot_id -> Bot
        self.dispatchers: dict[int, Dispatcher] = {}  # user_bot_id -> Dispatcher
        self._router = user_bot_router
        self._storage = storage
        self._token_to_bot_id: dict[str, int] = {}  # token_hash -> user_bot_id

    async def register_bot(self, user_bot_id: int, encrypted_token: str) -> Bot | None:
        """Register a new bot with webhook."""
        try:
            token = decrypt_token(encrypted_token)
            bot = Bot(
                token=token,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML),
            )

            # Validate token
            bot_info = await bot.get_me()
            if not bot_info:
                await bot.session.close()
                return None

            # Create dispatcher
            dp = Dispatcher(storage=self._storage)
            dp.include_router(self._router)

            # Set webhook
            webhook_url = f"{config.webhook_url}/{token}"
            await bot.set_webhook(webhook_url)

            # Store
            self.bots[user_bot_id] = bot
            self.dispatchers[user_bot_id] = dp
            self._token_to_bot_id[token] = user_bot_id

            logger.info(f"Bot registered: @{bot_info.username} (id={user_bot_id})")
            return bot

        except Exception as e:
            logger.error(f"Failed to register bot {user_bot_id}: {e}")
            return None

    async def handle_update(self, token: str, update_data: dict) -> bool:
        """Route incoming webhook update to the correct bot/dispatcher."""
        bot_id = self._token_to_bot_id.get(token)
        if bot_id is None:
            logger.warning(f"Update for unknown token")
            return False

        bot = self.bots.get(bot_id)
        dp = self.dispatchers.get(bot_id)
        if not bot or not dp:
            return False

        try:
            update = Update(**update_data)
            await dp.feed_update(bot, update)
            return True
        except Exception as e:
            logger.error(f"Error handling update for bot {bot_id}: {e}")
            return False

    async def stop_bot(self, user_bot_id: int):
        """Stop a bot and remove its webhook."""
        bot = self.bots.pop(user_bot_id, None)
        if bot:
            try:
                await bot.delete_webhook()
            except Exception:
                pass
            await bot.session.close()

            # Remove token mapping
            token_to_remove = None
            for token, bid in self._token_to_bot_id.items():
                if bid == user_bot_id:
                    token_to_remove = token
                    break
            if token_to_remove:
                del self._token_to_bot_id[token_to_remove]

        self.dispatchers.pop(user_bot_id, None)
        logger.info(f"Bot stopped: id={user_bot_id}")

    async def health_check(self) -> dict[int, str]:
        """Check all bots' health status."""
        results = {}
        for bot_id, bot in self.bots.items():
            try:
                await bot.get_me()
                results[bot_id] = "alive"
            except Exception:
                results[bot_id] = "dead"
        return results

    async def shutdown(self):
        """Gracefully shutdown all bots."""
        for bot_id in list(self.bots.keys()):
            await self.stop_bot(bot_id)
        logger.info("All bots stopped")

    @property
    def active_count(self) -> int:
        return len(self.bots)
