from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.inline import back_kb, main_menu_kb
from db.engine import async_session
from db.models import EndUser, Subscription
from services.admin_service import get_admin_by_telegram_id
from services.bot_service import get_bot_by_admin
from sqlalchemy import select, and_

router = Router()


@router.callback_query(F.data == "manage_users")
async def show_users(callback: CallbackQuery):
    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, callback.from_user.id)
        user_bot = await get_bot_by_admin(session, admin.id)

        if not user_bot:
            await callback.message.edit_text(
                "⚠️ Sizda hali bot yo'q.",
                reply_markup=main_menu_kb(),
            )
            await callback.answer()
            return

        result = await session.execute(
            select(EndUser).where(EndUser.user_bot_id == user_bot.id)
            .order_by(EndUser.created_at.desc())
            .limit(20)
        )
        users = result.scalars().all()

    if not users:
        await callback.message.edit_text(
            "👥 Hali foydalanuvchilar yo'q.",
            reply_markup=back_kb(),
        )
        await callback.answer()
        return

    text = "👥 <b>Foydalanuvchilar</b> (oxirgi 20 ta):\n\n"
    buttons = []
    for user in users:
        status = "🚫" if user.banned else "✅"
        text += f"{status} @{user.username or '—'} (ID: {user.telegram_id})\n"
        buttons.append([
            InlineKeyboardButton(
                text=f"{'Unban' if user.banned else 'Ban'} @{user.username or user.telegram_id}",
                callback_data=f"toggle_ban_{user.id}",
            )
        ])

    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_menu")])
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_ban_"))
async def toggle_user_ban(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[2])

    async with async_session() as session:
        result = await session.execute(
            select(EndUser).where(EndUser.id == user_id)
        )
        end_user = result.scalar_one_or_none()
        if end_user:
            end_user.banned = not end_user.banned
            action = "bloklandi" if end_user.banned else "blokdan chiqarildi"
            await session.commit()

    await callback.answer(f"✅ Foydalanuvchi {action}!")
    # Refresh user list
    await show_users(callback)
