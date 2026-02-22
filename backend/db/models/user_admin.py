from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class UserAdmin(Base):
    __tablename__ = "user_admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(255))
    language: Mapped[str] = mapped_column(String(5), default="uz")
    banned: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    bots: Mapped[list["UserBot"]] = relationship(back_populates="admin", lazy="selectin")
    subscriptions: Mapped[list["AdminSubscription"]] = relationship(
        back_populates="admin", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<UserAdmin id={self.id} tg={self.telegram_id}>"
