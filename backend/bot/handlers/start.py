import logging

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.inline import main_menu_kb, bot_dashboard_kb, back_kb, language_select_kb
from bot.middlewares.i18n import get_text
from db.engine import async_session
from services.admin_service import get_or_create_admin, get_admin_by_telegram_id
from services.bot_service import get_bots_by_admin, get_bot_by_id, get_collab_bots
from services.stats_service import get_admin_stats
from config import config

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    async with async_session() as session:
        admin, is_new = await get_or_create_admin(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            language="uz",
        )

    if admin.banned:
        await message.answer(_("admin_banned"))
        return

    if is_new:
        # Notify moderators
        for mod_id in config.moderator_ids:
            try:
                await message.bot.send_message(
                    mod_id,
                    _("new_admin_notification").format(
                        name=message.from_user.full_name,
                        username=message.from_user.username or "—",
                    ),
                )
            except Exception:
                pass

        # Show language selection for new users
        await message.answer(
            _("choose_language"),
            reply_markup=language_select_kb(),
        )
        return

    # Existing user — use their saved language
    lang = admin.language or "uz"
    _ = lambda key: get_text(key, lang)

    await message.answer(
        _("admin_welcome").format(name=message.from_user.first_name),
        reply_markup=main_menu_kb(lang=lang),
    )


@router.callback_query(F.data.startswith("admin_lang_"))
async def set_admin_language(callback: CallbackQuery):
    lang = callback.data.split("_")[2]  # uz, ru, en
    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, callback.from_user.id)
        if admin:
            admin.language = lang
            await session.commit()

    _ = lambda key: get_text(key, lang)
    await callback.message.edit_text(_("language_set"))
    await callback.message.answer(
        _("admin_welcome").format(name=callback.from_user.first_name),
        reply_markup=main_menu_kb(lang=lang),
    )
    await callback.answer()


