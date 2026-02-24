from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from config import config


def mod_menu_kb() -> InlineKeyboardMarkup:
    buttons = []

    # WebApp button (only works with HTTPS)
    if config.server_url.startswith("https://"):
        buttons.append([InlineKeyboardButton(
            text="📱 Dashboard",
            web_app=WebAppInfo(url=f"{config.server_url}/mod_webapp"),
        )])

    buttons.extend([
        [InlineKeyboardButton(text="📊 Statistika", callback_data="mod_stats")],
        [InlineKeyboardButton(text="👥 Adminlar", callback_data="mod_admins")],
        [InlineKeyboardButton(text="🔑 Parolni o'zgartirish", callback_data="mod_change_password")],
        [InlineKeyboardButton(text="🚪 Chiqish", callback_data="mod_logout")],
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def mod_back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="mod_menu")],
    ])
