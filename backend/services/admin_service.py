from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UserAdmin, AdminSubscription


async def get_or_create_admin(
    session: AsyncSession,
    telegram_id: int,
    username: str | None = None,
    full_name: str | None = None,
    language: str = "uz",
) -> tuple[UserAdmin, bool]:
    """Get existing admin or create new one. Returns (admin, is_new)."""
    result = await session.execute(
        select(UserAdmin).where(UserAdmin.telegram_id == telegram_id)
    )
    admin = result.scalar_one_or_none()

    if admin:
        # Update info
        admin.username = username
        admin.full_name = full_name
        await session.commit()
        return admin, False

    # Create new admin
    admin = UserAdmin(
        telegram_id=telegram_id,
        username=username,
        full_name=full_name,
        language=language,
    )
    session.add(admin)
    await session.flush()

    # Create free subscription
    free_sub = AdminSubscription(
        user_admin_id=admin.id,
        plan="free",
        status="active",
    )
    session.add(free_sub)
    await session.commit()

    return admin, True


async def get_admin_by_telegram_id(
    session: AsyncSession, telegram_id: int
) -> UserAdmin | None:
    result = await session.execute(
        select(UserAdmin).where(UserAdmin.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def get_active_subscription(
    session: AsyncSession, admin_id: int
) -> AdminSubscription | None:
    result = await session.execute(
        select(AdminSubscription).where(
            AdminSubscription.user_admin_id == admin_id,
            AdminSubscription.status == "active",
        ).order_by(AdminSubscription.started_at.desc())
    )
    return result.scalar_first()


async def get_all_admins(session: AsyncSession) -> list[UserAdmin]:
    result = await session.execute(select(UserAdmin).order_by(UserAdmin.created_at.desc()))
    return list(result.scalars().all())


async def ban_admin(session: AsyncSession, admin_id: int) -> bool:
    result = await session.execute(
        select(UserAdmin).where(UserAdmin.id == admin_id)
    )
    admin = result.scalar_one_or_none()
    if not admin:
        return False
    admin.banned = True
    await session.commit()
    return True


async def unban_admin(session: AsyncSession, admin_id: int) -> bool:
    result = await session.execute(
        select(UserAdmin).where(UserAdmin.id == admin_id)
    )
    admin = result.scalar_one_or_none()
    if not admin:
        return False
    admin.banned = False
    await session.commit()
    return True
