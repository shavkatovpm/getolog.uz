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
    minimal = "minimal"
    start = "start"
    pro = "pro"
    business = "business"
    scale = "scale"


class ChatType(str, enum.Enum):
    """Bot ulangan Telegram chat turi — obuna/kirish nazorati mantig'i
    ikkalasi uchun ham bir xil, faqat kerakli admin huquqlari farq qiladi
    (guruhda `can_post_messages`/`can_delete_messages` ma'nosiz)."""

    channel = "channel"
    group = "group"


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
    # Telegram username (@ belgisisiz) — Owner panelida admin(lar)ni aniqlash uchun
    # ko'rsatiladi. Har /start bosilganda yangilanadi (username o'zgarishi mumkin).
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(8), default="uz")

    # GETOLOG'ning o'z SaaS tarifi — MVP'da faqat owner tomonidan qo'lda beriladi
    tariff_plan: Mapped[TariffPlan] = mapped_column(
        Enum(TariffPlan, name="tariff_plan"), default=TariffPlan.free
    )
    tariff_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)
    # Joriy tarif davri qachon boshlanganini bildiradi (`set_admin_tariff`da
    # yangi tarif berilganda "bugun"ga o'rnatiladi) — kun bo'yicha necha foizi
    # o'tganini hisoblash uchun kerak (dashboard navbar'idagi progress-bar).
    tariff_started_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Faol obunachilar soni joriy tarif limitidan oshib ketgan kun — FAQAT
    # ESLATMA uchun (bot bloklanmaydi): dashboard'da ogohlantirish shu asosida
    # ko'rsatiladi va limitdan birinchi marta oshganda adminga bir martalik
    # xabar yuboriladi. Obunachi soni limit ostiga qaytganda (yoki tarif
    # oshirilganda) `None`ga qaytariladi.
    limit_exceeded_at: Mapped[date | None] = mapped_column(Date, nullable=True)

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

    # Bot admin qilib qo'shilgan, lekin tarif limiti tufayli hali ULANMAGAN
    # kanal/guruhning Telegram ID'si. Telegram `my_chat_member` hodisasini faqat
    # BIR MARTA (status o'zgarganda) yuboradi va "bot qaysi chatlarda admin"
    # degan so'rov Bot API'da yo'q — shuning uchun rad etilgan chatni shu yerda
    # eslab qolamiz. Admin joy bo'shatib "✅ Admin qildim"ni bosganda shu ID
    # bo'yicha jonli tekshirib ulanadi (`_retry_pending_channels`), aks holda
    # u botni kanaldan chiqarib qayta qo'shishga majbur bo'lardi.
    pending_chat_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    admin: Mapped["Admin | None"] = relationship(back_populates="bots")
    channels: Mapped[list["Channel"]] = relationship(back_populates="bot")


