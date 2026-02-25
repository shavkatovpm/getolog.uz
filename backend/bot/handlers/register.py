import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.keyboards.inline import main_menu_kb, confirm_kb, duration_kb, back_kb, check_channel_kb, card_or_free_kb
from bot.handlers.subscription import PLAN_FEATURES
from bot.middlewares.i18n import get_text
from core.bot_manager import BotManager
from db.engine import async_session
from services.admin_service import get_admin_by_telegram_id, get_active_subscription
from services.bot_service import validate_token, create_bot, get_bots_by_admin, add_channel
from utils.constants import RegisterStates, PlanName
from utils.validators import validate_card

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "create_bot")
async def start_create_bot(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

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
            _("bot_limit_reached").format(
                count=len(existing_bots),
                limit=bot_limit,
                names=bot_names,
                plan=plan.capitalize(),
            ),
            reply_markup=back_kb(lang=i18n_lang),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        _("send_token_prompt"),
        reply_markup=back_kb(lang=i18n_lang),
        disable_web_page_preview=True,
    )
    await state.set_state(RegisterStates.waiting_token)
    await callback.answer()


@router.message(RegisterStates.waiting_token)
async def process_token(message: Message, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    token = message.text.strip()

    # Basic validation
    if ":" not in token or len(token) < 30:
        await message.answer(
            _("token_format_error"),
            reply_markup=back_kb(lang=i18n_lang),
        )
        return

    await message.answer(_("token_checking"))

    # Validate with Telegram API
    bot_info = await validate_token(token)
    if not bot_info:
        await message.answer(
            _("token_invalid"),
            reply_markup=back_kb(lang=i18n_lang),
        )
        return

    # Remove webhook if set (needed for get_updates to work), but keep pending updates
    try:
        temp_bot = Bot(token=token)
        await temp_bot.delete_webhook()
        await temp_bot.session.close()
    except Exception:
        pass

    await state.update_data(token=token, bot_info=bot_info)

    await message.answer(
        _("bot_found_ask_card").format(username=bot_info["username"]),
        reply_markup=card_or_free_kb(lang=i18n_lang),
    )
    await state.set_state(RegisterStates.waiting_card)


@router.message(RegisterStates.waiting_card)
async def process_card(message: Message, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    formatted = validate_card(message.text)
    if not formatted:
        await message.answer(
            _("card_invalid"),
            reply_markup=back_kb(lang=i18n_lang),
        )
        return

    await state.update_data(card_number=formatted)
    data = await state.get_data()

    await message.answer(
        _("add_bot_to_channel").format(username=data["bot_info"]["username"]),
        reply_markup=check_channel_kb(lang=i18n_lang),
    )
    await state.set_state(RegisterStates.waiting_channel)


@router.callback_query(RegisterStates.waiting_card, F.data == "reg_free_mode")
async def choose_free_mode(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    data = await state.get_data()

    await state.update_data(is_free=True, card_number=None, price=0, duration=0)

    await callback.message.edit_text(
        _("free_mode_selected").format(username=data["bot_info"]["username"]),
        reply_markup=check_channel_kb(lang=i18n_lang),
    )
    await state.set_state(RegisterStates.waiting_channel)
    await callback.answer()


@router.callback_query(RegisterStates.waiting_channel, F.data == "check_channel")
async def check_channel_auto(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    data = await state.get_data()
    token = data["token"]

    await callback.answer(_("checking"))

    try:
        temp_bot = Bot(token=token)
        # Get ALL update types — no filter
        updates = await temp_bot.get_updates()

        logger.info(f"Channel auto-detect: got {len(updates)} updates")

        # Find the LAST my_chat_member event where bot became admin
        found_chat = None
        for update in reversed(updates):
            if update.my_chat_member:
                member = update.my_chat_member
                logger.info(
                    f"  my_chat_member: chat={member.chat.title} ({member.chat.id}), "
                    f"status={member.new_chat_member.status}"
                )
                if member.new_chat_member.status in ("administrator", "creator"):
                    found_chat = member.chat
                    break

        await temp_bot.session.close()
    except Exception as e:
        logger.error(f"Channel auto-detect error: {e}")
        await callback.message.edit_text(
            _("channel_error"),
            reply_markup=check_channel_kb(lang=i18n_lang),
        )
        return

    if not found_chat:
        await callback.message.edit_text(
            _("channel_not_added").format(username=data["bot_info"]["username"]),
            reply_markup=check_channel_kb(lang=i18n_lang),
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
        summary = _("bot_summary_free").format(
            username=data["bot_info"]["username"],
            channel=found_chat.title,
        )
        await callback.message.edit_text(summary, reply_markup=confirm_kb("reg", lang=i18n_lang))
    else:
        await callback.message.edit_text(
            _("channel_found_ask_price").format(
                type=chat_type.capitalize(),
                title=found_chat.title,
            ),
            reply_markup=back_kb(lang=i18n_lang),
        )
        await state.set_state(RegisterStates.waiting_price)


@router.message(RegisterStates.waiting_channel, F.forward_from_chat)
async def check_channel_forward(message: Message, state: FSMContext, i18n_lang: str = "uz"):
    """Detect channel from a forwarded message — most reliable method."""
    _ = lambda key: get_text(key, i18n_lang)

    data = await state.get_data()
    token = data["token"]
    bot_user_id = data["bot_info"]["id"]
    chat = message.forward_from_chat

    # Only accept channels and supergroups
    if chat.type not in ("channel", "supergroup", "group"):
        await message.answer(
            _("forward_not_channel"),
            reply_markup=check_channel_kb(lang=i18n_lang),
        )
        return

    try:
        temp_bot = Bot(token=token)
        member = await temp_bot.get_chat_member(chat.id, bot_user_id)
        await temp_bot.session.close()

        if member.status not in ("administrator", "creator"):
            await message.answer(
                _("channel_not_added").format(username=data["bot_info"]["username"]),
                reply_markup=check_channel_kb(lang=i18n_lang),
            )
            return
    except Exception as e:
        logger.error(f"Channel forward check error: {e}")
        await message.answer(
            _("channel_error"),
            reply_markup=check_channel_kb(lang=i18n_lang),
        )
        return

    chat_type = "channel" if chat.type == "channel" else "group"
    await state.update_data(
        channel_id=chat.id,
        channel_title=chat.title,
        channel_type=chat_type,
    )

    data = await state.get_data()
    if data.get("is_free"):
        summary = _("bot_summary_free").format(
            username=data["bot_info"]["username"],
            channel=chat.title,
        )
        await message.answer(summary, reply_markup=confirm_kb("reg", lang=i18n_lang))
    else:
        await message.answer(
            _("channel_found_ask_price").format(
                type=chat_type.capitalize(),
                title=chat.title,
            ),
            reply_markup=back_kb(lang=i18n_lang),
        )
        await state.set_state(RegisterStates.waiting_price)


@router.callback_query(RegisterStates.waiting_channel, F.data == "manual_channel_id")
async def switch_to_manual(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    await callback.message.edit_text(
        _("manual_channel_prompt"),
        reply_markup=back_kb(lang=i18n_lang),
    )
    await state.set_state(RegisterStates.waiting_channel_manual)
    await callback.answer()


@router.message(RegisterStates.waiting_channel_manual)
async def process_channel_manual(message: Message, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    data = await state.get_data()
    token = data["token"]
    bot_user_id = data["bot_info"]["id"]
    raw = message.text.strip()

    # Parse: @username or numeric ID
    if raw.startswith("@"):
        chat_id = raw
    else:
        try:
            chat_id = int(raw)
        except ValueError:
            await message.answer(
                _("channel_id_invalid"),
                reply_markup=back_kb(lang=i18n_lang),
            )
            return

    try:
        temp_bot = Bot(token=token)
        chat = await temp_bot.get_chat(chat_id)
        member = await temp_bot.get_chat_member(chat.id, bot_user_id)
        await temp_bot.session.close()

        if member.status not in ("administrator", "creator"):
            await message.answer(
                _("channel_not_added").format(username=data["bot_info"]["username"]),
                reply_markup=back_kb(lang=i18n_lang),
            )
            return
    except Exception:
        await message.answer(
            _("channel_not_found"),
            reply_markup=back_kb(lang=i18n_lang),
        )
        return

    chat_type = "channel" if chat.type == "channel" else "group"
    await state.update_data(
        channel_id=chat.id,
        channel_title=chat.title,
        channel_type=chat_type,
    )

    data = await state.get_data()
    if data.get("is_free"):
        summary = _("bot_summary_free").format(
            username=data["bot_info"]["username"],
            channel=chat.title,
        )
        await message.answer(summary, reply_markup=confirm_kb("reg", lang=i18n_lang))
    else:
        await message.answer(
            _("channel_found_ask_price").format(
                type=chat_type.capitalize(),
                title=chat.title,
            ),
            reply_markup=back_kb(lang=i18n_lang),
        )
        await state.set_state(RegisterStates.waiting_price)


@router.message(RegisterStates.waiting_price)
async def process_price(message: Message, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    try:
        price = int(message.text.strip().replace(" ", ""))
        if price < 1000:
            raise ValueError
    except ValueError:
        await message.answer(
            _("price_invalid"),
            reply_markup=back_kb(lang=i18n_lang),
        )
        return

    await state.update_data(price=price)

    await message.answer(
        _("select_duration"),
        reply_markup=duration_kb(lang=i18n_lang),
    )
    await state.set_state(RegisterStates.waiting_duration)


@router.callback_query(RegisterStates.waiting_duration, F.data.startswith("dur_"))
async def process_duration(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    duration = int(callback.data.split("_")[1])
    data = await state.get_data()

    duration_text = {
        0: _("duration_lifetime"),
        1: _("duration_1m"),
        6: _("duration_6m"),
        12: _("duration_12m"),
    }[duration]
    price_formatted = f"{data['price']:,}".replace(",", " ")

    summary = _("bot_summary").format(
        username=data["bot_info"]["username"],
        channel=data["channel_title"],
        price=price_formatted,
        duration=duration_text,
        card=data["card_number"],
    )

    await state.update_data(duration=duration)
    await callback.message.edit_text(summary, reply_markup=confirm_kb("reg", lang=i18n_lang))
    await callback.answer()


@router.callback_query(F.data == "reg_confirm")
async def confirm_registration(callback: CallbackQuery, state: FSMContext, bot_manager: BotManager, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

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
            _("bot_register_failed").format(username=data["bot_info"]["username"]),
            reply_markup=main_menu_kb(lang=i18n_lang),
        )
        await state.clear()
        await callback.answer()
        return

    if data.get("is_free"):
        success_text = _("bot_created_free").format(username=data["bot_info"]["username"])
    else:
        success_text = _("bot_created_paid").format(username=data["bot_info"]["username"])

    await callback.message.edit_text(success_text, reply_markup=main_menu_kb(lang=i18n_lang))
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "reg_cancel")
async def cancel_registration(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    await state.clear()
    await callback.message.edit_text(
        _("registration_cancelled"),
        reply_markup=main_menu_kb(lang=i18n_lang),
    )
    await callback.answer()