@router.callback_query(F.data == "back_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    await state.clear()
    await callback.message.edit_text(
        _("back_to_menu").format(name=callback.from_user.first_name),
        reply_markup=main_menu_kb(lang=i18n_lang),
    )
    await callback.answer()


# ══════════════════════
# ── MENING BOTLARIM ──
# ══════════════════════

@router.callback_query(F.data == "my_bots")
async def my_bots(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, callback.from_user.id)
        owned = await get_bots_by_admin(session, admin.id)
        collab = await get_collab_bots(session, callback.from_user.id)

    # Merge and deduplicate
    all_bots = {b.id: b for b in owned + collab}
    bots = list(all_bots.values())

    if not bots:
        await callback.message.edit_text(
            _("no_bots"),
            reply_markup=main_menu_kb(lang=i18n_lang),
        )
        await callback.answer()
        return

    buttons = [
        [InlineKeyboardButton(
            text=f"@{b.bot_username}",
            callback_data=f"select_bot_{b.id}",
        )]
        for b in bots
    ]
    buttons.append([InlineKeyboardButton(
        text=_('btn_back'),
        callback_data="back_menu",
    )])

    await callback.message.edit_text(
        _("select_bot"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


# ══════════════════════
# ── BOT DASHBOARD ──
# ══════════════════════

@router.callback_query(F.data.startswith("select_bot_"))
async def select_bot(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    bot_id = int(callback.data.split("_")[2])
    await state.update_data(selected_bot_id=bot_id)
    await _show_bot_dashboard(callback, bot_id, i18n_lang=i18n_lang)


async def _show_bot_dashboard(callback: CallbackQuery, bot_id: int, i18n_lang: str = "uz"):
    """Show bot dashboard with quick stats."""
    _ = lambda key: get_text(key, i18n_lang)

    async with async_session() as session:
        user_bot = await get_bot_by_id(session, bot_id)
        if not user_bot:
            await callback.message.edit_text(
                _("bot_not_found"),
                reply_markup=main_menu_kb(lang=i18n_lang),
            )
            await callback.answer()
            return

        stats = await get_admin_stats(session, bot_id)

    def fmt(n: float) -> str:
        return f"{n:,.0f}".replace(",", " ")

    await callback.message.edit_text(
        _("bot_dashboard").format(
            username=user_bot.bot_username,
            users=stats["total_users"],
            pending=stats["pending_payments"],
            today=fmt(stats["today_revenue"]),
        ),
        reply_markup=bot_dashboard_kb(bot_id, lang=i18n_lang),
    )
    await callback.answer()


@router.callback_query(F.data == "back_bot_dashboard")
async def back_bot_dashboard(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    data = await state.get_data()
    bot_id = data.get("selected_bot_id")
    current_state = await state.get_state()
    logger.info(f"back_bot_dashboard: bot_id={bot_id}, state={current_state}, data_keys={list(data.keys())}")

    # Clear FSM state (e.g. waiting_welcome) but keep data
    await state.set_state(None)

    if not bot_id:
        # Fallback: try to find user's bot directly
        async with async_session() as session:
            admin = await get_admin_by_telegram_id(session, callback.from_user.id)
            if admin:
                owned = await get_bots_by_admin(session, admin.id)
                collab = await get_collab_bots(session, callback.from_user.id)
                all_bots = {b.id: b for b in owned + collab}
                bots = list(all_bots.values())
                logger.info(f"back_bot_dashboard fallback: found {len(bots)} bots")
                if len(bots) == 1:
                    bot_id = bots[0].id
                    await state.update_data(selected_bot_id=bot_id)
                elif len(bots) > 1:
                    bot_id = bots[0].id
                    await state.update_data(selected_bot_id=bot_id)

    if not bot_id:
        logger.info("back_bot_dashboard: no bot found, going to my_bots")
        await my_bots(callback, state, i18n_lang=i18n_lang)
        return
    logger.info(f"back_bot_dashboard: showing dashboard for bot_id={bot_id}")
    await _show_bot_dashboard(callback, bot_id, i18n_lang=i18n_lang)


# ══════════════════════════════
# ── BOT-SPECIFIC ACTIONS ──
# ══════════════════════════════

@router.callback_query(F.data.startswith("bot_stats_"))
async def bot_stats(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    bot_id = int(callback.data.split("_")[2])
    await state.update_data(selected_bot_id=bot_id)
    from bot.handlers.stats import show_stats
    await show_stats(callback, state, i18n_lang=i18n_lang)


@router.callback_query(F.data.startswith("bot_payments_"))
async def bot_payments(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    bot_id = int(callback.data.split("_")[2])
    await state.update_data(selected_bot_id=bot_id)
    from bot.handlers.payments import show_payments
    await show_payments(callback, state, i18n_lang=i18n_lang)


@router.callback_query(F.data.startswith("bot_users_"))
async def bot_users(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    bot_id = int(callback.data.split("_")[2])
    await state.update_data(selected_bot_id=bot_id)
    from bot.handlers.manage_users import show_users
    await show_users(callback, state, i18n_lang=i18n_lang)


@router.callback_query(F.data.startswith("bot_settings_"))
async def bot_settings(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    bot_id = int(callback.data.split("_")[2])
    await state.update_data(selected_bot_id=bot_id)
    from bot.handlers.settings import show_settings
    await show_settings(callback, state, i18n_lang=i18n_lang)


# ══════════════════════
# ── PICK (LEGACY) ──
# ══════════════════════

@router.callback_query(F.data.startswith("pick_"))
async def pick_bot_for_action(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    """Handle bot selection when admin has multiple bots (legacy require_bot flow)."""
    parts = callback.data.split("_")
    # Format: pick_{action}_{bot_id}
    action = parts[1]
    bot_id = int(parts[2])
    await state.update_data(selected_bot_id=bot_id)

    if action == "settings":
        from bot.handlers.settings import show_settings
        await show_settings(callback, state, i18n_lang=i18n_lang)
    elif action == "stats":
        from bot.handlers.stats import show_stats
        await show_stats(callback, state, i18n_lang=i18n_lang)
    elif action == "users":
        from bot.handlers.manage_users import show_users
        await show_users(callback, state, i18n_lang=i18n_lang)
    elif action == "payments":
        from bot.handlers.payments import show_payments
        await show_payments(callback, state, i18n_lang=i18n_lang)


# ══════════════════════
# ── HELP ──
# ══════════════════════

@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    await callback.message.edit_text(
        _("help_text"),
        reply_markup=back_kb(lang=i18n_lang),
    )
    await callback.answer()
