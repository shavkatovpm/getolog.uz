from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.keyboards.inline import settings_kb, back_kb, main_menu_kb
from db.engine import async_session
from services.admin_service import get_admin_by_telegram_id
from services.bot_service import get_bot_by_admin, update_bot_settings
from utils.constants import SettingsStates

router = Router()


@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery):
    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, callback.from_user.id)
        user_bot = await get_bot_by_admin(session, admin.id)

    if not user_bot:
        await callback.message.edit_text(
            "⚠️ Sizda hali bot yo'q. Avval bot yarating.",
            reply_markup=main_menu_kb(),
        )
        await callback.answer()
        return

    text = (
        "⚙️ <b>Bot sozlamalari</b>\n\n"
        f"🤖 Bot: @{user_bot.bot_username}\n"
        f"💳 Karta: {user_bot.card_number or '—'}\n"
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
        reply_markup=back_kb(),
    )
    await state.set_state(SettingsStates.waiting_welcome)
    await callback.answer()


@router.message(SettingsStates.waiting_welcome)
async def save_welcome(message: Message, state: FSMContext):
    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, message.from_user.id)
        user_bot = await get_bot_by_admin(session, admin.id)
        await update_bot_settings(session, user_bot.id, welcome_message=message.text)

    await message.answer(
        "✅ Salomlash xabari yangilandi!",
        reply_markup=settings_kb(),
    )
    await state.clear()


@router.callback_query(F.data == "set_card")
async def ask_card(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "💳 Yangi <b>karta raqamini</b> yuboring:\n"
        "(Masalan: 8600 1234 5678 9012)",
        reply_markup=back_kb(),
    )
    await state.set_state(SettingsStates.waiting_card)
    await callback.answer()


@router.message(SettingsStates.waiting_card)
async def save_card(message: Message, state: FSMContext):
    card = message.text.strip().replace(" ", "")
    if not card.isdigit() or len(card) != 16:
        await message.answer("❌ Karta raqami 16 ta raqamdan iborat bo'lishi kerak:")
        return

    formatted = " ".join(card[i:i+4] for i in range(0, 16, 4))

    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, message.from_user.id)
        user_bot = await get_bot_by_admin(session, admin.id)
        await update_bot_settings(session, user_bot.id, card_number=formatted)

    await message.answer(
        f"✅ Karta yangilandi: {formatted}",
        reply_markup=settings_kb(),
    )
    await state.clear()


@router.callback_query(F.data == "set_price")
async def ask_price(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "💰 Yangi <b>narxni</b> yuboring (UZS da):\n"
        "(Masalan: 50000)",
        reply_markup=back_kb(),
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
        await message.answer("❌ Narx kamida 1000 UZS bo'lishi kerak:")
        return

    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, message.from_user.id)
        user_bot = await get_bot_by_admin(session, admin.id)
        # Update first channel price
        from services.bot_service import get_channels_by_bot
        channels = await get_channels_by_bot(session, user_bot.id)
        if channels:
            channels[0].price = price
            await session.commit()

    price_formatted = f"{price:,}".replace(",", " ")
    await message.answer(
        f"✅ Narx yangilandi: {price_formatted} UZS",
        reply_markup=settings_kb(),
    )
    await state.clear()
