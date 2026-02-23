from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def mod_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="mod_stats")],
        [InlineKeyboardButton(text="👥 Adminlar", callback_data="mod_admins")],
        [InlineKeyboardButton(text="💳 To'lovlar", callback_data="mod_payments")],
        [InlineKeyboardButton(text="🤖 Botlar", callback_data="mod_bots")],
        [InlineKeyboardButton(text="🔑 Parolni o'zgartirish", callback_data="mod_change_password")],
        [InlineKeyboardButton(text="🚪 Chiqish", callback_data="mod_logout")],
    ])


def mod_back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="mod_menu")],
    ])
