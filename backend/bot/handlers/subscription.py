import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.inline import back_kb, main_menu_kb
from config import config
from core.cache import cache_delete
from db.engine import async_session
from services.admin_service import get_admin_by_telegram_id, get_active_subscription
from services.bot_service import get_bots_by_admin
from db.models import AdminSubscription
from utils.constants import PlanName, SubStatus

logger = logging.getLogger(__name__)
router = Router()

# Getolog admin subscription plans (UZS / month)
PLANS = {
    PlanName.STANDARD: {"name": "Standard", "price": 97_000, "months": 1},
    PlanName.PREMIUM:  {"name": "Premium",  "price": 197_000, "months": 1},
}

# Features per plan
PLAN_FEATURES = {
    PlanName.FREE: {
        "ads": True,       # Getolog can send broadcast ads to end-users
        "branding": True,  # "Ushbu bot @getolog_bot tomonidan tayyorlandi"
        "payment_integration": False,  # Only card + screenshot
        "bot_limit": 1,
        "multi_admin_limit": 0,  # No collaborators
    },
    PlanName.STANDARD: {
        "ads": False,
        "branding": True,
        "payment_integration": False,
        "bot_limit": 2,
        "multi_admin_limit": 2,
    },
    PlanName.PREMIUM: {
        "ads": False,
        "branding": False,
        "payment_integration": True,  # Click + Payme
        "bot_limit": 5,
        "multi_admin_limit": 5,
    },
}

GETOLOG_CARD = config.getolog_card


class SubPayStates(StatesGroup):
    waiting_screenshot = State()


@router.callback_query(F.data == "my_subscription")
async def show_subscription(callback: CallbackQuery):
    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, callback.from_user.id)
        sub = await get_active_subscription(session, admin.id)
        bots = await get_bots_by_admin(session, admin.id)

    bot_count = len(bots)
    plan = sub.plan if sub else PlanName.FREE
    features = PLAN_FEATURES.get(plan, PLAN_FEATURES[PlanName.FREE])

    if plan == PlanName.FREE:
        text = (
            "📦 <b>Joriy tarif: Bepul</b>\n\n"
            f"🤖 Botlar: {bot_count}/{features['bot_limit']}\n"
            f"👥 Multi-admin: ❌\n"
            "🔹 Getolog reklama yuborishi mumkin\n"
            "🔹 Getolog brending ko'rsatiladi\n"
            "🔹 To'lov: faqat karta + screenshot\n\n"
            "Tarifni oshirish uchun tanlang:"
        )
        buttons = []
        for plan_id, plan_info in PLANS.items():
            price_fmt = f"{plan_info['price']:,}".replace(",", " ")
            feat = PLAN_FEATURES[plan_id]
            desc = []
            if not feat["ads"]:
                desc.append("reklama yo'q")
            if not feat["branding"]:
                desc.append("brending yo'q")
            if feat["payment_integration"]:
                desc.append("Click/Payme")
            feat_text = " · ".join(desc)
            buttons.append([
                InlineKeyboardButton(
                    text=f"{plan_info['name']} — {price_fmt} UZS/oy",
                    callback_data=f"buy_plan_{plan_id}",
                )
            ])
        buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_menu")])
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    elif plan == PlanName.STANDARD:
        expires = sub.expires_at.strftime("%d.%m.%Y") if sub.expires_at else "—"
        text = (
            "📦 <b>Joriy tarif: Standard</b>\n\n"
            f"📅 Tugash sanasi: {expires}\n"
            "✅ Holati: Aktiv\n\n"
            f"🤖 Botlar: {bot_count}/{features['bot_limit']}\n"
            f"👥 Multi-admin: ✅ ({features['multi_admin_limit']} tagacha)\n"
            "🔹 Reklama yuborilmaydi\n"
            "🔹 Brending ko'rsatiladi\n"
            "🔹 To'lov: faqat karta + screenshot\n\n"
            "Premium ga o'tish uchun:"
        )
        premium = PLANS[PlanName.PREMIUM]
        price_fmt = f"{premium['price']:,}".replace(",", " ")
        buttons = [
            [InlineKeyboardButton(
                text=f"⬆️ Premium — {price_fmt} UZS/oy",
                callback_data="buy_plan_premium",
            )],
            [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_menu")],
        ]
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    elif plan == PlanName.PREMIUM:
        expires = sub.expires_at.strftime("%d.%m.%Y") if sub.expires_at else "—"
        text = (
            "📦 <b>Joriy tarif: Premium</b>\n\n"
            f"📅 Tugash sanasi: {expires}\n"
            "✅ Holati: Aktiv\n\n"
            f"🤖 Botlar: {bot_count}/{features['bot_limit']}\n"
            f"👥 Multi-admin: ✅ ({features['multi_admin_limit']} tagacha)\n"
            "🔹 Reklama yuborilmaydi\n"
            "🔹 Brending ko'rsatilmaydi\n"
            "🔹 Click / Payme to'lov integratsiyasi faol\n"
        )
        kb = back_kb()

    else:
        # Backward compat: old plans (1month, 6month, 12month)
        expires = sub.expires_at.strftime("%d.%m.%Y") if sub.expires_at else "—"
        text = (
            f"📦 <b>Joriy tarif: {sub.plan} (eski)</b>\n\n"
            f"📅 Tugash sanasi: {expires}\n"
            "✅ Holati: Aktiv\n\n"
            "Muddati tugagandan keyin yangi tariflardan birini tanlashingiz mumkin."
        )
        kb = back_kb()

    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("buy_plan_"))
