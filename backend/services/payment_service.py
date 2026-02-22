from datetime import datetime, timezone

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Payment, EndUser


async def create_payment(
    session: AsyncSession,
    end_user_id: int,
    user_bot_id: int,
    channel_id: int,
    amount: float,
    payment_method: str = "card",
    screenshot_file_id: str | None = None,
) -> Payment:
    payment = Payment(
        end_user_id=end_user_id,
        user_bot_id=user_bot_id,
        channel_id=channel_id,
        amount=amount,
        payment_method=payment_method,
        screenshot_file_id=screenshot_file_id,
    )
    session.add(payment)
    await session.commit()
    return payment


async def approve_payment(session: AsyncSession, payment_id: int) -> Payment | None:
    result = await session.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    if not payment or payment.status != "pending":
        return None

    payment.status = "approved"
    payment.approved_at = datetime.now(timezone.utc)
    await session.commit()
    return payment


async def reject_payment(session: AsyncSession, payment_id: int) -> Payment | None:
    result = await session.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    if not payment or payment.status != "pending":
        return None

    payment.status = "rejected"
    await session.commit()
    return payment


async def get_pending_payments(
    session: AsyncSession, user_bot_id: int
) -> list[Payment]:
    result = await session.execute(
        select(Payment).where(
            and_(
                Payment.user_bot_id == user_bot_id,
                Payment.status == "pending",
            )
        ).order_by(Payment.created_at.desc())
    )
    return list(result.scalars().all())


async def get_payment_by_id(session: AsyncSession, payment_id: int) -> Payment | None:
    result = await session.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    return result.scalar_one_or_none()


async def get_payments_stats(session: AsyncSession, user_bot_id: int) -> dict:
    """Get payment statistics for a bot."""
    # Total approved payments
    result = await session.execute(
        select(
            func.count(Payment.id),
            func.coalesce(func.sum(Payment.amount), 0),
        ).where(
            and_(
                Payment.user_bot_id == user_bot_id,
                Payment.status == "approved",
            )
        )
    )
    row = result.one()

    # Total end users
    users_result = await session.execute(
        select(func.count(EndUser.id)).where(EndUser.user_bot_id == user_bot_id)
    )
    total_users = users_result.scalar()

    return {
        "total_payments": row[0],
        "total_revenue": float(row[1]),
        "total_users": total_users,
    }
