from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 Bot yaratish", callback_data="create_bot")],
        [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="stats")],
        [InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="manage_users")],
        [InlineKeyboardButton(text="💳 To'lovlar", callback_data="payments")],
    ])


def settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Salomlash xabari", callback_data="set_welcome")],
        [InlineKeyboardButton(text="💳 Karta raqami", callback_data="set_card")],
        [InlineKeyboardButton(text="💰 Narx o'zgartirish", callback_data="set_price")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_menu")],
    ])


def confirm_kb(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"{prefix}_confirm"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"{prefix}_cancel"),
        ],
    ])


def payment_action_kb(payment_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Tasdiqlash",
                callback_data=f"pay_approve_{payment_id}",
            ),
            InlineKeyboardButton(
                text="❌ Rad etish",
                callback_data=f"pay_reject_{payment_id}",
            ),
        ],
    ])


def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_menu")],
    ])


def duration_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 oy", callback_data="dur_1")],
        [InlineKeyboardButton(text="6 oy", callback_data="dur_6")],
        [InlineKeyboardButton(text="12 oy", callback_data="dur_12")],
        [InlineKeyboardButton(text="Umrbod", callback_data="dur_0")],
    ])
