import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.keyboards.inline import main_menu_kb, confirm_kb, duration_kb, back_kb, check_channel_kb, card_or_free_kb
from bot.handlers.subscription import PLAN_FEATURES
from core.bot_manager import BotManager
from db.engine import async_session
from services.admin_service import get_admin_by_telegram_id, get_active_subscription
from services.bot_service import validate_token, create_bot, get_bots_by_admin, add_channel
from utils.constants import RegisterStates, PlanName
from utils.validators import validate_card

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "create_bot")
async def start_create_bot(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        admin = await get_admin_by_telegram_id(session, callback.from_user.id)
        sub = await get_active_subscription(session, admin.id)
        existing_bots = await get_bots_by_admin(session, admin.id)

    plan = sub.plan if sub else PlanName.FREE
    features = PLAN_FEATURES.get(plan, PLAN_FEATURES[PlanName.FREE])
    bot_limit = features["bot_limit"]

    if len(existing_bots) >= bot_limit:
        bot_names = ", ".join(f"@{b.bot_username}" for b in existing_bots)
        await callback.message.edit_text(
            f"🤖 Sizda {len(existing_bots)}/{bot_limit} ta bot mavjud: {bot_names}\n\n"
            f"📦 Joriy tarif: <b>{plan.capitalize()}</b>\n"
            "Ko'proq bot yaratish uchun tarifni oshiring.",
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
            "Qayta urinib ko'ring:",
            reply_markup=back_kb(),
        )
        return

    await message.answer("🔄 Token tekshirilmoqda...")

    # Validate with Telegram API
    bot_info = await validate_token(token)
    if not bot_info:
        await message.answer(
            "❌ Token noto'g'ri yoki bot o'chirilgan.\n"
            "Iltimos, @BotFather dan yangi token oling va qayta yuboring.",
            reply_markup=back_kb(),
        )
        return

    await state.update_data(token=token, bot_info=bot_info)

    await message.answer(
        f"✅ Bot topildi: @{bot_info['username']}\n\n"
        "💳 To'lov qabul qiladigan <b>karta raqamingizni</b> yuboring:\n"
        "(Masalan: 8600 1234 5678 9012)\n\n"
        "Yoki kanal/guruhga kirish bepul bo'lsa, quyidagi tugmani bosing:",
        reply_markup=card_or_free_kb(),
    )
    await state.set_state(RegisterStates.waiting_card)


@router.message(RegisterStates.waiting_card)
async def process_card(message: Message, state: FSMContext):
    formatted = validate_card(message.text)
    if not formatted:
        await message.answer(
            "❌ Karta raqami noto'g'ri. 16 ta raqamdan iborat to'g'ri karta kiriting.\n"
            "Qayta kiriting:",
            reply_markup=back_kb(),
        )
        return

    await state.update_data(card_number=formatted)

    # Clear old updates on the user bot so we only detect new channel additions
    data = await state.get_data()
    token = data["token"]
    try:
        temp_bot = Bot(token=token)
        await temp_bot.delete_webhook(drop_pending_updates=True)
        await temp_bot.session.close()
    except Exception:
        pass

    await message.answer(
        f"📢 <b>Endi @{data['bot_info']['username']} ni kanalga admin qilib qo'shing.</b>\n\n"
        "1. Kanal sozlamalariga o'ting\n"
        "2. Administratorlar bo'limiga kiring\n"
        f"3. @{data['bot_info']['username']} ni admin qilib qo'shing\n\n"
        "Qo'shgandan keyin quyidagi tugmani bosing:",
        reply_markup=check_channel_kb(),
    )
    await state.set_state(RegisterStates.waiting_channel)


@router.callback_query(RegisterStates.waiting_card, F.data == "reg_free_mode")
async def choose_free_mode(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    token = data["token"]

    await state.update_data(is_free=True, card_number=None, price=0, duration=0)

    # Clear old updates on the user bot
    try:
        temp_bot = Bot(token=token)
        await temp_bot.delete_webhook(drop_pending_updates=True)
        await temp_bot.session.close()
    except Exception:
        pass

    await callback.message.edit_text(
        f"🆓 <b>Bepul rejim tanlandi!</b>\n\n"
        f"📢 Endi @{data['bot_info']['username']} ni kanalga admin qilib qo'shing.\n\n"
        "1. Kanal sozlamalariga o'ting\n"
        "2. Administratorlar bo'limiga kiring\n"
        f"3. @{data['bot_info']['username']} ni admin qilib qo'shing\n\n"
        "Qo'shgandan keyin quyidagi tugmani bosing:",
        reply_markup=check_channel_kb(),
    )
    await state.set_state(RegisterStates.waiting_channel)
    await callback.answer()


@router.callback_query(RegisterStates.waiting_channel, F.data == "check_channel")
async def check_channel_auto(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    token = data["token"]

    await callback.answer("🔍 Tekshirilmoqda...")

    try:
        temp_bot = Bot(token=token)
        updates = await temp_bot.get_updates(allowed_updates=["my_chat_member"])

        found_chat = None
        for update in updates:
            if update.my_chat_member:
                member = update.my_chat_member
                if member.new_chat_member.status in ("administrator", "member"):
                    found_chat = member.chat
                    break

        await temp_bot.session.close()
    except Exception as e:
        logger.error(f"Channel auto-detect error: {e}")
        await callback.message.edit_text(
            "❌ Xatolik yuz berdi. Qayta urinib ko'ring.",
            reply_markup=check_channel_kb(),
        )
        return

    if not found_chat:
        await callback.message.edit_text(
            "❌ Bot hali kanalga qo'shilmagan.\n\n"
            f"@{data['bot_info']['username']} ni kanalga <b>admin</b> qilib qo'shing, "
            "keyin qayta tekshiring.",
            reply_markup=check_channel_kb(),
        )
        return

    chat_type = "channel" if found_chat.type == "channel" else "group"
    await state.update_data(
        channel_id=found_chat.id,
        channel_title=found_chat.title,
        channel_type=chat_type,
    )

    data = await state.get_data()
    if data.get("is_free"):
        # Free mode — skip price/duration, go to confirm
        summary = (
            "📋 <b>Bot sozlamalari:</b>\n\n"
            f"🤖 Bot: @{data['bot_info']['username']}\n"
            f"📢 Kanal: {found_chat.title}\n"
            "💰 Narx: Bepul\n"
            "📅 Muddat: Umrbod\n\n"
            "Tasdiqlaysizmi?"
        )
        await callback.message.edit_text(summary, reply_markup=confirm_kb("reg"))
    else:
        await callback.message.edit_text(
            f"✅ {chat_type.capitalize()} topildi: <b>{found_chat.title}</b>\n\n"
            "💰 Kirish narxini yuboring (UZS da):\n"
            "(Masalan: 50000)",
            reply_markup=back_kb(),
        )
        await state.set_state(RegisterStates.waiting_price)


@router.callback_query(RegisterStates.waiting_channel, F.data == "manual_channel_id")
async def switch_to_manual(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📢 Kanal yoki guruhingizning <b>ID sini</b> yuboring.\n\n"
        "ID olish: kanalga @getmyid_bot qo'shing.\n"
        "(Masalan: -1001234567890)",
        reply_markup=back_kb(),
    )
    await state.set_state(RegisterStates.waiting_channel_manual)
    await callback.answer()


@router.message(RegisterStates.waiting_channel_manual)
async def process_channel_manual(message: Message, state: FSMContext):
    try:
        chat_id = int(message.text.strip())
    except ValueError:
        await message.answer(
            "❌ Noto'g'ri ID. Raqam yuboring (masalan: -1001234567890):",
            reply_markup=back_kb(),
        )
        return

    data = await state.get_data()
    token = data["token"]
    try:
        temp_bot = Bot(token=token)
        chat = await temp_bot.get_chat(chat_id)
        await temp_bot.session.close()
    except Exception:
        await message.answer(
            "❌ Kanal/guruh topilmadi. Botni admin qilib qo'shganingizga ishonch hosil qiling.\n"
            "Qayta urinib ko'ring:",
            reply_markup=back_kb(),
        )
        return

    chat_type = "channel" if chat.type == "channel" else "group"
    await state.update_data(
        channel_id=chat_id,
        channel_title=chat.title,
        channel_type=chat_type,
    )

    data = await state.get_data()
    if data.get("is_free"):
        # Free mode — skip price/duration, go to confirm
        summary = (
            "📋 <b>Bot sozlamalari:</b>\n\n"
            f"🤖 Bot: @{data['bot_info']['username']}\n"
            f"📢 Kanal: {chat.title}\n"
            "💰 Narx: Bepul\n"
            "📅 Muddat: Umrbod\n\n"
            "Tasdiqlaysizmi?"
        )
        await message.answer(summary, reply_markup=confirm_kb("reg"))
    else:
        await message.answer(
            f"✅ {chat_type.capitalize()} topildi: <b>{chat.title}</b>\n\n"
            "💰 Kirish narxini yuboring (UZS da):\n"
            "(Masalan: 50000)",
            reply_markup=back_kb(),
        )
        await state.set_state(RegisterStates.waiting_price)


@router.message(RegisterStates.waiting_price)
async def process_price(message: Message, state: FSMContext):
    try:
        price = int(message.text.strip().replace(" ", ""))
        if price < 1000:
            raise ValueError
    except ValueError:
        await message.answer(
            "❌ Narx kamida 1000 UZS bo'lishi kerak. Qayta kiriting:",
            reply_markup=back_kb(),
        )
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
async def confirm_registration(callback: CallbackQuery, state: FSMContext, bot_manager: BotManager):
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

        # Update card number (if paid mode)
        if data.get("card_number"):
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

    # Register bot with bot_manager so it starts accepting updates
    result = await bot_manager.register_bot(user_bot.id, user_bot.bot_token)
    if result:
        logger.info(f"User bot @{data['bot_info']['username']} registered with BotManager")
    else:
        logger.error(f"Failed to register @{data['bot_info']['username']} with BotManager")
        await callback.message.edit_text(
            f"⚠️ Bot bazaga saqlandi, lekin ishga tushirishda xatolik yuz berdi.\n\n"
            f"🤖 @{data['bot_info']['username']}\n\n"
            "Server qayta ishga tushganda bot avtomatik faollashadi.",
            reply_markup=main_menu_kb(),
        )
        await state.clear()
        await callback.answer()
        return

    if data.get("is_free"):
        success_text = (
            "✅ <b>Bot muvaffaqiyatli yaratildi!</b>\n\n"
            f"🤖 @{data['bot_info']['username']} endi ishlayapti.\n"
            "🆓 Kirish bepul — end userlar botga /start bosib kanalga kirishlari mumkin.\n\n"
            "Sozlamalarni o'zgartirish uchun menyudan foydalaning."
        )
    else:
        success_text = (
            "✅ <b>Bot muvaffaqiyatli yaratildi!</b>\n\n"
            f"🤖 @{data['bot_info']['username']} endi ishlayapti.\n"
            "End userlar botga /start bosib, to'lov qilishlari mumkin.\n\n"
            "Sozlamalarni o'zgartirish uchun menyudan foydalaning."
        )
    await callback.message.edit_text(success_text, reply_markup=main_menu_kb())
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
