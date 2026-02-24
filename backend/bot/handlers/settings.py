from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.helpers import require_bot, get_current_bot
from bot.keyboards.inline import settings_kb, back_kb, back_bot_kb, main_menu_kb
from bot.handlers.subscription import PLAN_FEATURES
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
async def show_settings(callback: CallbackQuery, state: FSMContext):
    user_bot, admin = await require_bot(callback, state, "settings")
    if not user_bot:
        return

    text = (
        "⚙️ <b>Bot sozlamalari</b>\n\n"
        f"🤖 Bot: @{user_bot.bot_username}\n"
        f"💳 Karta: {decrypt_card(user_bot.card_number) if user_bot.card_number else '—'}\n"
        f"💬 Salomlash: {(user_bot.welcome_message or '—')[:50]}...\n\n"
        "Nimani o'zgartirmoqchisiz?"
    )
    await callback.message.edit_text(text, reply_markup=settings_kb())
    await callback.answer()


@router.callback_query(F.data == "set_welcome")
async def ask_welcome(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "✏️ Yangi <b>salomlash xabarini</b> yuboring.\n\n"
        "Bu xabar end user bot'ga /start bosganda ko'rinadi.",
        reply_markup=back_bot_kb(),
    )
    await state.set_state(SettingsStates.waiting_welcome)
    await callback.answer()


@router.message(SettingsStates.waiting_welcome)
async def save_welcome(message: Message, state: FSMContext):
    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, message.from_user.id)
        user_bot = await get_current_bot(session, admin.id, state)
        await update_bot_settings(session, user_bot.id, welcome_message=message.text)
        await cache_delete(f"settings:{user_bot.id}")

    await message.answer(
        "✅ Salomlash xabari yangilandi!",
        reply_markup=settings_kb(),
    )
    await state.set_state(None)


@router.callback_query(F.data == "set_card")
async def ask_card(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "💳 Yangi <b>karta raqamini</b> yuboring:\n"
        "(Masalan: 8600 1234 5678 9012)",
        reply_markup=back_bot_kb(),
    )
    await state.set_state(SettingsStates.waiting_card)
    await callback.answer()


@router.message(SettingsStates.waiting_card)
async def save_card(message: Message, state: FSMContext):
    formatted = validate_card(message.text)
    if not formatted:
        await message.answer(
            "❌ Karta raqami noto'g'ri. 16 ta raqamdan iborat to'g'ri karta kiriting:",
            reply_markup=back_bot_kb(),
        )
        return

    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, message.from_user.id)
        user_bot = await get_current_bot(session, admin.id, state)
        await update_bot_settings(session, user_bot.id, card_number=formatted)
        await cache_delete(f"settings:{user_bot.id}")

    await message.answer(
        f"✅ Karta yangilandi: {formatted}",
        reply_markup=settings_kb(),
    )
    await state.set_state(None)


@router.callback_query(F.data == "set_price")
async def ask_price(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "💰 Yangi <b>narxni</b> yuboring (UZS da):\n"
        "(Masalan: 50000)",
        reply_markup=back_bot_kb(),
    )
    await state.set_state(SettingsStates.waiting_price)
    await callback.answer()


@router.message(SettingsStates.waiting_price)
async def save_price(message: Message, state: FSMContext):
    try:
        price = int(message.text.strip().replace(" ", ""))
        if price < 1000:
            raise ValueError
    except ValueError:
        await message.answer(
            "❌ Narx kamida 1000 UZS bo'lishi kerak:",
            reply_markup=back_bot_kb(),
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
        f"✅ Narx yangilandi: {price_formatted} UZS",
        reply_markup=settings_kb(),
    )
    await state.set_state(None)


# --- Collaborator (Hamkor) Management ---


