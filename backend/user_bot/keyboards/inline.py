from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.middlewares.i18n import get_text


def language_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
    ])


def payment_method_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    _ = lambda key: get_text(key, lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_('payment_card'), callback_data="pay_card")],
        [InlineKeyboardButton(text=_('btn_cancel'), callback_data="cancel_payment")],
    ])


def channel_select_kb(channels: list, lang: str = "uz") -> InlineKeyboardMarkup:
    _ = lambda key: get_text(key, lang)
    buttons = []
    for ch in channels:
        price_fmt = f"{float(ch.price):,.0f}".replace(",", " ")
        duration = {
            0: _("duration_lifetime"), 1: _("duration_1m"),
            6: _("duration_6m"), 12: _("duration_12m"),
        }.get(ch.duration_months, f"{ch.duration_months}")
        buttons.append([
            InlineKeyboardButton(
                text=f"{ch.title} — {price_fmt} UZS / {duration}",
                callback_data=f"buy_ch_{ch.id}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def support_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    _ = lambda key: get_text(key, lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_('support'), callback_data="support")],
    ])
