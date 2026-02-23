from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from utils.constants import SubStatus


class AdminSubscription(Base):
    __tablename__ = "admin_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_admin_id: Mapped[int] = mapped_column(ForeignKey("user_admins.id"))
    plan: Mapped[str] = mapped_column(String(20), default="free")  # free / standard / premium
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))  # None = free
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    status: Mapped[str] = mapped_column(String(20), default=SubStatus.ACTIVE)
    notified_3day: Mapped[bool] = mapped_column(Boolean, default=False)
    notified_1day: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    admin: Mapped["UserAdmin"] = relationship(back_populates="subscriptions")

    def __repr__(self) -> str:
        return f"<AdminSubscription id={self.id} plan={self.plan}>"