@router.callback_query(F.data == "manage_collabs")
async def manage_collabs(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, callback.from_user.id)
        sub = await get_active_subscription(session, admin.id)
        user_bot = await get_current_bot(session, admin.id, state)

    plan = sub.plan if sub else PlanName.FREE
    features = PLAN_FEATURES.get(plan, PLAN_FEATURES[PlanName.FREE])

    if features["multi_admin_limit"] == 0:
        await callback.message.edit_text(
            "👥 <b>Hamkorlar</b>\n\n"
            "❌ Bepul tarifda hamkor qo'shish imkoni yo'q.\n"
            "Standard yoki Premium tarifga o'ting.",
            reply_markup=settings_kb(),
        )
        await callback.answer()
        return

    if not user_bot:
        await callback.message.edit_text(
            "⚠️ Avval bot yarating.",
            reply_markup=main_menu_kb(),
        )
        await callback.answer()
        return

    collabs = user_bot.collaborators
    limit = features["multi_admin_limit"]

    text = f"👥 <b>Hamkorlar</b> ({len(collabs)}/{limit})\n\n"
    if collabs:
        for c in collabs:
            text += f"• @{c.username or c.telegram_id}\n"
    else:
        text += "Hozircha hamkor yo'q.\n"

    buttons = []
    if len(collabs) < limit:
        buttons.append([InlineKeyboardButton(
            text="➕ Hamkor qo'shish",
            callback_data="add_collab",
        )])
    for c in collabs:
        buttons.append([InlineKeyboardButton(
            text=f"❌ @{c.username or c.telegram_id} ni o'chirish",
            callback_data=f"remove_collab_{c.id}",
        )])
    buttons.append([
        InlineKeyboardButton(text="◀️ Orqaga", callback_data="settings"),
        InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_menu"),
    ])

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(F.data == "add_collab")
async def add_collab(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "👤 Hamkorning <b>Telegram ID</b> sini yuboring.\n\n"
        "ID olish uchun hamkor @getmyid_bot ga /start bossin.",
        reply_markup=back_bot_kb(),
    )
    await state.set_state(SettingsStates.waiting_collab_id)
    await callback.answer()


@router.message(SettingsStates.waiting_collab_id)
async def save_collab(message: Message, state: FSMContext):
    try:
        collab_tg_id = int(message.text.strip())
    except ValueError:
        await message.answer(
            "❌ Noto'g'ri ID. Raqam yuboring:",
            reply_markup=back_bot_kb(),
        )
        return

    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, message.from_user.id)
        sub = await get_active_subscription(session, admin.id)
        user_bot = await get_current_bot(session, admin.id, state)

        if not user_bot:
            await message.answer("⚠️ Bot topilmadi.", reply_markup=settings_kb())
            await state.set_state(None)
            return

        plan = sub.plan if sub else "free"
        features = PLAN_FEATURES.get(plan, PLAN_FEATURES["free"])
        limit = features["multi_admin_limit"]

        # Check limit
        if len(user_bot.collaborators) >= limit:
            await message.answer(
                f"❌ Hamkor limiti ({limit}) ga yetdingiz.",
                reply_markup=settings_kb(),
            )
            await state.set_state(None)
            return

        # Check if already exists
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
                "❌ Bu foydalanuvchi allaqachon hamkor sifatida qo'shilgan.",
                reply_markup=settings_kb(),
            )
            await state.set_state(None)
            return

        # Check not adding self
        if collab_tg_id == message.from_user.id:
            await message.answer(
                "❌ O'zingizni hamkor qilib qo'sha olmaysiz.",
                reply_markup=settings_kb(),
            )
            await state.set_state(None)
            return

        # Try to get username
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
        f"✅ Hamkor qo'shildi: @{username or collab_tg_id}",
        reply_markup=settings_kb(),
    )
    await state.set_state(None)


@router.callback_query(F.data.startswith("remove_collab_"))
async def remove_collab(callback: CallbackQuery, state: FSMContext):
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
            await callback.answer(f"✅ @{username} o'chirildi!")
        else:
            await callback.answer("❌ Hamkor topilmadi.")

    # Refresh the list
    await manage_collabs(callback, state)


# --- Bot Deactivation ---


@router.callback_query(F.data == "deactivate_bot")
async def ask_deactivate_bot(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, callback.from_user.id)
        user_bot = await get_current_bot(session, admin.id, state)

    if not user_bot:
        await callback.message.edit_text(
            "⚠️ Bot topilmadi.",
            reply_markup=main_menu_kb(),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"⚠️ <b>@{user_bot.bot_username} ni o'chirishni tasdiqlang.</b>\n\n"
        "Bu botni o'chirsangiz:\n"
        "• Bot foydalanuvchilarga javob bermaydi\n"
        "• Barcha sozlamalar saqlanib qoladi\n\n"
        "Davom etasizmi?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑 O'chirish",
                    callback_data=f"do_deactivate_{user_bot.id}",
                ),
                InlineKeyboardButton(
                    text="❌ Bekor qilish",
                    callback_data="settings",
                ),
            ],
        ]),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("do_deactivate_"))
async def confirm_deactivate_bot(
    callback: CallbackQuery, state: FSMContext, bot_manager: BotManager
):
    bot_id = int(callback.data.split("_")[2])

    async with async_session() as session:
        success = await deactivate_bot(session, bot_id)

    if success:
        await bot_manager.stop_bot(bot_id)
        await state.update_data(selected_bot_id=None)
        await callback.message.edit_text(
            "✅ Bot muvaffaqiyatli o'chirildi.",
            reply_markup=main_menu_kb(),
        )
    else:
        await callback.message.edit_text(
            "❌ Bot topilmadi.",
            reply_markup=main_menu_kb(),
        )
    await callback.answer()
