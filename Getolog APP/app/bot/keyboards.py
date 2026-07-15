"""Botlarda ishlatiladigan inline tugmalar to'plamlari.

Diqqat: bosh bot va admin boti endi faqat onboarding va obunachi oqimi uchun
inline tugma ishlatadi — boshqaruv (tarif, to'lov tasdiqlash) dashboard
(`app/api`) orqali amalga oshadi.
"""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.db.models import SubscriptionPlan, TariffPlan

TARIFF_LABELS = {
    TariffPlan.free: "Bepul (sinov)",
    TariffPlan.start: "Start — $50",
    TariffPlan.pro: "Pro — $100",
    TariffPlan.business: "Biznes — $150",
    TariffPlan.scale: "Scale",
}


def plan_choice_keyboard(plans: list[SubscriptionPlan]) -> InlineKeyboardMarkup:
    """Obunachiga kanal uchun mavjud tarif rejalarini ko'rsatish uchun tugmalar."""
    builder = InlineKeyboardBuilder()
    for plan in plans:
        text = f"{plan.duration_months} oy — {plan.price:g} {plan.currency}"
        builder.button(text=text, callback_data=f"choose_plan:{plan.id}")
    builder.adjust(1)
    return builder.as_markup()
