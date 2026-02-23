from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UserAdmin, UserBot, EndUser, Payment, Subscription, AdminSubscription
from utils.constants import PaymentStatus, PlanName, SubStatus


async def get_moderator_stats(session: AsyncSession) -> dict:
    """Platform-wide statistics for moderator."""
    total_admins = (await session.execute(
        select(func.count(UserAdmin.id))
    )).scalar()

    total_bots = (await session.execute(
        select(func.count(UserBot.id)).where(UserBot.is_active == True)
    )).scalar()

    total_end_users = (await session.execute(
        select(func.count(EndUser.id))
    )).scalar()

    total_payments = (await session.execute(
        select(func.count(Payment.id)).where(Payment.status == PaymentStatus.APPROVED)
    )).scalar()

    total_revenue = (await session.execute(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.status == PaymentStatus.APPROVED
        )
    )).scalar()

    active_subs = (await session.execute(
        select(func.count(Subscription.id)).where(Subscription.status == SubStatus.ACTIVE)
    )).scalar()

    paid_admins = (await session.execute(
        select(func.count(AdminSubscription.id)).where(
            and_(
                AdminSubscription.status == SubStatus.ACTIVE,
                AdminSubscription.plan != PlanName.FREE,
            )
        )
    )).scalar()

    return {
        "total_admins": total_admins,
        "total_bots": total_bots,
        "total_end_users": total_end_users,
        "total_payments": total_payments,
        "total_revenue": float(total_revenue),
        "active_subscriptions": active_subs,
        "paid_admins": paid_admins,
    }


async def get_admin_stats(session: AsyncSession, user_bot_id: int) -> dict:
    """Statistics for a specific User Admin's bot."""
    total_users = (await session.execute(
        select(func.count(EndUser.id)).where(EndUser.user_bot_id == user_bot_id)
    )).scalar()

    total_payments = (await session.execute(
        select(func.count(Payment.id)).where(
            and_(Payment.user_bot_id == user_bot_id, Payment.status == PaymentStatus.APPROVED)
        )
    )).scalar()

    total_revenue = (await session.execute(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            and_(Payment.user_bot_id == user_bot_id, Payment.status == PaymentStatus.APPROVED)
        )
    )).scalar()

    pending_payments = (await session.execute(
        select(func.count(Payment.id)).where(
            and_(Payment.user_bot_id == user_bot_id, Payment.status == PaymentStatus.PENDING)
        )
    )).scalar()

    return {
        "total_users": total_users,
        "total_payments": total_payments,
        "total_revenue": float(total_revenue),
        "pending_payments": pending_payments,
    }
