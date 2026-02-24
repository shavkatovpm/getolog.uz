from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.helpers import require_bot, get_current_bot
from bot.keyboards.inline import settings_kb, back_kb, back_bot_kb, main_menu_kb
from bot.handlers.subscription import PLAN_FEATURES
from bot.middlewares.i18n import get_text
from core.bot_manager import BotManager
from core.cache import cache_delete
from core.encryption import decrypt_card
from db.engine import async_session
from db.models import BotCollaborator
from services.admin_service import get_admin_by_telegram_id, get_active_subscription
from services.bot_service import update_bot_settings, deactivate_bot
from utils.constants import SettingsStates, PlanName
from utils.validators import validate_card
from sqlalchemy import select, and_

router = Router()


@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    user_bot, admin = await require_bot(callback, state, "settings", i18n_lang=i18n_lang)
    if not user_bot:
        return

    text = _("settings_header").format(
        username=user_bot.bot_username,
        card=decrypt_card(user_bot.card_number) if user_bot.card_number else '—',
        welcome=(user_bot.welcome_message or '—')[:50],
    )
    await callback.message.edit_text(text, reply_markup=settings_kb(lang=i18n_lang))
    await callback.answer()


@router.callback_query(F.data == "set_welcome")
async def ask_welcome(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    await callback.message.edit_text(
        _("ask_welcome_message"),
        reply_markup=back_bot_kb(lang=i18n_lang),
    )
    await state.set_state(SettingsStates.waiting_welcome)
    await callback.answer()


@router.message(SettingsStates.waiting_welcome)
async def save_welcome(message: Message, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, message.from_user.id)
        user_bot = await get_current_bot(session, admin.id, state)
        await update_bot_settings(session, user_bot.id, welcome_message=message.text)
        await cache_delete(f"settings:{user_bot.id}")

    await message.answer(
        _("welcome_saved"),
        reply_markup=settings_kb(lang=i18n_lang),
    )
    await state.set_state(None)


@router.callback_query(F.data == "set_card")
async def ask_card(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    await callback.message.edit_text(
        _("ask_card_number"),
        reply_markup=back_bot_kb(lang=i18n_lang),
    )
    await state.set_state(SettingsStates.waiting_card)
    await callback.answer()


@router.message(SettingsStates.waiting_card)
async def save_card(message: Message, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    formatted = validate_card(message.text)
    if not formatted:
        await message.answer(
            _("card_invalid_16"),
            reply_markup=back_bot_kb(lang=i18n_lang),
        )
        return

    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, message.from_user.id)
        user_bot = await get_current_bot(session, admin.id, state)
        await update_bot_settings(session, user_bot.id, card_number=formatted)
        await cache_delete(f"settings:{user_bot.id}")

    await message.answer(
        _("card_saved").format(card=formatted),
        reply_markup=settings_kb(lang=i18n_lang),
    )
    await state.set_state(None)


@router.callback_query(F.data == "set_price")
async def ask_price(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    await callback.message.edit_text(
        _("ask_new_price"),
        reply_markup=back_bot_kb(lang=i18n_lang),
    )
    await state.set_state(SettingsStates.waiting_price)
    await callback.answer()


@router.message(SettingsStates.waiting_price)
async def save_price(message: Message, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    try:
        price = int(message.text.strip().replace(" ", ""))
        if price < 1000:
            raise ValueError
    except ValueError:
        await message.answer(
            _("price_min_error"),
            reply_markup=back_bot_kb(lang=i18n_lang),
        )
        return

    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, message.from_user.id)
        user_bot = await get_current_bot(session, admin.id, state)
        from services.bot_service import get_channels_by_bot
        channels = await get_channels_by_bot(session, user_bot.id)
        if channels:
            channels[0].price = price
            await session.commit()
        await cache_delete(f"settings:{user_bot.id}")

    price_formatted = f"{price:,}".replace(",", " ")
    await message.answer(
        _("price_saved").format(price=price_formatted),
        reply_markup=settings_kb(lang=i18n_lang),
    )
    await state.set_state(None)


# --- Collaborator (Hamkor) Management ---


@router.callback_query(F.data == "manage_collabs")
async def manage_collabs(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, callback.from_user.id)
        sub = await get_active_subscription(session, admin.id)
        user_bot = await get_current_bot(session, admin.id, state)

    plan = sub.plan if sub else PlanName.FREE
    features = PLAN_FEATURES.get(plan, PLAN_FEATURES[PlanName.FREE])

    if features["multi_admin_limit"] == 0:
        await callback.message.edit_text(
            _("collabs_no_access"),
            reply_markup=settings_kb(lang=i18n_lang),
        )
        await callback.answer()
        return

    if not user_bot:
        await callback.message.edit_text(
            _("create_bot_first"),
            reply_markup=main_menu_kb(lang=i18n_lang),
        )
        await callback.answer()
        return

    collabs = user_bot.collaborators
    limit = features["multi_admin_limit"]

    text = _("collabs_header").format(count=len(collabs), limit=limit)
    if collabs:
        for c in collabs:
            text += f"• @{c.username or c.telegram_id}\n"
    else:
        text += _("no_collabs_yet")

    buttons = []
    if len(collabs) < limit:
        buttons.append([InlineKeyboardButton(
            text=_('btn_add_collab'),
            callback_data="add_collab",
        )])
    for c in collabs:
        buttons.append([InlineKeyboardButton(
            text=f"@{c.username or c.telegram_id}",
            callback_data=f"remove_collab_{c.id}",
        )])
    buttons.append([
        InlineKeyboardButton(text=_('btn_back'), callback_data="settings"),
        InlineKeyboardButton(text=_('btn_main_menu'), callback_data="back_menu"),
    ])

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(F.data == "add_collab")
async def add_collab(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    await callback.message.edit_text(
        _("add_collab_prompt"),
        reply_markup=back_bot_kb(lang=i18n_lang),
    )
    await state.set_state(SettingsStates.waiting_collab_id)
    await callback.answer()


@router.message(SettingsStates.waiting_collab_id)
async def save_collab(message: Message, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    try:
        collab_tg_id = int(message.text.strip())
    except ValueError:
        await message.answer(
            _("collab_id_invalid"),
            reply_markup=back_bot_kb(lang=i18n_lang),
        )
        return

    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, message.from_user.id)
        sub = await get_active_subscription(session, admin.id)
        user_bot = await get_current_bot(session, admin.id, state)

        if not user_bot:
            await message.answer(_("bot_not_found"), reply_markup=settings_kb(lang=i18n_lang))
            await state.set_state(None)
            return

        plan = sub.plan if sub else "free"
        features = PLAN_FEATURES.get(plan, PLAN_FEATURES["free"])
        limit = features["multi_admin_limit"]

        if len(user_bot.collaborators) >= limit:
            await message.answer(
                _("collab_limit_reached").format(limit=limit),
                reply_markup=settings_kb(lang=i18n_lang),
            )
            await state.set_state(None)
            return

        existing = await session.execute(
            select(BotCollaborator).where(
                and_(
                    BotCollaborator.user_bot_id == user_bot.id,
                    BotCollaborator.telegram_id == collab_tg_id,
                )
            )
        )
        if existing.scalar_one_or_none():
            await message.answer(
                _("collab_already_exists"),
                reply_markup=settings_kb(lang=i18n_lang),
            )
            await state.set_state(None)
            return

        if collab_tg_id == message.from_user.id:
            await message.answer(
                _("collab_self_error"),
                reply_markup=settings_kb(lang=i18n_lang),
            )
            await state.set_state(None)
            return

        username = None
        try:
            chat = await message.bot.get_chat(collab_tg_id)
            username = chat.username
        except Exception:
            pass

        collab = BotCollaborator(
            user_bot_id=user_bot.id,
            telegram_id=collab_tg_id,
            username=username,
        )
        session.add(collab)
        await session.commit()

    await message.answer(
        _("collab_added").format(username=username or collab_tg_id),
        reply_markup=settings_kb(lang=i18n_lang),
    )
    await state.set_state(None)


@router.callback_query(F.data.startswith("remove_collab_"))
async def remove_collab(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    collab_id = int(callback.data.replace("remove_collab_", ""))

    async with async_session() as session:
        result = await session.execute(
            select(BotCollaborator).where(BotCollaborator.id == collab_id)
        )
        collab = result.scalar_one_or_none()
        if collab:
            username = collab.username or collab.telegram_id
            await session.delete(collab)
            await session.commit()
            await callback.answer(_("collab_removed").format(username=username))
        else:
            await callback.answer(_("collab_not_found"))

    await manage_collabs(callback, state, i18n_lang=i18n_lang)


# --- Bot Deactivation ---


@router.callback_query(F.data == "deactivate_bot")
async def ask_deactivate_bot(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, callback.from_user.id)
        user_bot = await get_current_bot(session, admin.id, state)

    if not user_bot:
        await callback.message.edit_text(
            _("bot_not_found"),
            reply_markup=main_menu_kb(lang=i18n_lang),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        _("deactivate_confirm").format(username=user_bot.bot_username),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_('btn_delete'),
                    callback_data=f"do_deactivate_{user_bot.id}",
                ),
                InlineKeyboardButton(
                    text=_('btn_cancel'),
                    callback_data="settings",
                ),
            ],
        ]),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("do_deactivate_"))
async def confirm_deactivate_bot(
    callback: CallbackQuery, state: FSMContext, bot_manager: BotManager, i18n_lang: str = "uz"
):
    _ = lambda key: get_text(key, i18n_lang)
    bot_id = int(callback.data.split("_")[2])

    async with async_session() as session:
        success = await deactivate_bot(session, bot_id)

    if success:
        await bot_manager.stop_bot(bot_id)
        await state.update_data(selected_bot_id=None)
        await callback.message.edit_text(
            _("deactivate_success"),
            reply_markup=main_menu_kb(lang=i18n_lang),
        )
    else:
        await callback.message.edit_text(
            _("bot_not_found"),
            reply_markup=main_menu_kb(lang=i18n_lang),
        )
    await callback.answer()
