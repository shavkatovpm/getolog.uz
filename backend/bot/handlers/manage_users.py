import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from core.cache import cache_get, cache_set, cache_delete
from core.encryption import decrypt_token

logger = logging.getLogger(__name__)

from bot.helpers import require_bot
from bot.keyboards.inline import back_kb
from db.engine import async_session
from db.models import EndUser
from sqlalchemy import select

router = Router()


@router.callback_query(F.data == "manage_users")
async def show_users(callback: CallbackQuery, state: FSMContext):
    user_bot, admin = await require_bot(callback, state, "users")
    if not user_bot:
        return

    cache_key = f"users:{user_bot.id}"
    cached = await cache_get(cache_key)

    if cached is not None:
        users_data = cached.get("users", [])
    else:
        async with async_session() as session:
            result = await session.execute(
                select(EndUser).where(EndUser.user_bot_id == user_bot.id)
                .order_by(EndUser.created_at.desc())
                .limit(20)
            )
            users = result.scalars().all()
            users_data = [
                {"id": u.id, "username": u.username, "telegram_id": u.telegram_id, "banned": u.banned}
                for u in users
            ]
            await cache_set(cache_key, {"users": users_data}, ttl=30)

    if not users_data:
        await callback.message.edit_text(
            f"👥 <b>Foydalanuvchilar</b> — @{user_bot.bot_username}\n\n"
            "Hali foydalanuvchilar yo'q.",
            reply_markup=back_kb(),
        )
        await callback.answer()
        return

    text = f"👥 <b>Foydalanuvchilar</b> — @{user_bot.bot_username} (oxirgi 20 ta):\n\n"
    buttons = []
    for user in users_data:
        banned = user["banned"]
        username = user["username"]
        telegram_id = user["telegram_id"]
        user_id = user["id"]
        status = "🚫" if banned else "✅"
        text += f"{status} @{username or '—'} (ID: {telegram_id})\n"
        buttons.append([
            InlineKeyboardButton(
                text=f"{'Unban' if banned else 'Ban'} @{username or telegram_id}",
                callback_data=f"toggle_ban_{user_id}",
            )
        ])

    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_menu")])
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_ban_"))
async def toggle_user_ban(callback: CallbackQuery, state: FSMContext):
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

            # Notify end user via their bot
            try:
                user_bot = end_user.bot
                token = decrypt_token(user_bot.bot_token)
                temp_bot = Bot(token=token)
                if end_user.banned:
                    await temp_bot.send_message(
                        end_user.telegram_id,
                        "⛔ Siz admin tomonidan <b>bloklangansiz</b>.\n"
                        "Botdan foydalana olmaysiz.",
                    )
                else:
                    await temp_bot.send_message(
                        end_user.telegram_id,
                        "✅ Siz admin tomonidan <b>blokdan chiqarildingiz</b>.\n"
                        "Botdan qayta foydalanishingiz mumkin.",
                    )
                await temp_bot.session.close()
            except Exception as e:
                logger.error(f"Failed to notify end user about ban toggle: {e}")

    # Invalidate users cache
    if end_user:
        await cache_delete(f"users:{end_user.user_bot_id}")

    await callback.answer(f"✅ Foydalanuvchi {action}!")
    # Refresh user list
    await show_users(callback, state)
