"""Faol obunachi hisoblash, bepul limit va tarif chegarasi bilan bog'liq mantiq.

Muhim: bu yerda ikki xil o'lchov bor va ular chalkashtirilmasligi kerak.
- "Faol" obunachi = hozir status=active bo'lganlar soni (chiqib ketsa o'rin bo'shaydi).
- "Umrbod" obunachi = holatidan qat'i nazar, umuman qo'shilgan noyob user_id soni
  (faqat Bepul tarifning 10 talik limiti uchun ishlatiladi — chiqib ketsa ham
  o'rin qaytmaydi).
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Admin, Bot, Channel, Subscriber, SubscriberStatus, TariffPlan

FREE_LIFETIME_LIMIT = 10

# None = cheksiz (Scale tarifida qat'iy limit yo'q, faqat qo'shimcha narxlanadi)
TARIFF_LIMITS: dict[TariffPlan, int | None] = {
    TariffPlan.free: FREE_LIFETIME_LIMIT,
    TariffPlan.start: 200,
    TariffPlan.pro: 500,
    TariffPlan.business: 1000,
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


async def count_lifetime_subscribers(session: AsyncSession, admin_id: int) -> int:
    """Adminning umrbod qo'shgan noyob obunachilari soni (bepul limit uchun)."""
    result = await session.execute(
        select(func.count(func.distinct(Subscriber.user_id)))
        .join(Channel, Channel.id == Subscriber.channel_id)
        .join(Bot, Bot.id == Channel.bot_id)
        .where(Bot.admin_id == admin_id)
    )
    return result.scalar_one()


async def can_accept_new_subscriber(session: AsyncSession, admin: Admin) -> bool:
    """Admin yangi obunachini qabul qila oladimi — joriy tarifiga qarab tekshiradi."""
    if admin.tariff_plan == TariffPlan.free:
        lifetime = await count_lifetime_subscribers(session, admin.id)
        return lifetime < FREE_LIFETIME_LIMIT

    limit = TARIFF_LIMITS[admin.tariff_plan]
    if limit is None:
        return True

    active = await count_active_subscribers(session, admin.id)
    return active < limit
