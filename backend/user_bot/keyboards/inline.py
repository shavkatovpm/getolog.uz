from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def language_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
    ])


def payment_method_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Karta orqali to'lash", callback_data="pay_card")],
    ])


def channel_select_kb(channels: list) -> InlineKeyboardMarkup:
    buttons = []
    for ch in channels:
        price_fmt = f"{float(ch.price):,.0f}".replace(",", " ")
        duration = {0: "umrbod", 1: "1 oy", 6: "6 oy", 12: "12 oy"}.get(
            ch.duration_months, f"{ch.duration_months} oy"
        )
        buttons.append([
            InlineKeyboardButton(
                text=f"📢 {ch.title} — {price_fmt} UZS / {duration}",
                callback_data=f"buy_ch_{ch.id}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def support_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📩 Adminga yozish", callback_data="support")],
    ])
