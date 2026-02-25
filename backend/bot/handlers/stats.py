from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.helpers import require_bot
from bot.keyboards.inline import back_bot_kb
from bot.middlewares.i18n import get_text
from db.engine import async_session
from services.stats_service import get_admin_stats

router = Router()


@router.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery, state: FSMContext, i18n_lang: str = "uz"):
    _ = lambda key: get_text(key, i18n_lang)

    user_bot, admin = await require_bot(callback, state, "stats", i18n_lang=i18n_lang)
    if not user_bot:
        return

    async with async_session() as session:
        stats = await get_admin_stats(session, user_bot.id)

    def fmt(n: float) -> str:
        return f"{n:,.0f}".replace(",", " ")

    total_users = stats["total_users"]
    total_payments = stats["total_payments"]
    conversion = round(total_payments / total_users * 100) if total_users > 0 else 0
    avg_check = stats["total_revenue"] / total_payments if total_payments > 0 else 0

    text = _("stats_header").format(username=user_bot.bot_username)

    text += _("revenue_header")
    text += _("revenue_today").format(amount=fmt(stats['today_revenue']))
    text += _("revenue_month").format(amount=fmt(stats['month_revenue']))
    text += _("revenue_total").format(amount=fmt(stats['total_revenue']))

    text += _("users_stats_header")
    text += _("users_total").format(count=total_users)
    text += _("users_active_subs").format(count=stats['active_subs'])
    text += _("users_conversion").format(percent=conversion)

    text += _("payments_stats_header")
    text += _("payments_approved").format(count=total_payments)
    text += _("payments_pending").format(count=stats['pending_payments'])
    text += _("payments_rejected").format(count=stats['rejected_payments'])
    text += _("payments_avg_check").format(amount=fmt(avg_check))

    if stats["expiring_soon"] > 0:
        text += _("warning_expiring").format(count=stats['expiring_soon'])

    if stats["pending_payments"] > 0:
        text += _("warning_pending_payments").format(count=stats['pending_payments'])

    await callback.message.edit_text(text, reply_markup=back_bot_kb(lang=i18n_lang))
    await callback.answer()