class Channel(Base):
    """Adminning boti ulangan Telegram kanali yoki yopiq guruhi (`chat_type`)."""

    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Bitta bot faqat bitta kanalni boshqaradi — boshqa kanal uchun admin
    # yangi bot ulashi kerak (bittalik shu `unique=True` bilan bazada ham
    # majburlanadi, `on_bot_status_changed_in_chat` ikkinchi kanalni rad etadi).
    bot_id: Mapped[int] = mapped_column(ForeignKey("bots.id"), unique=True)
    telegram_channel_id: Mapped[int] = mapped_column(BigInteger)
    title: Mapped[str] = mapped_column(String(255))
    chat_type: Mapped[ChatType] = mapped_column(Enum(ChatType, name="chat_type"), default=ChatType.channel)

    # Bot kanalda kerakli admin huquqlariga ega ekani tekshirilganmi
    permissions_ok: Mapped[bool] = mapped_column(Boolean, default=False)

    # Admin dashboard orqali tahrirlaydigan matn — obunachi shaxsiy botga
    # /start bosganda tarif tanlashdan OLDIN shu matn ko'rsatiladi (masalan
    # kanal haqida qisqa ma'lumot). Bo'sh bo'lsa standart matn ishlatiladi.
    welcome_message: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    bot: Mapped["Bot"] = relationship(back_populates="channels")
    subscribers: Mapped[list["Subscriber"]] = relationship(back_populates="channel")
    plans: Mapped[list["SubscriptionPlan"]] = relationship(back_populates="channel")
    payment_cards: Mapped[list["PaymentCard"]] = relationship(back_populates="channel")


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

    # To'lov tasdiqlangan paytdagi Telegram ma'lumotlari (`Payment.username`/
    # `full_name`'dan ko'chiriladi — obunachi bilan alohida so'rovsiz). Telegram
    # username'i bo'lmasligi mumkin, shuning uchun nullable.
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status: Mapped[SubscriberStatus] = mapped_column(
        Enum(SubscriberStatus, name="subscriber_status"), default=SubscriberStatus.active
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # To'liq sana+vaqt — juda qisqa (masalan test uchun daqiqalik) tariflar ham
    # aniq hisoblanishi uchun (faqat "kun" darajasida saqlash yetarli emas).
    # `None` = umrbod (lifetime) obunachi — hech qachon muddati tugamaydi va
    # kanaldan avtomatik chiqarilmaydi (`scheduler._kick_expired_subscribers`
    # va `_send_due_reminders` buni o'tkazib yuboradi).
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Joriy davrning umumiy uzunligi (daqiqada) — eslatmalar qanday chastotada
    # yuborilishini belgilash uchun (masalan oylik tarifda "3 kun/1 kun oldin",
    # juda qisqa test tarifida esa muddatga nisbatan foizli chegaralar
    # ishlatiladi — `app/services/scheduler.py:_reminder_thresholds`).
    duration_minutes: Mapped[int] = mapped_column(default=30 * 24 * 60)

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

    # `is_lifetime=True` bo'lsa `duration_months` e'tiborga olinmaydi (shu
    # sabab nullable) — reja umrbod, obunachi hech qachon chiqarilmaydi.
    duration_months: Mapped[int | None] = mapped_column(nullable=True)
    # Faqat test uchun: o'rnatilsa, `duration_months` o'rniga shu (juda qisqa,
    # masalan 5 daqiqalik) muddat ishlatiladi — eslatma/kick oqimini oy kutmasdan
    # tekshirish uchun (`app/services/subscription_service.py:plan_duration`).
    duration_minutes: Mapped[int | None] = mapped_column(nullable=True)
    is_lifetime: Mapped[bool] = mapped_column(Boolean, default=False)
    price: Mapped[float] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(8), default="UZS")
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    admin: Mapped["Admin"] = relationship(back_populates="subscription_plans")
    channel: Mapped["Channel"] = relationship(back_populates="plans")


class PaymentCard(Base):
    """Admin kanali uchun to'lov qabul qilinadigan bank kartasi. Bitta kanalga
    bir nechta karta biriktirilishi mumkin (masalan Uzcard va Humo alohida) —
    obunachi tarif tanlaganda shu kartalar ro'yxati ko'rsatiladi."""

    __tablename__ = "payment_cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))
    bank_name: Mapped[str] = mapped_column(String(100))
    card_number: Mapped[str] = mapped_column(String(64))
    owner_name: Mapped[str] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    channel: Mapped["Channel"] = relationship(back_populates="payment_cards")


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
    # Chek yuborilgan paytdagi Telegram ma'lumotlari — tasdiqlanganda
    # `Subscriber.username`/`full_name`'ga ko'chiriladi.
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    method: Mapped[str] = mapped_column(String(16), default="manual")
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status"), default=PaymentStatus.pending
    )
    receipt_file_id: Mapped[str | None] = mapped_column(String, nullable=True)

    # Tasdiqlangach yuborilgan "Kanalga kirish" xabarining ID'si — obunachi
    # haqiqatan ham kanalga qo'shilganini Telegram tasdiqlagach (`chat_member`
    # hodisasi), shu xabar "Siz qo'shildingiz ✅"ga tahrirlanadi
    # (`app/bot/handlers/subscriber_flow.py:on_member_joined`).
    invite_message_id: Mapped[int | None] = mapped_column(nullable=True)

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
