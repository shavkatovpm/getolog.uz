import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.inline import back_kb, main_menu_kb
from bot.middlewares.i18n import get_text
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
async def show_subscription(callback: CallbackQuery, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, callback.from_user.id)
        sub = await get_active_subscription(session, admin.id)
        bots = await get_bots_by_admin(session, admin.id)

    bot_count = len(bots)
    plan = sub.plan if sub else PlanName.FREE
    features = PLAN_FEATURES.get(plan, PLAN_FEATURES[PlanName.FREE])

    if plan == PlanName.FREE:
        text = _("plan_free").format(bots=bot_count, limit=features['bot_limit'])
        buttons = []
        for plan_id, plan_info in PLANS.items():
            price_fmt = f"{plan_info['price']:,}".replace(",", " ")
            buttons.append([
                InlineKeyboardButton(
                    text=f"{plan_info['name']} — {price_fmt} UZS/oy",
                    callback_data=f"buy_plan_{plan_id}",
                )
            ])
        buttons.append([InlineKeyboardButton(
            text=_('btn_back'),
            callback_data="back_menu",
        )])
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    elif plan == PlanName.STANDARD:
        expires = sub.expires_at.strftime("%d.%m.%Y") if sub.expires_at else "\u2014"
        text = _("plan_standard").format(
            expires=expires,
            bots=bot_count,
            limit=features['bot_limit'],
            collab_limit=features['multi_admin_limit'],
        )
        premium = PLANS[PlanName.PREMIUM]
        price_fmt = f"{premium['price']:,}".replace(",", " ")
        buttons = [
            [InlineKeyboardButton(
                text=f"Premium — {price_fmt} UZS/oy",
                callback_data="buy_plan_premium",
            )],
            [InlineKeyboardButton(
                text=_('btn_back'),
                callback_data="back_menu",
            )],
        ]
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    elif plan == PlanName.PREMIUM:
        expires = sub.expires_at.strftime("%d.%m.%Y") if sub.expires_at else "\u2014"
        text = _("plan_premium").format(
            expires=expires,
            bots=bot_count,
            limit=features['bot_limit'],
            collab_limit=features['multi_admin_limit'],
        )
        kb = back_kb(lang=i18n_lang)

    else:
        # Backward compat: old plans (1month, 6month, 12month)
        expires = sub.expires_at.strftime("%d.%m.%Y") if sub.expires_at else "\u2014"
        text = _("plan_old").format(plan=sub.plan, expires=expires)
        kb = back_kb(lang=i18n_lang)

    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("buy_plan_"))
async def buy_plan(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    plan_id = callback.data.replace("buy_plan_", "")
    plan = PLANS.get(plan_id)
    if not plan:
        await callback.answer(_("plan_not_found"))
        return

    price_fmt = f"{plan['price']:,}".replace(",", " ")

    await state.update_data(plan_id=plan_id)

    features = PLAN_FEATURES[plan_id]
    feat_lines = []
    if not features["ads"]:
        feat_lines.append(_("feat_no_ads"))
    if not features["branding"]:
        feat_lines.append(_("feat_no_branding"))
    if features["payment_integration"]:
        feat_lines.append(_("feat_click_payme"))
    feat_text = "\n".join(feat_lines)

    await callback.message.edit_text(
        _("buy_plan").format(
            name=plan['name'],
            price=price_fmt,
            features=feat_text,
            card=GETOLOG_CARD,
        ),
        reply_markup=back_kb(lang=i18n_lang),
    )
    await state.set_state(SubPayStates.waiting_screenshot)
    await callback.answer()


@router.message(SubPayStates.waiting_screenshot, F.photo)
async def process_sub_screenshot(message: Message, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    data = await state.get_data()
    plan_id = data["plan_id"]
    plan = PLANS[plan_id]
    photo = message.photo[-1]

    price_fmt = f"{plan['price']:,}".replace(",", " ")

    await message.answer(
        _("sub_payment_received"),
        reply_markup=main_menu_kb(lang=i18n_lang),
    )

    # Notify all moderators
    for mod_id in config.moderator_ids:
        try:
            await message.bot.send_photo(
                mod_id,
                photo=photo.file_id,
                caption=get_text("sub_mod_notification", "uz").format(
                    username=message.from_user.username or "\u2014",
                    name=message.from_user.full_name,
                    plan=plan['name'],
                    price=price_fmt,
                    admin_id=message.from_user.id,
                ),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=get_text('btn_approve', 'uz'),
                            callback_data=f"mod_sub_approve_{message.from_user.id}_{plan_id}",
                        ),
                        InlineKeyboardButton(
                            text=get_text('btn_reject', 'uz'),
                            callback_data=f"mod_sub_reject_{message.from_user.id}",
                        ),
                    ]
                ]),
            )
        except Exception as e:
            logger.error(f"Failed to notify moderator {mod_id}: {e}")

    await state.clear()


@router.message(SubPayStates.waiting_screenshot)
async def wrong_sub_screenshot(message: Message, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    await message.answer(
        _("sub_wrong_screenshot"),
        reply_markup=back_kb(lang=i18n_lang),
    )


@router.callback_query(F.data.startswith("mod_sub_approve_"))
async def mod_approve_subscription(callback: CallbackQuery, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    if callback.from_user.id not in config.moderator_ids:
        await callback.answer(_("no_permission"))
        return

    parts = callback.data.split("_")
    # mod_sub_approve_{telegram_id}_{plan_id}
    admin_tg_id = int(parts[3])
    plan_id = parts[4]
    plan = PLANS.get(plan_id)

    if not plan:
        await callback.answer(_("plan_not_found"))
        return

    from datetime import datetime, timedelta, timezone

    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, admin_tg_id)
        if not admin:
            await callback.answer(_("admin_not_found"))
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

        # Get admin's language for the notification sent to them
        admin_lang = admin.language or "uz"

    # Build notification using admin's language
    _admin = lambda key: get_text(key, admin_lang)

    features = PLAN_FEATURES[plan_id]
    feat_lines = []
    if not features["ads"]:
        feat_lines.append(_admin("feat_no_ads"))
    if features["branding"]:
        feat_lines.append(_admin("feat_branding_kept"))
    else:
        feat_lines.append(_admin("feat_no_branding"))
    if features["payment_integration"]:
        feat_lines.append(_admin("feat_click_payme"))
    feat_text = "\n".join(feat_lines)

    try:
        await callback.bot.send_message(
            admin_tg_id,
            _admin("sub_activated").format(plan=plan['name'], features=feat_text),
            reply_markup=main_menu_kb(lang=admin_lang),
        )
    except Exception:
        pass

    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n" + _("confirmed"),
    )
    await callback.answer(_("sub_activated_cb"))


@router.callback_query(F.data.startswith("mod_sub_reject_"))
async def mod_reject_subscription(callback: CallbackQuery, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    if callback.from_user.id not in config.moderator_ids:
        await callback.answer(_("no_permission"))
        return

    admin_tg_id = int(callback.data.split("_")[3])

    # Look up admin's language for the rejection message sent to them
    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, admin_tg_id)
        admin_lang = (admin.language if admin else None) or "uz"

    _admin = lambda key: get_text(key, admin_lang)

    try:
        await callback.bot.send_message(
            admin_tg_id,
            _admin("sub_rejected"),
            reply_markup=main_menu_kb(lang=admin_lang),
        )
    except Exception:
        pass

    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n" + _("rejected_label"),
    )
    await callback.answer(_("sub_rejected_cb"))
