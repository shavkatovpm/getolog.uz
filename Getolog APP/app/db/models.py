"""GETOLOG ma'lumotlar bazasining 7 ta asosiy jadvali.

Muhim qoida: `Subscriber` yozuvi hech qachon o'chirilmaydi — obunachi kanaldan
chiqarilganda ham faqat uning `status` maydoni o'zgaradi. Shu tufayli bitta
jadval ikkita muhim sonni ham beradi: faol obunachilar soni (status=active)
va bepul tarifning umrbod 10 ta limiti (barcha noyob user_id, holatidan qat'i
nazar).
"""

import enum
from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TariffPlan(str, enum.Enum):
    """GETOLOG'ning adminlarga taqdim etadigan o'z SaaS tariflari."""

    free = "free"
    start = "start"
    pro = "pro"
    business = "business"
    scale = "scale"


class SubscriberStatus(str, enum.Enum):
    """Obunachining kanaldagi holati."""

    active = "active"
    expired = "expired"
    removed = "removed"


class PaymentStatus(str, enum.Enum):
    """Obunachi to'lovining holati (MVP'da faqat qo'lda tasdiqlanadi)."""

    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Admin(Base):
    """GETOLOG botidan foydalanadigan kanal admini (mijoz)."""

    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    language: Mapped[str] = mapped_column(String(8), default="uz")

    # GETOLOG'ning o'z SaaS tarifi — MVP'da faqat owner tomonidan qo'lda beriladi
    tariff_plan: Mapped[TariffPlan] = mapped_column(
        Enum(TariffPlan, name="tariff_plan"), default=TariffPlan.free
    )
    tariff_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    bots: Mapped[list["Bot"]] = relationship(back_populates="admin")
    subscription_plans: Mapped[list["SubscriptionPlan"]] = relationship(back_populates="admin")
    settings: Mapped["AdminSettings | None"] = relationship(
        back_populates="admin", uselist=False
    )


class Bot(Base):
    """Telegram bot: yoki GETOLOG bosh boti (is_main=True), yoki adminning
    o'z kanaliga ulangan shaxsiy boti."""

    __tablename__ = "bots"

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id: Mapped[int | None] = mapped_column(ForeignKey("admins.id"), nullable=True)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)

    # Botning Telegram'dagi raqamli ID'si (getMe() dan olinadi). Bu maxfiy emas
    # (tokenning o'zida ham ochiq ko'rinadi), shuning uchun shifrlanmagan holda,
    # tezkor qidiruv uchun saqlanadi — masalan kanalga qo'shilgan botni DB'dan
    # topishda (tokenni qayta-qayta deshifrlashga hojat qolmaydi).
    telegram_bot_id: Mapped[int] = mapped_column(BigInteger, unique=True)

    # Token bazada hech qachon ochiq saqlanmaydi — faqat shifrlangan holda.
    # Fernet shifrlash har safar boshqacha natija beradi (nonce tufayli), shuning
    # uchun bu ustunda unique bo'lishi shart emas — noyoblik `username` orqali
    # ta'minlanadi (Telegram bot username'lari global miqyosda noyob).
    token_encrypted: Mapped[str] = mapped_column(String)
    username: Mapped[str] = mapped_column(String(255), unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    admin: Mapped["Admin | None"] = relationship(back_populates="bots")
    channels: Mapped[list["Channel"]] = relationship(back_populates="bot")


class Channel(Base):
    """Adminning boti ulangan Telegram kanali."""

    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True)
    bot_id: Mapped[int] = mapped_column(ForeignKey("bots.id"))
    telegram_channel_id: Mapped[int] = mapped_column(BigInteger)
    title: Mapped[str] = mapped_column(String(255))

    # Bot kanalda kerakli admin huquqlariga ega ekani tekshirilganmi
    permissions_ok: Mapped[bool] = mapped_column(Boolean, default=False)

    # Admin /narx orqali kiritadigan to'lov rekvizitlari (karta raqami va h.k.) —
    # obunachiga tarif tanlaganda ko'rsatiladi
    payment_instructions: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    bot: Mapped["Bot"] = relationship(back_populates="channels")
    subscribers: Mapped[list["Subscriber"]] = relationship(back_populates="channel")
    plans: Mapped[list["SubscriptionPlan"]] = relationship(back_populates="channel")


class Subscriber(Base):
    """Kanalga bot orqali qo'shilgan obunachi. Yozuv hech qachon o'chirilmaydi,
    faqat `status` o'zgaradi (fayl boshidagi izohga qarang)."""

    __tablename__ = "subscribers"
    __table_args__ = (
        UniqueConstraint("channel_id", "user_id", name="uq_subscriber_channel_user"),
        Index("ix_subscriber_status_end_date", "status", "end_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))
    user_id: Mapped[int] = mapped_column(BigInteger)  # obunachining Telegram ID'si

    status: Mapped[SubscriberStatus] = mapped_column(
        Enum(SubscriberStatus, name="subscriber_status"), default=SubscriberStatus.active
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    end_date: Mapped[date] = mapped_column(Date)

    # Har bir eslatma faqat bir marta yuborilishi uchun (cron qayta ishga
    # tushsa yoki kechiksa ham takror xabar ketmaydi — "catch-up" mantiq shu
    # flag'larga tayanadi)
    reminder_3d_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_1d_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_0d_sent: Mapped[bool] = mapped_column(Boolean, default=False)

    channel: Mapped["Channel"] = relationship(back_populates="subscribers")


class SubscriptionPlan(Base):
    """Adminning o'z kanali uchun belgilagan tarif rejasi
    (masalan: 1 oy — 50 000 so'm)."""

    __tablename__ = "subscription_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id: Mapped[int] = mapped_column(ForeignKey("admins.id"))
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))

    duration_months: Mapped[int] = mapped_column()
    price: Mapped[float] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(8), default="UZS")
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    admin: Mapped["Admin"] = relationship(back_populates="subscription_plans")
    channel: Mapped["Channel"] = relationship(back_populates="plans")


class Payment(Base):
    """Obunachining kanalga kirish uchun to'lovi.
    MVP'da `method` doim "manual" — chek/skrinshot orqali admin qo'lda
    tasdiqlaydi. Payme/Click ulanganda shu jadvalga yangi method qo'shiladi."""

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))
    admin_id: Mapped[int] = mapped_column(ForeignKey("admins.id"))
    plan_id: Mapped[int] = mapped_column(ForeignKey("subscription_plans.id"))
    user_id: Mapped[int] = mapped_column(BigInteger)  # obunachining Telegram ID'si

    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    method: Mapped[str] = mapped_column(String(16), default="manual")
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status"), default=PaymentStatus.pending
    )
    receipt_file_id: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AdminSettings(Base):
    """Admin uchun qo'shimcha sozlamalar. MVP'da bo'sh — kelajakda
    (masalan eslatma matnini moslashtirish) kengaytirish uchun rezerv jadval."""

    __tablename__ = "admin_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id: Mapped[int] = mapped_column(ForeignKey("admins.id"), unique=True)

    admin: Mapped["Admin"] = relationship(back_populates="settings")
