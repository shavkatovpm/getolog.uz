from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        Index("ix_payments_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    end_user_id: Mapped[int] = mapped_column(ForeignKey("end_users.id"))
    user_bot_id: Mapped[int] = mapped_column(ForeignKey("user_bots.id"))
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    payment_method: Mapped[str] = mapped_column(String(50), default="card")
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending / approved / rejected
    screenshot_file_id: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    end_user: Mapped["EndUser"] = relationship(back_populates="payments")
    bot: Mapped["UserBot"] = relationship(back_populates="payments")
    channel: Mapped["Channel"] = relationship()
    subscription: Mapped["Subscription | None"] = relationship(
        back_populates="payment", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Payment id={self.id} status={self.status}>"
