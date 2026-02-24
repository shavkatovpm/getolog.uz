from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from bot.middlewares.i18n import get_text
from config import config


def mod_menu_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    _ = lambda key: get_text(key, lang)
    buttons = []

    if config.server_url.startswith("https://"):
        buttons.append([InlineKeyboardButton(
            text="📱 Dashboard",
            web_app=WebAppInfo(url=f"{config.server_url}/mod_webapp"),
        )])

    buttons.extend([
        [InlineKeyboardButton(text=_('btn_mod_stats'), callback_data="mod_stats")],
        [InlineKeyboardButton(text=_('btn_mod_admins'), callback_data="mod_admins")],
        [InlineKeyboardButton(text=_('btn_mod_change_pwd'), callback_data="mod_change_password")],
        [InlineKeyboardButton(text=_('btn_mod_logout'), callback_data="mod_logout")],
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def mod_back_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    _ = lambda key: get_text(key, lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_('btn_back'), callback_data="mod_menu")],
    ])
