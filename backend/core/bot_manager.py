import asyncio
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
    """Manages all User Admin bots via webhooks (prod) or polling (dev)."""

    def __init__(self, user_bot_router: Router, storage: RedisStorage, is_production: bool = True):
        self.bots: dict[int, Bot] = {}  # user_bot_id -> Bot
        self._secret_to_bot_id: dict[str, int] = {}  # secret_hash -> user_bot_id
        self._secret_to_bot: dict[str, Bot] = {}  # secret_hash -> Bot
        self._polling_tasks: dict[int, asyncio.Task] = {}  # dev mode polling tasks
        self._is_production = is_production

        # Single shared dispatcher for all user bots
        # FSM state is scoped by (bot_id, chat_id, user_id) in Redis
        self._dp = Dispatcher(storage=storage)
        self._dp.include_router(user_bot_router)

    async def register_bot(self, user_bot_id: int, encrypted_token: str) -> Bot | None:
        """Register a new bot with webhook (prod) or polling (dev)."""
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

            self.bots[user_bot_id] = bot

            if self._is_production:
                # Set webhook using secret hash instead of raw token
                secret = _make_webhook_secret(token)
                webhook_url = f"{config.webhook_url}/{secret}"
                await bot.set_webhook(webhook_url)
                self._secret_to_bot_id[secret] = user_bot_id
                self._secret_to_bot[secret] = bot
            else:
                # Dev mode: use polling instead of webhooks
                # Don't drop pending updates so /start sent before polling aren't lost
                await bot.delete_webhook(drop_pending_updates=False)
                await asyncio.sleep(0.5)  # Let Telegram switch from webhook to polling mode
                task = asyncio.create_task(self._poll_bot(user_bot_id, bot))
                self._polling_tasks[user_bot_id] = task

            logger.info(f"Bot registered: @{bot_info.username} (id={user_bot_id})")
            return bot

        except Exception as e:
            logger.error(f"Failed to register bot {user_bot_id}: {e}")
            return None

    async def _poll_bot(self, user_bot_id: int, bot: Bot):
        """Poll updates for a single user bot (dev mode only)."""
        offset = 0
        bot_info = await bot.get_me()
        logger.info(f"Polling ACTIVE for @{bot_info.username} (id={user_bot_id}, bot_id={bot_info.id})")
        allowed = ["message", "callback_query", "my_chat_member", "chat_member"]
        while True:
            try:
                updates = await bot.get_updates(
                    offset=offset,
                    timeout=10,
                    allowed_updates=allowed,
                )
                for update in updates:
                    logger.info(f"[bot {user_bot_id}] Update #{update.update_id}: {update.message or update.callback_query}")
                    try:
                        await self._dp.feed_update(bot, update)
                    except Exception as e:
                        logger.error(f"Error processing update for bot {user_bot_id}: {e}", exc_info=True)
                    offset = update.update_id + 1
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Polling error for bot {user_bot_id}: {e}", exc_info=True)
                await asyncio.sleep(5)

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
        """Stop a bot and remove its webhook/polling."""
        # Cancel polling task if running (dev mode)
        task = self._polling_tasks.pop(user_bot_id, None)
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

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
