from datetime import datetime, timedelta, timezone

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Subscription, Channel
from utils.constants import SubStatus


async def create_subscription(
    session: AsyncSession,
    end_user_id: int,
    channel_id: int,
    payment_id: int,
    invite_link: str,
    duration_months: int,
) -> Subscription:
    now = datetime.now(timezone.utc)
    expires_at = None
    if duration_months > 0:
        expires_at = now + timedelta(days=30 * duration_months)

    sub = Subscription(
        end_user_id=end_user_id,
        channel_id=channel_id,
        payment_id=payment_id,
        invite_link=invite_link,
        expires_at=expires_at,
    )
    session.add(sub)
    await session.commit()
    return sub


async def mark_link_used(session: AsyncSession, subscription_id: int) -> bool:
    result = await session.execute(
        select(Subscription).where(Subscription.id == subscription_id)
    )
    sub = result.scalar_one_or_none()
    if not sub:
        return False
    sub.link_used = True
    sub.joined_at = datetime.now(timezone.utc)
    await session.commit()
    return True


async def get_active_subscription(
    session: AsyncSession, end_user_id: int, channel_id: int
) -> Subscription | None:
    result = await session.execute(
        select(Subscription).where(
            and_(
                Subscription.end_user_id == end_user_id,
                Subscription.channel_id == channel_id,
                Subscription.status == SubStatus.ACTIVE,
            )
        )
    )
    return result.scalar_one_or_none()


async def get_subscriptions_by_channel(
    session: AsyncSession, channel_id: int
) -> list[Subscription]:
    result = await session.execute(
        select(Subscription).where(Subscription.channel_id == channel_id)
        .order_by(Subscription.created_at.desc())
    )
    return list(result.scalars().all())
