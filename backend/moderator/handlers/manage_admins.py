from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from config import config
from db.engine import async_session
from moderator.keyboards.inline import mod_back_kb
from services.admin_service import get_all_admins, ban_admin, unban_admin
from db.models import UserAdmin

router = Router()


@router.callback_query(F.data == "mod_admins")
async def show_admins(callback: CallbackQuery):
    if callback.from_user.id not in config.moderator_ids:
        await callback.answer("⛔")
        return

    async with async_session() as session:
        admins = await get_all_admins(session)

    if not admins:
        await callback.message.edit_text(
            "👥 Hali adminlar yo'q.",
            reply_markup=mod_back_kb(),
        )
        await callback.answer()
        return

    text = f"👥 <b>Adminlar</b> ({len(admins)} ta):\n\n"
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

    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="mod_menu")])
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("mod_toggle_"))
async def toggle_admin_ban(callback: CallbackQuery):
    if callback.from_user.id not in config.moderator_ids:
        await callback.answer("⛔")
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
                await callback.answer("✅ Blokdan chiqarildi!")
            else:
                await ban_admin(session, admin_id)
                await callback.answer("🚫 Bloklandi!")

    await show_admins(callback)