async def buy_plan(callback: CallbackQuery, state: FSMContext):
    plan_id = callback.data.replace("buy_plan_", "")
    plan = PLANS.get(plan_id)
    if not plan:
        await callback.answer("❌ Tarif topilmadi.")
        return

    price_fmt = f"{plan['price']:,}".replace(",", " ")

    await state.update_data(plan_id=plan_id)

    features = PLAN_FEATURES[plan_id]
    feat_lines = []
    if not features["ads"]:
        feat_lines.append("✅ Reklama yuborilmaydi")
    if not features["branding"]:
        feat_lines.append("✅ Brending ko'rsatilmaydi")
    if features["payment_integration"]:
        feat_lines.append("✅ Click / Payme integratsiyasi")
    feat_text = "\n".join(feat_lines)

    await callback.message.edit_text(
        f"💳 <b>{plan['name']} obuna — {price_fmt} UZS/oy</b>\n\n"
        f"{feat_text}\n\n"
        f"Quyidagi karta raqamiga to'lov qiling:\n\n"
        f"<code>{GETOLOG_CARD}</code>\n\n"
        f"✅ To'lov qilgandan keyin <b>chek rasmini</b> (screenshot) yuboring.",
        reply_markup=back_kb(),
    )
    await state.set_state(SubPayStates.waiting_screenshot)
    await callback.answer()


@router.message(SubPayStates.waiting_screenshot, F.photo)
async def process_sub_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    plan_id = data["plan_id"]
    plan = PLANS[plan_id]
    photo = message.photo[-1]

    price_fmt = f"{plan['price']:,}".replace(",", " ")

    await message.answer(
        "✅ To'lov ma'lumotlari qabul qilindi!\n\n"
        "⏳ Moderator tasdiqlashini kuting. Tasdiqlanganidan keyin obuna faollashadi.",
        reply_markup=main_menu_kb(),
    )

    # Notify all moderators
    for mod_id in config.moderator_ids:
        try:
            await message.bot.send_photo(
                mod_id,
                photo=photo.file_id,
                caption=(
                    f"💎 <b>Getolog obuna to'lovi!</b>\n\n"
                    f"👤 @{message.from_user.username or '—'} ({message.from_user.full_name})\n"
                    f"📦 Tarif: {plan['name']}\n"
                    f"💰 {price_fmt} UZS/oy\n"
                    f"🆔 Admin ID: {message.from_user.id}"
                ),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Tasdiqlash",
                            callback_data=f"mod_sub_approve_{message.from_user.id}_{plan_id}",
                        ),
                        InlineKeyboardButton(
                            text="❌ Rad etish",
                            callback_data=f"mod_sub_reject_{message.from_user.id}",
                        ),
                    ]
                ]),
            )
        except Exception as e:
            logger.error(f"Failed to notify moderator {mod_id}: {e}")

    await state.clear()


