"""Ishlab turgan barcha aiogram Bot obyektlarini xotirada ushlab turadi.

GETOLOG bitta serverda ko'plab bot tokenini boshqaradi (bosh bot + har bir
admin o'z boti). Bot obyektlari ikki xil kalit bo'yicha qidiriladi:
- token bo'yicha — webhook so'rovi URL'da tokenni olib keladi;
- Telegram raqamli ID bo'yicha — scheduler kabi joylarda bazadan olingan
  `telegram_bot_id` orqali tezkor topish uchun (tokenni deshifrlashga hojat
  qolmaydi).
"""

from aiogram import Bot

from app.config import settings

_bots_by_token: dict[str, Bot] = {}
_bots_by_telegram_id: dict[int, Bot] = {}


def register_bot(bot: Bot) -> None:
    """Yangi bot obyektini registrga qo'shadi (masalan admin token ulaganda)."""
    _bots_by_token[bot.token] = bot
    _bots_by_telegram_id[bot.id] = bot


def get_bot_by_token(token: str) -> Bot | None:
    """Token bo'yicha oldindan yaratilgan Bot obyektini qaytaradi, topilmasa None."""
    return _bots_by_token.get(token)


def get_bot_by_telegram_id(telegram_id: int) -> Bot | None:
    """Botning Telegram raqamli ID'si bo'yicha Bot obyektini qaytaradi."""
    return _bots_by_telegram_id.get(telegram_id)


def all_bots() -> list[Bot]:
    """Server yopilganda barcha bot sessiyalarini to'g'ri yopish uchun ishlatiladi."""
    return list(_bots_by_token.values())


def get_main_bot() -> Bot:
    """Adminlarga xabar yuborish uchun GETOLOG bosh botining obyektini qaytaradi."""
    bot = get_bot_by_token(settings.main_bot_token)
    if bot is None:
        raise RuntimeError("Bosh bot hali registrga qo'shilmagan — server to'g'ri ishga tushmagan")
    return bot
