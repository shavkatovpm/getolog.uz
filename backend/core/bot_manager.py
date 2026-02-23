import hashlib
import hmac
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Update

from config import config
from core.encryption import decrypt_token

logger = logging.getLogger(__name__)


def _make_webhook_secret(token: str) -> str:
    """Create a URL-safe secret hash from bot token. Token never appears in URL."""
    key = (config.encryption_key or "getolog").encode()
    return hmac.new(key, token.encode(), hashlib.sha256).hexdigest()[:32]


class BotManager:
    """Manages all User Admin bots via webhooks."""

    def __init__(self, user_bot_router: Router, storage: RedisStorage):
        self.bots: dict[int, Bot] = {}  # user_bot_id -> Bot
        self._secret_to_bot_id: dict[str, int] = {}  # secret_hash -> user_bot_id
        self._secret_to_bot: dict[str, Bot] = {}  # secret_hash -> Bot

        # Single shared dispatcher for all user bots
        # FSM state is scoped by (bot_id, chat_id, user_id) in Redis
        self._dp = Dispatcher(storage=storage)
        self._dp.include_router(user_bot_router)

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

            # Set webhook using secret hash instead of raw token
            secret = _make_webhook_secret(token)
            webhook_url = f"{config.webhook_url}/{secret}"
            await bot.set_webhook(webhook_url)

            # Store
            self.bots[user_bot_id] = bot
            self._secret_to_bot_id[secret] = user_bot_id
            self._secret_to_bot[secret] = bot

            logger.info(f"Bot registered: @{bot_info.username} (id={user_bot_id})")
            return bot

        except Exception as e:
            logger.error(f"Failed to register bot {user_bot_id}: {e}")
            return None

    async def handle_update(self, secret: str, update_data: dict) -> bool:
        """Route incoming webhook update to the correct bot."""
        bot_id = self._secret_to_bot_id.get(secret)
        if bot_id is None:
            logger.warning("Update for unknown webhook secret")
            return False

        bot = self._secret_to_bot.get(secret)
        if not bot:
            return False

        try:
            update = Update(**update_data)
            await self._dp.feed_update(bot, update)
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

            # Remove secret mapping
            secret_to_remove = None
            for secret, bid in self._secret_to_bot_id.items():
                if bid == user_bot_id:
                    secret_to_remove = secret
                    break
            if secret_to_remove:
                del self._secret_to_bot_id[secret_to_remove]
                del self._secret_to_bot[secret_to_remove]

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
