from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.middlewares.i18n import get_text
from core.mod_auth import verify_password, change_password, create_mod_session, delete_mod_session
from db.engine import async_session
from moderator.keyboards.inline import mod_menu_kb, mod_back_kb
from services.stats_service import get_moderator_stats
from utils.constants import ModeratorStates

router = Router()


async def is_mod_authenticated(state: FSMContext) -> bool:
    """Check if user is authenticated as moderator in current session."""
    data = await state.get_data()
    return data.get("mod_authenticated", False)


# ── /modlog — password-based moderator login ──


@router.message(Command("modlog"))
async def modlog_start(message: Message, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    if await is_mod_authenticated(state):
        await create_mod_session(message.from_user.id)
        await message.answer(
            _("mod_panel"),
            reply_markup=mod_menu_kb(lang=i18n_lang),
        )
        return

    await message.answer(_("mod_login_prompt"))
    await state.set_state(ModeratorStates.waiting_password)


@router.message(ModeratorStates.waiting_password)
async def modlog_check_password(message: Message, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    try:
        await message.delete()
    except Exception:
        pass

    if verify_password(message.text.strip()):
        await state.set_state(None)
        await state.update_data(mod_authenticated=True)
        await create_mod_session(message.from_user.id)
        await message.answer(
            _("mod_login_success"),
            reply_markup=mod_menu_kb(lang=i18n_lang),
        )
    else:
        await message.answer(_("mod_password_wrong"))


@router.message(Command("cancel"), ModeratorStates.waiting_password)
async def cancel_login(message: Message, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    await state.set_state(None)
    await message.answer(_("mod_login_cancelled"))


# ── Moderator menu (authenticated via callback) ──


@router.callback_query(F.data == "mod_menu")
async def mod_menu(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    if not await is_mod_authenticated(state):
        await callback.answer(_("mod_auth_required"), show_alert=True)
        return

    await callback.message.edit_text(
        _("mod_panel"),
        reply_markup=mod_menu_kb(lang=i18n_lang),
    )
    await callback.answer()


@router.callback_query(F.data == "mod_stats")
async def mod_stats(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    if not await is_mod_authenticated(state):
        await callback.answer(_("mod_auth_required"), show_alert=True)
        return

    async with async_session() as session:
        stats = await get_moderator_stats(session)

    revenue_fmt = f"{stats['total_revenue']:,.0f}".replace(",", " ")
    text = _("mod_platform_stats").format(
        admins=stats['total_admins'],
        paid=stats['paid_admins'],
        bots=stats['total_bots'],
        users=stats['total_end_users'],
        payments=stats['total_payments'],
        revenue=revenue_fmt,
        subs=stats['active_subscriptions'],
    )
    await callback.message.edit_text(text, reply_markup=mod_back_kb(lang=i18n_lang))
    await callback.answer()


# ── Password change ──


@router.callback_query(F.data == "mod_change_password")
async def ask_new_password(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    if not await is_mod_authenticated(state):
        await callback.answer(_("mod_auth_required"), show_alert=True)
        return

    await callback.message.edit_text(
        _("mod_change_password_prompt"),
        reply_markup=mod_back_kb(lang=i18n_lang),
    )
    await state.set_state(ModeratorStates.waiting_new_password)
    await callback.answer()


@router.message(ModeratorStates.waiting_new_password)
async def save_new_password(message: Message, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    new_pwd = message.text.strip()

    try:
        await message.delete()
    except Exception:
        pass

    if len(new_pwd) < 4:
        await message.answer(_("mod_password_short"))
        return

    change_password(new_pwd)
    await state.set_state(None)
    await message.answer(
        _("mod_password_changed"),
        reply_markup=mod_menu_kb(lang=i18n_lang),
    )


# ── Moderator logout ──


@router.callback_query(F.data == "mod_logout")
async def mod_logout(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    await state.update_data(mod_authenticated=False)
    await delete_mod_session(callback.from_user.id)
    await callback.message.edit_text(_("mod_logged_out"))
    await callback.answer()
