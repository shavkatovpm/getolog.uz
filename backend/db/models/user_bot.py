from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class UserBot(Base):
    __tablename__ = "user_bots"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_admin_id: Mapped[int] = mapped_column(ForeignKey("user_admins.id"))
    bot_token: Mapped[str] = mapped_column(Text)  # Fernet encrypted
    bot_username: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    welcome_message: Mapped[str | None] = mapped_column(
        Text,
        default="Assalomu alaykum! Pullik kanalga kirish uchun quyidagi tugmani bosing.",
    )
    payment_method: Mapped[str] = mapped_column(String(50), default="card")
    card_number: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    admin: Mapped["UserAdmin"] = relationship(back_populates="bots")
    channels: Mapped[list["Channel"]] = relationship(
        back_populates="bot", lazy="selectin"
    )
    end_users: Mapped[list["EndUser"]] = relationship(
        back_populates="bot", lazy="selectin"
    )
    payments: Mapped[list["Payment"]] = relationship(
        back_populates="bot", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<UserBot id={self.id} @{self.bot_username}>"
