from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class BotCollaborator(Base):
    __tablename__ = "bot_collaborators"
    __table_args__ = (
        UniqueConstraint("user_bot_id", "telegram_id", name="uq_collab_bot"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_bot_id: Mapped[int] = mapped_column(ForeignKey("user_bots.id"))
    telegram_id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="admin")
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    bot: Mapped["UserBot"] = relationship(back_populates="collaborators")

    def __repr__(self) -> str:
        return f"<BotCollaborator id={self.id} bot={self.user_bot_id} tg={self.telegram_id}>"
