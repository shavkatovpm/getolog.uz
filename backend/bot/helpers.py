from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline import main_menu_kb
from bot.middlewares.i18n import get_text
from db.engine import async_session
from services.admin_service import get_admin_by_telegram_id
from services.bot_service import get_bots_by_admin, get_bot_by_id, get_bot_by_admin, get_collab_bots


async def require_bot(
    callback: CallbackQuery,
    state: FSMContext,
    action: str,
    i18n_lang: str = "uz",
):
    """Ensure admin has a bot selected.

    Returns (user_bot, admin) or (None, None) if a selection screen was shown.
    Includes bots the user collaborates on.
    """
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
            _("no_bot_yet"),
            reply_markup=main_menu_kb(lang=i18n_lang),
        )
        await callback.answer()
        return None, None

    if len(bots) == 1:
        await state.update_data(selected_bot_id=bots[0].id)
        return bots[0], admin

    # Multiple bots — check state for previous selection
    data = await state.get_data()
    selected_id = data.get("selected_bot_id")
    if selected_id:
        for b in bots:
            if b.id == selected_id:
                return b, admin

    # Show bot selection
    buttons = [
        [InlineKeyboardButton(
            text=f"@{b.bot_username}",
            callback_data=f"pick_{action}_{b.id}",
        )]
        for b in bots
    ]
    buttons.append([InlineKeyboardButton(
        text=_('btn_back'), callback_data="back_menu"
    )])

    await callback.message.edit_text(
        _("which_bot"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()
    return None, None


async def get_current_bot(session: AsyncSession, admin_id: int, state: FSMContext):
    """Get the currently selected bot from state, or fallback to first owned bot."""
    data = await state.get_data()
    selected_id = data.get("selected_bot_id")
    if selected_id:
        return await get_bot_by_id(session, selected_id)
    return await get_bot_by_admin(session, admin_id)
