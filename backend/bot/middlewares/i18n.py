import json
import os
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from db.engine import async_session
from services.admin_service import get_admin_by_telegram_id

# Load translations
_translations: dict[str, dict] = {}
_i18n_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "i18n")

for lang in ("uz", "ru", "en"):
    path = os.path.join(_i18n_dir, f"{lang}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            _translations[lang] = json.load(f)


def get_text(key: str, lang: str = "uz") -> str:
    """Get translated text by key."""
    return _translations.get(lang, _translations.get("uz", {})).get(key, key)


class I18nMiddleware(BaseMiddleware):
    """Inject i18n helper into handler data, detecting language from DB."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        lang = "uz"

        user_id = None
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        if user_id:
            try:
                async with async_session() as session:
                    admin = await get_admin_by_telegram_id(session, user_id)
                    if admin and admin.language:
                        lang = admin.language
            except Exception:
                pass

        data["_"] = lambda key: get_text(key, lang)
        data["i18n_lang"] = lang

        return await handler(event, data)
