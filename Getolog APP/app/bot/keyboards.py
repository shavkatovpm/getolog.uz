"""Botlarda ishlatiladigan inline tugmalar to'plamlari.

Diqqat: bosh bot va admin boti endi faqat onboarding va obunachi oqimi uchun
inline tugma ishlatadi — boshqaruv (tarif, to'lov tasdiqlash) dashboard
(`app/api`) orqali amalga oshadi.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import settings
from app.db.models import SubscriptionPlan, TariffPlan
from app.services.formatting import format_amount
from app.services.subscription_service import plan_duration_label

#  getolog.uz/price'dagi narxlar bilan bir xil bo'lishi shart.
TARIFF_LABELS = {
    TariffPlan.free: "Bepul",
    TariffPlan.minimal: "Minimal — 295 000 so'm/oy",
    TariffPlan.start: "Standart — 590 000 so'm/oy",
    TariffPlan.pro: "Pro — 1 270 000 so'm/oy",
    TariffPlan.business: "Biznes — 1 890 000 so'm/oy",
    TariffPlan.scale: "Scale",
}


def plan_choice_keyboard(plans: list[SubscriptionPlan]) -> InlineKeyboardMarkup:
    """Obunachiga kanal uchun mavjud tarif rejalarini ko'rsatish uchun tugmalar."""
    builder = InlineKeyboardBuilder()
    for plan in plans:
        text = f"{plan_duration_label(plan)} — {format_amount(plan.price)} {plan.currency}"
        builder.button(text=text, callback_data=f"choose_plan:{plan.id}")
    builder.adjust(1)
    return builder.as_markup()


def start_menu_keyboard(*, has_bots: bool, any_pending: bool = False) -> InlineKeyboardMarkup:
    """`/start` bosilganda (yoki "✅ Admin qildim" bosilib holat yangilanganda)
    ko'rsatiladigan asosiy menyu.

    Uchta holat bor:
    - Hali birorta ham bot ulanmagan — faqat "Bot qo'shish" tugmasi.
    - Kamida bitta bot/kanal hali admin bo'lishini kutayotgan bo'lsa — e'tibor
      chalg'imasligi uchun FAQAT "✅ Admin qildim" tugmasi ko'rsatiladi.
    - Hammasi ulangan (kutilayotgani yo'q) — dashboard (Mini App) va yana bot
      qo'shish tugmalari. Parolni olish endi tugma orqali emas, faqat
      `/parol` komandasi orqali (`cmd_password`).
    """
    builder = InlineKeyboardBuilder()
    if not has_bots:
        builder.row(InlineKeyboardButton(text="➕ Bot qo'shish", callback_data="add_bot"))
        return builder.as_markup()

    if any_pending:
        builder.row(InlineKeyboardButton(text="✅ Admin qildim", callback_data="check_admin"))
        builder.row(InlineKeyboardButton(text="🆘 Yordam kerak", callback_data="request_help"))
        return builder.as_markup()

    builder.row(
        InlineKeyboardButton(
            text="🚀 Dashboardga kirish", web_app=WebAppInfo(url=settings.dashboard_origin)
        )
    )
    builder.row(InlineKeyboardButton(text="➕ Bot qo'shish", callback_data="add_bot"))
    return builder.as_markup()


def help_button_keyboard() -> InlineKeyboardMarkup:
    """Bot ulash bosqichida chalkashib qolgan foydalanuvchi uchun — bosilsa
    sovuq murojaat emas, o'zi so'ragan yordam sifatida super adminga xabar boradi."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🆘 Yordam kerak", callback_data="request_help"))
    return builder.as_markup()


def payment_review_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    """To'lov bildirishnomasi ostida — dashboard'ga kirmasdan tezkor tasdiqlash/rad etish."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"pay_approve:{payment_id}"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"pay_reject:{payment_id}"),
    )
    return builder.as_markup()


def channel_invite_keyboard(invite_link: str, *, is_group: bool = False) -> InlineKeyboardMarkup:
    """To'lov tasdiqlangach obunachiga yuboriladigan tugma — xom URL matn ichida
    ko'rinmasligi uchun (va Telegram'ning avtomatik preview generatsiyasi bilan
    bog'liq imkoniyatlardan qochish uchun ham) havola shu tugma ichida beriladi."""
    label = "🔗 Guruhga kirish" if is_group else "🔗 Kanalga kirish"
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=label, url=invite_link))
    return builder.as_markup()


def payment_reject_confirm_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    """"❌ Bekor qilish" bosilgach: izohsiz o'tkazish tugmasi — yoki admin shunchaki
    matn yozib izoh qoldirishi mumkin (`PaymentReviewStates.waiting_for_reject_comment`)."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="⏭ Izohsiz bekor qilish", callback_data=f"pay_reject_skip:{payment_id}"
        )
    )
    return builder.as_markup()
