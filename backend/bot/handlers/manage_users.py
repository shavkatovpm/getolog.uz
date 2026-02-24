import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from core.cache import cache_get, cache_set, cache_delete
from core.encryption import decrypt_token

logger = logging.getLogger(__name__)

from bot.helpers import require_bot
from bot.keyboards.inline import back_bot_kb
from bot.middlewares.i18n import get_text
from db.engine import async_session
from db.models import EndUser
from sqlalchemy import select

router = Router()


@router.callback_query(F.data == "manage_users")
async def show_users(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    user_bot, admin = await require_bot(callback, state, "users", i18n_lang=i18n_lang)
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
            _("no_users_yet").format(username=user_bot.bot_username),
            reply_markup=back_bot_kb(lang=i18n_lang),
        )
        await callback.answer()
        return

    text = _("manage_users_header").format(username=user_bot.bot_username)
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

    buttons.append([InlineKeyboardButton(
        text=_('btn_back'), callback_data="back_bot_dashboard"
    )])
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_ban_"))
async def toggle_user_ban(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    user_id = int(callback.data.split("_")[2])

    async with async_session() as session:
        result = await session.execute(
            select(EndUser).where(EndUser.id == user_id)
        )
        end_user = result.scalar_one_or_none()
        if end_user:
            end_user.banned = not end_user.banned
            action = _("action_banned") if end_user.banned else _("action_unbanned")
            await session.commit()

            # Notify end user via their bot — use end_user's language
            try:
                user_bot = end_user.bot
                token = decrypt_token(user_bot.bot_token)
                temp_bot = Bot(token=token)
                eu_lang = end_user.language or "uz"
                _eu = lambda key: get_text(key, eu_lang)
                if end_user.banned:
                    await temp_bot.send_message(
                        end_user.telegram_id,
                        _eu("user_banned_msg"),
                    )
                else:
                    await temp_bot.send_message(
                        end_user.telegram_id,
                        _eu("user_unbanned_msg"),
                    )
                await temp_bot.session.close()
            except Exception as e:
                logger.error(f"Failed to notify end user about ban toggle: {e}")

    if end_user:
        await cache_delete(f"users:{end_user.user_bot_id}")

    await callback.answer(_("user_ban_toggled").format(action=action))
    await show_users(callback, state, i18n_lang=i18n_lang)
