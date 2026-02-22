from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        Index("ix_subscriptions_expires_status", "expires_at", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    end_user_id: Mapped[int] = mapped_column(ForeignKey("end_users.id"))
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))
    payment_id: Mapped[int] = mapped_column(ForeignKey("payments.id"))
    invite_link: Mapped[str | None] = mapped_column(Text)
    link_used: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))  # None = lifetime
    kicked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="active")  # active / expired / kicked
    notified_3day: Mapped[bool] = mapped_column(Boolean, default=False)
    notified_1day: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    end_user: Mapped["EndUser"] = relationship(back_populates="subscriptions")
    channel: Mapped["Channel"] = relationship(back_populates="subscriptions")
    payment: Mapped["Payment"] = relationship(back_populates="subscription")

    def __repr__(self) -> str:
        return f"<Subscription id={self.id} status={self.status}>"
