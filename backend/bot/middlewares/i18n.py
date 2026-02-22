import json
import os
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

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
    """Inject i18n helper into handler data."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Default language
        lang = "uz"

        # Try to get from FSM data or user record
        # For now, just pass the helper function
        data["_"] = lambda key: get_text(key, lang)
        data["i18n_lang"] = lang

        return await handler(event, data)
