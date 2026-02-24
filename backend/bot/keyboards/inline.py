from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from config import config


def main_menu_kb() -> InlineKeyboardMarkup:
    buttons = []
    # WebApp button only works with HTTPS URLs (Telegram requirement)
    if config.server_url.startswith("https://"):
        buttons.append([InlineKeyboardButton(
            text="Dashboard",
            web_app=WebAppInfo(url=f"{config.server_url}/webapp"),
        )])
    buttons.extend([
        [
            InlineKeyboardButton(text="➕ Bot qo'shish", callback_data="create_bot"),
            InlineKeyboardButton(text="🤖 Mening botlarim", callback_data="my_bots"),
        ],
        [
            InlineKeyboardButton(text="📦 Obuna", callback_data="my_subscription"),
            InlineKeyboardButton(text="❓ Yordam", callback_data="help"),
        ],
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def bot_dashboard_kb(bot_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data=f"bot_stats_{bot_id}"),
            InlineKeyboardButton(text="💳 To'lovlar", callback_data=f"bot_payments_{bot_id}"),
        ],
        [
            InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data=f"bot_users_{bot_id}"),
            InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data=f"bot_settings_{bot_id}"),
        ],
        [
            InlineKeyboardButton(text="🔄 Boshqa bot", callback_data="my_bots"),
            InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_menu"),
        ],
    ])


def back_bot_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_bot_dashboard")],
    ])


def settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Salomlash xabari", callback_data="set_welcome")],
        [InlineKeyboardButton(text="💳 Karta raqami", callback_data="set_card")],
        [InlineKeyboardButton(text="💰 Narx o'zgartirish", callback_data="set_price")],
        [InlineKeyboardButton(text="👥 Hamkorlar", callback_data="manage_collabs")],
        [InlineKeyboardButton(text="🗑 Botni o'chirish", callback_data="deactivate_bot")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_bot_dashboard")],
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


def card_or_free_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆓 Kirish bepul", callback_data="reg_free_mode")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_menu")],
    ])


def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_menu")],
    ])


def check_channel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Tekshirish", callback_data="check_channel")],
        [InlineKeyboardButton(text="✏️ Qo'lda kiritish", callback_data="manual_channel_id")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_menu")],
    ])


def duration_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 oy", callback_data="dur_1")],
        [InlineKeyboardButton(text="6 oy", callback_data="dur_6")],
        [InlineKeyboardButton(text="12 oy", callback_data="dur_12")],
        [InlineKeyboardButton(text="Umrbod", callback_data="dur_0")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="back_menu")],
    ])