@router.message(SubPayStates.waiting_screenshot)
async def wrong_sub_screenshot(message: Message):
    await message.answer(
        "❌ Iltimos, <b>rasm</b> (screenshot) yuboring.",
        reply_markup=back_kb(),
    )


@router.callback_query(F.data.startswith("mod_sub_approve_"))
async def mod_approve_subscription(callback: CallbackQuery):
    if callback.from_user.id not in config.moderator_ids:
        await callback.answer("⛔ Ruxsat yo'q.")
        return

    parts = callback.data.split("_")
    # mod_sub_approve_{telegram_id}_{plan_id}
    admin_tg_id = int(parts[3])
    plan_id = parts[4]
    plan = PLANS.get(plan_id)

    if not plan:
        await callback.answer("❌ Tarif topilmadi.")
        return

    from datetime import datetime, timedelta, timezone

    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, admin_tg_id)
        if not admin:
            await callback.answer("❌ Admin topilmadi.")
            return

        # Expire old active subscription
        old_sub = await get_active_subscription(session, admin.id)
        if old_sub:
            old_sub.status = SubStatus.EXPIRED

        # Create new subscription (1 month)
        now = datetime.now(timezone.utc)
        new_sub = AdminSubscription(
            user_admin_id=admin.id,
            plan=plan_id,
            started_at=now,
            expires_at=now + timedelta(days=30),
            amount_paid=plan["price"],
            status=SubStatus.ACTIVE,
        )
        session.add(new_sub)
        await session.commit()

        # Invalidate premium cache for all admin's bots
        bots = await get_bots_by_admin(session, admin.id)
        for b in bots:
            await cache_delete(f"premium:{b.bot_username}")

    # Build notification based on plan
    features = PLAN_FEATURES[plan_id]
    feat_lines = []
    if not features["ads"]:
        feat_lines.append("✅ Reklama yuborilmaydi")
    if features["branding"]:
        feat_lines.append("ℹ️ Getolog brending saqlanadi")
    else:
        feat_lines.append("✅ Brending ko'rsatilmaydi")
    if features["payment_integration"]:
        feat_lines.append("✅ Click / Payme integratsiyasi faol")
    feat_text = "\n".join(feat_lines)

    try:
        await callback.bot.send_message(
            admin_tg_id,
            f"✅ <b>Obuna faollashtirildi!</b>\n\n"
            f"📦 Tarif: {plan['name']}\n"
            f"📅 Muddat: 1 oy\n\n"
            f"{feat_text}",
            reply_markup=main_menu_kb(),
        )
    except Exception:
        pass

    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n✅ <b>TASDIQLANDI</b>",
    )
    await callback.answer("✅ Obuna faollashtirildi!")


@router.callback_query(F.data.startswith("mod_sub_reject_"))
async def mod_reject_subscription(callback: CallbackQuery):
    if callback.from_user.id not in config.moderator_ids:
        await callback.answer("⛔ Ruxsat yo'q.")
        return

    admin_tg_id = int(callback.data.split("_")[3])

    try:
        await callback.bot.send_message(
            admin_tg_id,
            "❌ <b>To'lov rad etildi.</b>\n\n"
            "To'lov tasdiqlana olmadi. Iltimos, to'g'ri summani o'tkazing va qayta urinib ko'ring.",
            reply_markup=main_menu_kb(),
        )
    except Exception:
        pass

    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n❌ <b>RAD ETILDI</b>",
    )
    await callback.answer("❌ Rad etildi.")
