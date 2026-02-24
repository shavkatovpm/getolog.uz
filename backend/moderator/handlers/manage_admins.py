from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.middlewares.i18n import get_text
from db.engine import async_session
from moderator.handlers.dashboard import is_mod_authenticated
from moderator.keyboards.inline import mod_back_kb
from services.admin_service import get_all_admins, ban_admin, unban_admin
from db.models import UserAdmin

router = Router()


@router.callback_query(F.data == "mod_admins")
async def show_admins(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    if not await is_mod_authenticated(state):
        await callback.answer(_("mod_auth_required"), show_alert=True)
        return

    async with async_session() as session:
        admins = await get_all_admins(session)

    if not admins:
        await callback.message.edit_text(
            _("mod_no_admins"),
            reply_markup=mod_back_kb(lang=i18n_lang),
        )
        await callback.answer()
        return

    text = _("mod_admins_header").format(count=len(admins))
    buttons = []
    for a in admins[:20]:
        status = "🚫" if a.banned else "✅"
        text += f"{status} @{a.username or '—'} — {a.full_name or '—'}\n"
        action = "Unban" if a.banned else "Ban"
        buttons.append([
            InlineKeyboardButton(
                text=f"{action} @{a.username or a.telegram_id}",
                callback_data=f"mod_toggle_{a.id}",
            )
        ])

    buttons.append([InlineKeyboardButton(
        text=_('btn_back'), callback_data="mod_menu"
    )])
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("mod_toggle_"))
async def toggle_admin_ban(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    if not await is_mod_authenticated(state):
        await callback.answer(_("mod_auth_required"), show_alert=True)
        return

    admin_id = int(callback.data.split("_")[2])
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(UserAdmin).where(UserAdmin.id == admin_id)
        )
        admin = result.scalar_one_or_none()
        if admin:
            if admin.banned:
                await unban_admin(session, admin_id)
                await callback.answer(_("mod_admin_unbanned"))
            else:
                await ban_admin(session, admin_id)
                await callback.answer(_("mod_admin_banned"))

    await show_admins(callback, state, i18n_lang=i18n_lang)
