from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class EndUser(Base):
    __tablename__ = "end_users"
    __table_args__ = (
        UniqueConstraint("telegram_id", "user_bot_id", name="uq_enduser_bot"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True)
    user_bot_id: Mapped[int] = mapped_column(ForeignKey("user_bots.id"))
    username: Mapped[str | None] = mapped_column(String(255))
    language: Mapped[str] = mapped_column(String(5), default="uz")
    banned: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    bot: Mapped["UserBot"] = relationship(back_populates="end_users")
    payments: Mapped[list["Payment"]] = relationship(
        back_populates="end_user", lazy="selectin"
    )
    subscriptions: Mapped[list["Subscription"]] = relationship(
        back_populates="end_user", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<EndUser id={self.id} tg={self.telegram_id}>"
