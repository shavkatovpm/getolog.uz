from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from bot.middlewares.i18n import get_text
from config import config


def main_menu_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    _ = lambda key: get_text(key, lang)
    buttons = []
    if config.server_url.startswith("https://"):
        buttons.append([InlineKeyboardButton(
            text="Dashboard",
            web_app=WebAppInfo(url=f"{config.server_url}/webapp"),
        )])
    buttons.extend([
        [
            InlineKeyboardButton(text=_('btn_create_bot'), callback_data="create_bot"),
            InlineKeyboardButton(text=_('btn_my_bots'), callback_data="my_bots"),
        ],
        [
            InlineKeyboardButton(text=_('btn_subscription'), callback_data="my_subscription"),
            InlineKeyboardButton(text=_('btn_help'), callback_data="help"),
        ],
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def bot_dashboard_kb(bot_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    _ = lambda key: get_text(key, lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=_('btn_stats'), callback_data=f"bot_stats_{bot_id}"),
            InlineKeyboardButton(text=_('btn_payments'), callback_data=f"bot_payments_{bot_id}"),
        ],
        [
            InlineKeyboardButton(text=_('btn_users'), callback_data=f"bot_users_{bot_id}"),
            InlineKeyboardButton(text=_('btn_settings'), callback_data=f"bot_settings_{bot_id}"),
        ],
        [
            InlineKeyboardButton(text=_('btn_other_bot'), callback_data="my_bots"),
            InlineKeyboardButton(text=_('btn_main_menu'), callback_data="back_menu"),
        ],
    ])


def back_bot_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    _ = lambda key: get_text(key, lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_('btn_back'), callback_data="back_bot_dashboard")],
    ])


def settings_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    _ = lambda key: get_text(key, lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_('btn_welcome_msg'), callback_data="set_welcome")],
        [InlineKeyboardButton(text=_('btn_card_number'), callback_data="set_card")],
        [InlineKeyboardButton(text=_('btn_change_price'), callback_data="set_price")],
        [InlineKeyboardButton(text=_('btn_collaborators'), callback_data="manage_collabs")],
        [InlineKeyboardButton(text=_('btn_delete_bot'), callback_data="deactivate_bot")],
        [InlineKeyboardButton(text=_('btn_back'), callback_data="back_bot_dashboard")],
    ])


def confirm_kb(prefix: str, lang: str = "uz") -> InlineKeyboardMarkup:
    _ = lambda key: get_text(key, lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=_('btn_approve'), callback_data=f"{prefix}_confirm"),
            InlineKeyboardButton(text=_('btn_cancel'), callback_data=f"{prefix}_cancel"),
        ],
    ])


def payment_action_kb(payment_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    _ = lambda key: get_text(key, lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_('btn_approve'),
                callback_data=f"pay_approve_{payment_id}",
            ),
            InlineKeyboardButton(
                text=_('btn_reject'),
                callback_data=f"pay_reject_{payment_id}",
            ),
        ],
    ])


def card_or_free_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    _ = lambda key: get_text(key, lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_('btn_free_access'), callback_data="reg_free_mode")],
        [InlineKeyboardButton(text=_('btn_back'), callback_data="back_menu")],
    ])


def back_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    _ = lambda key: get_text(key, lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_('btn_back'), callback_data="back_menu")],
    ])


def check_channel_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    _ = lambda key: get_text(key, lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_('btn_check'), callback_data="check_channel")],
        [InlineKeyboardButton(text=_('btn_manual_input'), callback_data="manual_channel_id")],
        [InlineKeyboardButton(text=_('btn_back'), callback_data="back_menu")],
    ])


def duration_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    _ = lambda key: get_text(key, lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_("duration_1m"), callback_data="dur_1")],
        [InlineKeyboardButton(text=_("duration_6m"), callback_data="dur_6")],
        [InlineKeyboardButton(text=_("duration_12m"), callback_data="dur_12")],
        [InlineKeyboardButton(text=_("duration_lifetime"), callback_data="dur_0")],
        [InlineKeyboardButton(text=_('btn_cancel'), callback_data="back_menu")],
    ])


def language_select_kb() -> InlineKeyboardMarkup:
    """Language selection for main bot admin."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="admin_lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="admin_lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="admin_lang_en")],
    ])
