from decimal import Decimal

from sqlalchemy import BigInteger, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_bot_id: Mapped[int] = mapped_column(ForeignKey("user_bots.id"))
    telegram_chat_id: Mapped[int] = mapped_column(BigInteger)
    type: Mapped[str] = mapped_column(String(10), default="channel")  # channel / group
    title: Mapped[str | None] = mapped_column(String(255))
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    currency: Mapped[str] = mapped_column(String(10), default="UZS")
    duration_months: Mapped[int] = mapped_column(Integer, default=1)  # 0 = lifetime

    # Relationships
    bot: Mapped["UserBot"] = relationship(back_populates="channels")
    subscriptions: Mapped[list["Subscription"]] = relationship(
        back_populates="channel", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Channel id={self.id} {self.title}>"
