import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.helpers import require_bot
from bot.keyboards.inline import back_bot_kb, main_menu_kb
from bot.middlewares.i18n import get_text
from db.engine import async_session
from services.payment_service import get_pending_payments, approve_payment, reject_payment, get_payment_by_id
from services.subscription_service import create_subscription
from utils.constants import PaymentStatus
from core.cache import cache_delete
from core.invite_link import create_invite_link

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "payments")
async def show_payments(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    user_bot, admin = await require_bot(callback, state, "payments", i18n_lang=i18n_lang)
    if not user_bot:
        return

    async with async_session() as session:
        pending = await get_pending_payments(session, user_bot.id)

    if not pending:
        await callback.message.edit_text(
            _("no_pending_payments").format(username=user_bot.bot_username),
            reply_markup=back_bot_kb(lang=i18n_lang),
        )
        await callback.answer()
        return

    text = _("pending_payments_header").format(
        username=user_bot.bot_username, count=len(pending)
    )

    buttons = []
    for p in pending[:10]:
        amount_fmt = f"{float(p.amount):,.0f}".replace(",", " ")
        username = p.end_user.username or p.end_user.telegram_id
        text += f"#{p.id} — {amount_fmt} UZS — @{username}\n"
        buttons.append([
            InlineKeyboardButton(
                text=f"#{p.id} {_('btn_approve')}",
                callback_data=f"pay_approve_{p.id}",
            ),
            InlineKeyboardButton(
                text=f"#{p.id} {_('btn_reject')}",
                callback_data=f"pay_reject_{p.id}",
            ),
        ])

    buttons.append([InlineKeyboardButton(
        text=_('btn_back'), callback_data="back_bot_dashboard"
    )])

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pay_approve_"))
async def handle_approve(callback: CallbackQuery, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    payment_id = int(callback.data.split("_")[2])

    async with async_session() as session:
        payment = await get_payment_by_id(session, payment_id)
        if not payment or payment.status != PaymentStatus.PENDING:
            await callback.answer(_("payment_not_found_or_processed"))
            return

        channel = payment.channel
        end_user = payment.end_user

        from services.bot_service import get_bot_by_id
        from core.encryption import decrypt_token
        user_bot = await get_bot_by_id(session, payment.user_bot_id)
        if not user_bot:
            await callback.answer(_("bot_not_found"))
            return

        try:
            token = decrypt_token(user_bot.bot_token)
            temp_bot = Bot(token=token)
            invite_link = await create_invite_link(temp_bot, channel.telegram_chat_id)
            await temp_bot.session.close()
        except Exception as e:
            logger.error(f"Failed to create invite link: {e}")
            await callback.message.edit_text(
                _("invite_link_error").format(error=e),
                reply_markup=back_bot_kb(lang=i18n_lang),
            )
            await callback.answer("⚠️")
            return

        payment = await approve_payment(session, payment_id)
        if not payment:
            await callback.answer(_("payment_not_found_or_processed"))
            return

        sub = await create_subscription(
            session,
            end_user_id=end_user.id,
            channel_id=channel.id,
            payment_id=payment.id,
            invite_link=invite_link,
            duration_months=channel.duration_months,
        )

    # Notify end user — use end_user's language
    eu_lang = end_user.language or "uz"
    _eu = lambda key: get_text(key, eu_lang)
    notify_failed = False
    try:
        duration_text = {
            0: _eu("duration_lifetime"), 1: _eu("duration_1m"),
            6: _eu("duration_6m"), 12: _eu("duration_12m"),
        }.get(channel.duration_months, f"{channel.duration_months}")
        await callback.bot.send_message(
            end_user.telegram_id,
            _eu("payment_approved_user").format(
                channel=channel.title, duration=duration_text, link=invite_link
            ),
        )
    except Exception as e:
        logger.error(f"Failed to notify end user: {e}")
        notify_failed = True

    await cache_delete(f"stats:{payment.user_bot_id}")

    result_text = _("payment_approved_admin").format(
        id=payment_id, username=end_user.username or end_user.telegram_id
    )
    if notify_failed:
        result_text += _("payment_notify_failed").format(link=invite_link)

    await callback.message.edit_text(result_text, reply_markup=back_bot_kb(lang=i18n_lang))
    await callback.answer(f"✅")


@router.callback_query(F.data.startswith("pay_reject_"))
async def handle_reject(callback: CallbackQuery, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)
    payment_id = int(callback.data.split("_")[2])

    async with async_session() as session:
        payment = await reject_payment(session, payment_id)
        if not payment:
            await callback.answer(_("payment_not_found_or_processed"))
            return

        payment = await get_payment_by_id(session, payment_id)
        end_user = payment.end_user
        channel = payment.channel

    # Notify end user in their language
    eu_lang = end_user.language or "uz"
    _eu = lambda key: get_text(key, eu_lang)
    try:
        await callback.bot.send_message(
            end_user.telegram_id,
            _eu("payment_rejected_user").format(channel=channel.title),
        )
    except Exception as e:
        logger.error(f"Failed to notify end user about rejection: {e}")

    await callback.message.edit_text(
        _("payment_rejected_admin").format(
            id=payment_id, username=end_user.username or end_user.telegram_id
        ),
        reply_markup=back_bot_kb(lang=i18n_lang),
    )
    await callback.answer("❌")
