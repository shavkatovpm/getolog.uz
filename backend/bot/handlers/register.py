import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.keyboards.inline import main_menu_kb, confirm_kb, duration_kb, back_kb
from db.engine import async_session
from services.admin_service import get_admin_by_telegram_id
from services.bot_service import validate_token, create_bot, get_bot_by_admin, add_channel
from utils.constants import RegisterStates

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "create_bot")
async def start_create_bot(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, callback.from_user.id)
        existing_bot = await get_bot_by_admin(session, admin.id)

    if existing_bot:
        await callback.message.edit_text(
            f"🤖 Sizda allaqachon bot mavjud: @{existing_bot.bot_username}\n\n"
            "Yangi bot yaratish uchun avval mavjudni o'chirishingiz kerak.",
            reply_markup=back_kb(),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "🔑 <b>Bot tokenini yuboring</b>\n\n"
        "1. @BotFather ga o'ting\n"
        "2. /newbot buyrug'ini yuboring\n"
        "3. Bot nomini kiriting\n"
        "4. Olingan tokenni bu yerga yuboring\n\n"
        "⚠️ Token formati: <code>123456:ABC-DEF...</code>",
        reply_markup=back_kb(),
    )
    await state.set_state(RegisterStates.waiting_token)
    await callback.answer()


@router.message(RegisterStates.waiting_token)
async def process_token(message: Message, state: FSMContext):
    token = message.text.strip()

    # Basic validation
    if ":" not in token or len(token) < 30:
        await message.answer(
            "❌ Noto'g'ri format. Token quyidagicha bo'lishi kerak:\n"
            "<code>123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11</code>\n\n"
            "Qayta urinib ko'ring:"
        )
        return

    await message.answer("🔄 Token tekshirilmoqda...")

    # Validate with Telegram API
    bot_info = await validate_token(token)
    if not bot_info:
        await message.answer(
            "❌ Token noto'g'ri yoki bot o'chirilgan.\n"
            "Iltimos, @BotFather dan yangi token oling va qayta yuboring."
        )
        return

    await state.update_data(token=token, bot_info=bot_info)

    await message.answer(
        f"✅ Bot topildi: @{bot_info['username']}\n\n"
        "💳 Endi to'lov qabul qiladigan <b>karta raqamingizni</b> yuboring:\n"
        "(Masalan: 8600 1234 5678 9012)",
    )
    await state.set_state(RegisterStates.waiting_card)


@router.message(RegisterStates.waiting_card)
async def process_card(message: Message, state: FSMContext):
    card = message.text.strip().replace(" ", "")
    if not card.isdigit() or len(card) != 16:
        await message.answer(
            "❌ Karta raqami 16 ta raqamdan iborat bo'lishi kerak.\n"
            "Qayta kiriting:"
        )
        return

    # Format card number
    formatted = " ".join(card[i:i+4] for i in range(0, 16, 4))
    await state.update_data(card_number=formatted)

    await message.answer(
        "📢 Endi pullik kanal yoki guruhingizning <b>ID sini</b> yuboring.\n\n"
        "ID olish uchun:\n"
        "1. Kanal/guruhni oching\n"
        "2. @getmyid_bot ni kanalga qo'shing va ID ni oling\n"
        "3. ID ni bu yerga yuboring (masalan: -1001234567890)",
    )
    await state.set_state(RegisterStates.waiting_channel)


@router.message(RegisterStates.waiting_channel)
async def process_channel(message: Message, state: FSMContext):
    try:
        chat_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Noto'g'ri ID. Raqam yuboring (masalan: -1001234567890):")
        return

    # Try to get chat info
    data = await state.get_data()
    token = data["token"]
    try:
        temp_bot = Bot(token=token)
        chat = await temp_bot.get_chat(chat_id)
        await temp_bot.session.close()
    except Exception:
        await message.answer(
            "❌ Kanal/guruh topilmadi. Botni admin qilib qo'shganingizga ishonch hosil qiling.\n"
            "Qayta urinib ko'ring:"
        )
        return

    chat_type = "channel" if chat.type == "channel" else "group"
    await state.update_data(
        channel_id=chat_id,
        channel_title=chat.title,
        channel_type=chat_type,
    )

    await message.answer(
        f"✅ {chat_type.capitalize()} topildi: <b>{chat.title}</b>\n\n"
        "💰 Kirish narxini yuboring (UZS da):\n"
        "(Masalan: 50000)",
    )
    await state.set_state(RegisterStates.waiting_price)


@router.message(RegisterStates.waiting_price)
async def process_price(message: Message, state: FSMContext):
    try:
        price = int(message.text.strip().replace(" ", ""))
        if price < 1000:
            raise ValueError
    except ValueError:
        await message.answer("❌ Narx kamida 1000 UZS bo'lishi kerak. Qayta kiriting:")
        return

    await state.update_data(price=price)

    await message.answer(
        "📅 Obuna muddatini tanlang:",
        reply_markup=duration_kb(),
    )
    await state.set_state(RegisterStates.waiting_duration)


@router.callback_query(RegisterStates.waiting_duration, F.data.startswith("dur_"))
async def process_duration(callback: CallbackQuery, state: FSMContext):
    duration = int(callback.data.split("_")[1])
    data = await state.get_data()

    duration_text = {0: "Umrbod", 1: "1 oy", 6: "6 oy", 12: "12 oy"}[duration]
    price_formatted = f"{data['price']:,}".replace(",", " ")

    summary = (
        "📋 <b>Bot sozlamalari:</b>\n\n"
        f"🤖 Bot: @{data['bot_info']['username']}\n"
        f"📢 Kanal: {data['channel_title']}\n"
        f"💰 Narx: {price_formatted} UZS\n"
        f"📅 Muddat: {duration_text}\n"
        f"💳 Karta: {data['card_number']}\n\n"
        "Tasdiqlaysizmi?"
    )

    await state.update_data(duration=duration)
    await callback.message.edit_text(summary, reply_markup=confirm_kb("reg"))
    await callback.answer()


@router.callback_query(F.data == "reg_confirm")
async def confirm_registration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, callback.from_user.id)

        # Create bot record
        user_bot = await create_bot(
            session,
            user_admin_id=admin.id,
            token=data["token"],
            bot_username=data["bot_info"]["username"],
        )

        # Update card number
        from services.bot_service import update_bot_settings
        await update_bot_settings(session, user_bot.id, card_number=data["card_number"])

        # Add channel
        await add_channel(
            session,
            user_bot_id=user_bot.id,
            telegram_chat_id=data["channel_id"],
            chat_type=data["channel_type"],
            title=data["channel_title"],
            price=data["price"],
            duration_months=data["duration"],
        )

    # Register bot with bot_manager (will be done from main.py context)
    await state.update_data(user_bot_id=user_bot.id)

    await callback.message.edit_text(
        "✅ <b>Bot muvaffaqiyatli yaratildi!</b>\n\n"
        f"🤖 @{data['bot_info']['username']} endi ishlayapti.\n"
        "End userlar botga /start bosib, to'lov qilishlari mumkin.\n\n"
        "Sozlamalarni o'zgartirish uchun menyudan foydalaning.",
        reply_markup=main_menu_kb(),
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "reg_cancel")
async def cancel_registration(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❌ Bot yaratish bekor qilindi.",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()
