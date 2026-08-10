"""Faol obunachi hisoblash, kanal soni va tarif chegaralari bilan bog'liq mantiq.

"Faol" obunachi = hozir status=active bo'lganlar soni (chiqib ketsa o'rin
bo'shaydi) — getolog.uz/price'dagi va'daga mos, barcha tariflar (Bepul ham)
shu bo'yicha hisoblanadi. "Umrbod" obunachi (`count_lifetime_subscribers`) —
bu YERDA "umrbod QO'SHILGAN" (barcha vaqt davomida noyob) obunachilar sonini
bildiradi, faqat Owner panelida ma'lumot uchun ko'rsatiladi, hech qanday
limitga bog'liq emas. Buni ADASHTIRMASLIK kerak `SubscriptionPlan.is_lifetime`
bilan — bu esa obunachi BIR MARTA to'lab MUDDATSIZ (hech qachon tugamaydigan)
tarif sotib olganini bildiradi, quyida `count_billable_subscribers`da hisobga
olinadi.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Admin, Bot, Channel, Subscriber, SubscriberStatus, SubscriptionPlan, TariffPlan

# Umrbod (`is_lifetime`) reja sotib olgan obunachi GETOLOG tarif hisobiga
# (billable) shuncha kun davomida hisoblanadi, keyin hisobdan chiqadi — chunki
# admin ulardan faqat BIR MARTA pul olgan, shuning uchun ularni har oy "faol
# mijoz" deb hisoblab admindan yuqori tarif talab qilish adolatsiz bo'lardi.
LIFETIME_BILLABLE_DAYS = 30


def plan_duration(plan: SubscriptionPlan) -> timedelta | None:
    """Tarifning haqiqiy amal qilish muddati — `None` bo'lsa reja umrbod (cheksiz).

    `duration_minutes` o'rnatilgan bo'lsa (faqat test uchun — masalan 5 daqiqalik
    tarif), o'sha ishlatiladi; aks holda oddiy oylik hisob (`duration_months`)."""
    if plan.is_lifetime:
        return None
    if plan.duration_minutes is not None:
        return timedelta(minutes=plan.duration_minutes)
    return timedelta(days=30 * plan.duration_months)


def plan_duration_label(plan: SubscriptionPlan) -> str:
    """Obunachiga ko'rsatiladigan muddat matni — "1 oy", "Umrbod" yoki (test uchun) "5 daqiqa"."""
    if plan.is_lifetime:
        return "Umrbod"
    if plan.duration_minutes is not None:
        return f"{plan.duration_minutes} daqiqa"
    return f"{plan.duration_months} oy"

# None = cheksiz (Scale tarifida qat'iy limit yo'q, faqat qo'shimcha narxlanadi)
# Raqamlar getolog.uz/price bilan bir xil bo'lishi shart.
TARIFF_LIMITS: dict[TariffPlan, int | None] = {
    TariffPlan.free: 20,
    TariffPlan.minimal: 100,
    TariffPlan.start: 200,
    TariffPlan.pro: 500,
    TariffPlan.business: 1000,
    TariffPlan.scale: None,
}

# Nechta kanal (bot) ulash mumkinligi.
CHANNEL_LIMITS: dict[TariffPlan, int | None] = {
    TariffPlan.free: 1,
    TariffPlan.minimal: 2,
    TariffPlan.start: 2,
    TariffPlan.pro: 3,
    TariffPlan.business: 4,
    TariffPlan.scale: None,
}


async def count_active_subscribers(session: AsyncSession, admin_id: int) -> int:
    """Adminning barcha kanallari bo'yicha hozir faol obunachilar soni."""
    result = await session.execute(
        select(func.count(Subscriber.id))
        .join(Channel, Channel.id == Subscriber.channel_id)
        .join(Bot, Bot.id == Channel.bot_id)
        .where(Bot.admin_id == admin_id, Subscriber.status == SubscriberStatus.active)
    )
    return result.scalar_one()


async def count_billable_subscribers(session: AsyncSession, admin_id: int) -> int:
    """GETOLOG tarif eslatmasi/limiti uchun hisoblanadigan obunachilar soni.

    Oddiy (davriy) obunachilar to'liq hisoblanadi. Umrbod (`end_date is None`)
    obunachilar esa faqat qo'shilgandan keyingi birinchi `LIFETIME_BILLABLE_DAYS`
    kun davomida hisoblanadi — shundan keyin ular kanalda/guruhda haqiqatan ham
    qolsa-da, tarif hisobiga kirmaydi (izoh uchun fayl boshiga qarang)."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=LIFETIME_BILLABLE_DAYS)
    result = await session.execute(
        select(func.count(Subscriber.id))
        .join(Channel, Channel.id == Subscriber.channel_id)
        .join(Bot, Bot.id == Channel.bot_id)
        .where(
            Bot.admin_id == admin_id,
            Subscriber.status == SubscriberStatus.active,
            or_(Subscriber.end_date.is_not(None), Subscriber.joined_at > cutoff),
        )
    )
    return result.scalar_one()


async def count_lifetime_subscribers(session: AsyncSession, admin_id: int) -> int:
    """Adminning umrbod qo'shgan noyob obunachilari soni (faqat Owner panelida
    ma'lumot sifatida ko'rsatiladi — limitga ta'sir qilmaydi)."""
    result = await session.execute(
        select(func.count(func.distinct(Subscriber.user_id)))
        .join(Channel, Channel.id == Subscriber.channel_id)
        .join(Bot, Bot.id == Channel.bot_id)
        .where(Bot.admin_id == admin_id)
    )
    return result.scalar_one()


async def count_channels(session: AsyncSession, admin_id: int) -> int:
    """Adminning barcha botlari bo'yicha ulangan (bazada qayd etilgan) kanallar soni."""
    result = await session.execute(
        select(func.count(Channel.id))
        .join(Bot, Bot.id == Channel.bot_id)
        .where(Bot.admin_id == admin_id)
    )
    return result.scalar_one()


async def can_add_channel(session: AsyncSession, admin: Admin) -> bool:
    """Admin yangi kanal ulay oladimi — joriy tarifidagi kanal soni chegarasiga qarab tekshiradi.

    Bu qat'iy (hard) chegara — obunachi soni limitidan farqli o'laroq, kanal/guruh
    soni undan oshsa yangi kanal ulanmaydi (mavjudlari ishlashda davom etadi)."""
    limit = CHANNEL_LIMITS[admin.tariff_plan]
    if limit is None:
        return True

    current = await count_channels(session, admin.id)
    return current < limit
