"""GETOLOG dashboard API — barcha /api/* yo'llar shu yerda ro'yxatdan o'tkaziladi.

Avtorizatsiya middleware (`app/api/middlewares.py`) allaqachon `request["auth"]`
ichiga `{"role": "owner"|"admin", "admin_id": int|None, "telegram_id": int}`
qo'yib beradi (faqat `/api/auth/*` bundan mustasno) — bu yerda faqat rolga
qarab qo'shimcha ega bo'lish (ownership) tekshiruvlari qo'llanadi.
"""

import time
from datetime import date, datetime, timedelta, timezone

from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiohttp import web
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import AuthError, issue_jwt, resolve_role, verify_webapp_init_data
from app.bot import registry
from app.bot.keyboards import TARIFF_LABELS
from app.config import settings
from app.db.models import (
    Admin,
    Bot as BotModel,
    Channel,
    ChatType,
    Payment,
    PaymentCard,
    PaymentStatus,
    Subscriber,
    SubscriberStatus,
    SubscriptionPlan,
    TariffPlan,
)
from app.services import payment_service
from app.services.channel_service import get_bot_for_channel, remove_subscriber
from app.services.login_codes import verify_login_code
from app.services.subscription_service import (
    TARIFF_LIMITS,
    count_active_subscribers,
    count_billable_subscribers,
    count_lifetime_subscribers,
)

routes = web.RouteTableDef()


# ---------- Auth ----------


@routes.post("/api/auth/telegram-code")
async def auth_telegram_code(request: web.Request) -> web.Response:
    body = await request.json()
    session: AsyncSession = request["session"]
    code = (body.get("code") or "").strip()

    telegram_id = verify_login_code(code)
    if telegram_id is None:
        raise web.HTTPForbidden(text="Kod noto'g'ri yoki muddati o'tgan")

    try:
        claims = await resolve_role(session, telegram_id)
    except AuthError as exc:
        raise web.HTTPForbidden(text=str(exc)) from exc
    return web.json_response({"token": issue_jwt(claims), **claims})


@routes.post("/api/auth/telegram-webapp")
async def auth_telegram_webapp(request: web.Request) -> web.Response:
    body = await request.json()
    session: AsyncSession = request["session"]
    try:
        telegram_id = verify_webapp_init_data(body.get("init_data", ""))
        claims = await resolve_role(session, telegram_id)
    except AuthError as exc:
        raise web.HTTPForbidden(text=str(exc)) from exc
    return web.json_response({"token": issue_jwt(claims), **claims})


# ---------- Yordamchi funksiyalar ----------


def _require_owner(request: web.Request) -> None:
    if request["auth"]["role"] != "owner":
        raise web.HTTPForbidden(text="Faqat GETOLOG egasi uchun")


def _scoped_admin_id(request: web.Request) -> int | None:
    """owner uchun ?admin_id= parametridan, admin uchun o'z ID'sidan oladi."""
    auth = request["auth"]
    if auth["role"] == "owner":
        raw = request.query.get("admin_id")
        return int(raw) if raw else None
    return auth["admin_id"]


async def _get_channel_scoped(session: AsyncSession, request: web.Request, channel_id: int) -> Channel:
    result = await session.execute(select(Channel).where(Channel.id == channel_id))
    channel = result.scalar_one_or_none()
    if channel is None:
        raise web.HTTPNotFound(text="Kanal topilmadi")

    auth = request["auth"]
    if auth["role"] == "admin":
        bot_result = await session.execute(select(BotModel).where(BotModel.id == channel.bot_id))
        bot_row = bot_result.scalar_one()
        if bot_row.admin_id != auth["admin_id"]:
            raise web.HTTPForbidden(text="Bu kanal sizga tegishli emas")
    return channel


async def _get_subscriber_scoped(session: AsyncSession, request: web.Request, subscriber_id: int) -> Subscriber:
    result = await session.execute(select(Subscriber).where(Subscriber.id == subscriber_id))
    subscriber = result.scalar_one_or_none()
    if subscriber is None:
        raise web.HTTPNotFound(text="Obunachi topilmadi")

    # Egalik tekshiruvi kanal orqali amalga oshadi — `_get_channel_scoped` bilan bir xil qoida.
    await _get_channel_scoped(session, request, subscriber.channel_id)
    return subscriber


async def _get_payment_scoped(session: AsyncSession, request: web.Request, payment_id: int) -> Payment:
    result = await session.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if payment is None:
        raise web.HTTPNotFound(text="To'lov topilmadi")

    auth = request["auth"]
    if auth["role"] == "admin" and payment.admin_id != auth["admin_id"]:
        raise web.HTTPForbidden(text="Bu to'lov sizga tegishli emas")
    return payment


async def _get_bot_scoped(session: AsyncSession, request: web.Request, bot_id: int) -> BotModel:
    result = await session.execute(select(BotModel).where(BotModel.id == bot_id))
    bot_row = result.scalar_one_or_none()
    if bot_row is None or bot_row.is_main:
        raise web.HTTPNotFound(text="Bot topilmadi")

    auth = request["auth"]
    if auth["role"] == "admin" and bot_row.admin_id != auth["admin_id"]:
        raise web.HTTPForbidden(text="Bu bot sizga tegishli emas")
    return bot_row


# ---------- Men (joriy foydalanuvchi) ----------


@routes.get("/api/me")
async def get_me(request: web.Request) -> web.Response:
    auth = request["auth"]
    if auth["role"] != "admin":
        return web.json_response(
            {
                "tariff_plan": None,
                "tariff_label": None,
                "tariff_expiry": None,
                "tariff_started_at": None,
                "subscriber_count": None,
                "subscriber_limit": None,
                "limit_exceeded_at": None,
            }
        )

    session: AsyncSession = request["session"]
    result = await session.execute(select(Admin).where(Admin.id == auth["admin_id"]))
    admin = result.scalar_one()
    return web.json_response(
        {
            "tariff_plan": admin.tariff_plan.value,
            "tariff_label": TARIFF_LABELS[admin.tariff_plan],
            "tariff_expiry": admin.tariff_expiry.isoformat() if admin.tariff_expiry else None,
            "tariff_started_at": admin.tariff_started_at.isoformat() if admin.tariff_started_at else None,
            # GETOLOG tarif eslatmasi shu songa qarab ishlaydi — umrbod reja sotib
            # olganlar faqat birinchi 30 kun hisoblanadi (`count_billable_subscribers`),
            # shuning uchun bu yerda ATAYLAB haqiqiy headcount emas, shu funksiya ishlatiladi.
            "subscriber_count": await count_billable_subscribers(session, admin.id),
            "subscriber_limit": TARIFF_LIMITS[admin.tariff_plan],
            "limit_exceeded_at": admin.limit_exceeded_at.isoformat() if admin.limit_exceeded_at else None,
        }
    )


# ---------- Adminlar (faqat owner) ----------


@routes.get("/api/admins")
async def list_admins(request: web.Request) -> web.Response:
    """Owner paneli uchun adminlarning to'liq kesimi: tarifi, obunachi soni va
    har biriga ulangan botlar (username + kanal + huquqlar + daromad).

    Botlar/obunachilar/to'lovlar bo'yicha agregatlar admin sonidan qat'i nazar
    uchta so'rovda olinadi (har admin uchun alohida so'rov yuborilmaydi).
    """
    _require_owner(request)
    session: AsyncSession = request["session"]
    result = await session.execute(select(Admin).order_by(Admin.created_at.desc()))
    admins = result.scalars().all()

    # Bot -> kanal (LEFT JOIN: kanal hali ulanmagan bot ham ko'rinishi kerak)
    bot_rows = (
        await session.execute(
            select(BotModel, Channel)
            .outerjoin(Channel, Channel.bot_id == BotModel.id)
            .where(BotModel.is_main.is_(False), BotModel.admin_id.isnot(None))
            .order_by(BotModel.id)
        )
    ).all()

    active_by_channel = dict(
        (
            await session.execute(
                select(Subscriber.channel_id, func.count(Subscriber.id))
                .where(Subscriber.status == SubscriberStatus.active)
                .group_by(Subscriber.channel_id)
            )
        ).all()
    )
    revenue_by_channel = dict(
        (
            await session.execute(
                select(Payment.channel_id, func.coalesce(func.sum(Payment.amount), 0))
                .where(
                    Payment.status == PaymentStatus.approved,
                    Payment.approved_at >= datetime.now(timezone.utc) - timedelta(days=30),
                )
                .group_by(Payment.channel_id)
            )
        ).all()
    )

    bots_by_admin: dict[int, list[dict]] = {}
    for bot_row, channel in bot_rows:
        bots_by_admin.setdefault(bot_row.admin_id, []).append(
            {
                "id": bot_row.id,
                "username": bot_row.username,
                "channel_id": channel.id if channel else None,
                "channel_title": channel.title if channel else None,
                "chat_type": channel.chat_type.value if channel else None,
                "permissions_ok": channel.permissions_ok if channel else None,
                "active_subscribers": active_by_channel.get(channel.id, 0) if channel else 0,
                "revenue_30d": float(revenue_by_channel.get(channel.id, 0)) if channel else 0.0,
            }
        )

    data = []
    for admin in admins:
        bots = bots_by_admin.get(admin.id, [])
        data.append(
            {
                "id": admin.id,
                "telegram_id": admin.telegram_id,
                "full_name": admin.full_name,
                "username": admin.username,
                "tariff_plan": admin.tariff_plan.value,
                "tariff_label": TARIFF_LABELS[admin.tariff_plan],
                "tariff_expiry": admin.tariff_expiry.isoformat() if admin.tariff_expiry else None,
                "tariff_started_at": (
                    admin.tariff_started_at.isoformat() if admin.tariff_started_at else None
                ),
                "subscriber_limit": TARIFF_LIMITS.get(admin.tariff_plan),
                "limit_exceeded_at": (
                    admin.limit_exceeded_at.isoformat() if admin.limit_exceeded_at else None
                ),
                "active_subscribers": await count_active_subscribers(session, admin.id),
                "lifetime_subscribers": await count_lifetime_subscribers(session, admin.id),
                "revenue_30d": sum(b["revenue_30d"] for b in bots),
                "bots": bots,
                "created_at": admin.created_at.isoformat(),
            }
        )
    return web.json_response(data)


@routes.post("/api/admins/{admin_id}/tariff")
async def set_admin_tariff(request: web.Request) -> web.Response:
    _require_owner(request)
    session: AsyncSession = request["session"]
    admin_id = int(request.match_info["admin_id"])
    body = await request.json()

    try:
        plan = TariffPlan(body["tariff_plan"])
        months = int(body["months"])
        if months <= 0:
            raise ValueError
    except (KeyError, ValueError) as exc:
        raise web.HTTPBadRequest(text="tariff_plan yoki months noto'g'ri") from exc

    result = await session.execute(select(Admin).where(Admin.id == admin_id))
    admin = result.scalar_one_or_none()
    if admin is None:
        raise web.HTTPNotFound(text="Admin topilmadi")

    admin.tariff_plan = plan
    admin.tariff_started_at = date.today()
    admin.tariff_expiry = date.today() + timedelta(days=30 * months)
    # Tarif oshirilgani uchun oldingi limit-eslatmasi (agar bo'lsa) endi ahamiyatsiz —
    # yangi tarifda qayta hisoblanadi (`_check_tariff_limits`).
    admin.limit_exceeded_at = None
    if plan != TariffPlan.free:
        # Bir marta yoqilgach hech qachon o'chirilmaydi — keyinchalik tarif tugasa
        # yoki Bepulga tushirilsa ham brend qaytib chiqmaydi (`shows_branding`).
        admin.ever_paid = True
    await session.commit()

    main_bot = registry.get_main_bot()
    await main_bot.send_message(
        admin.telegram_id,
        f"Sizga {TARIFF_LABELS[plan]} tarifi {admin.tariff_expiry.strftime('%d.%m.%Y')} "
        "sanagacha faollashtirildi 🎉",
    )

    return web.json_response(
        {"id": admin.id, "tariff_plan": admin.tariff_plan.value, "tariff_expiry": admin.tariff_expiry.isoformat()}
    )


@routes.get("/api/stats/overview")
async def stats_overview(request: web.Request) -> web.Response:
    _require_owner(request)
    session: AsyncSession = request["session"]

    total_admins = (await session.execute(select(func.count(Admin.id)))).scalar_one()
    total_channels = (await session.execute(select(func.count(Channel.id)))).scalar_one()
    total_active = (
        await session.execute(
            select(func.count(Subscriber.id)).where(Subscriber.status == SubscriberStatus.active)
        )
    ).scalar_one()
    total_revenue_30d = (
        await session.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.status == PaymentStatus.approved,
                Payment.approved_at >= datetime.now(timezone.utc) - timedelta(days=30),
            )
        )
    ).scalar_one()

    # GETOLOG'ning o'z tarifi 3 kun ichida tugaydigan adminlar — owner'ga
    # kimga murojaat qilish kerakligini ko'rsatish uchun.
    soon = date.today() + timedelta(days=3)
    expiring_result = await session.execute(
        select(Admin)
        .where(Admin.tariff_expiry.isnot(None), Admin.tariff_expiry <= soon)
        .order_by(Admin.tariff_expiry.asc())
    )
    expiring_admins = expiring_result.scalars().all()

    return web.json_response(
        {
            "total_admins": total_admins,
            "total_channels": total_channels,
            "total_active_subscribers": total_active,
            "total_revenue_30d": float(total_revenue_30d),
            "expiring_admins": [
                {
                    "id": a.id,
                    "full_name": a.full_name,
                    "username": a.username,
                    "telegram_id": a.telegram_id,
                    "tariff_label": TARIFF_LABELS[a.tariff_plan],
                    "tariff_expiry": a.tariff_expiry.isoformat(),
                    "days_left": (a.tariff_expiry - date.today()).days,
                }
                for a in expiring_admins
            ],
        }
    )


# ---------- Botlar ----------


@routes.get("/api/bots")
async def list_bots(request: web.Request) -> web.Response:
    session: AsyncSession = request["session"]
    admin_id = _scoped_admin_id(request)

    query = select(BotModel).where(BotModel.is_main.is_(False))
    if admin_id is not None:
        query = query.where(BotModel.admin_id == admin_id)
    elif request["auth"]["role"] != "owner":
        raise web.HTTPForbidden(text="admin_id kerak")

    result = await session.execute(query.order_by(BotModel.id))
    bots = result.scalars().all()

    data = []
    for bot_row in bots:
        channel_result = await session.execute(select(Channel).where(Channel.bot_id == bot_row.id))
        channel = channel_result.scalar_one_or_none()
        data.append(
            {
                "id": bot_row.id,
                "username": bot_row.username,
                "channel_id": channel.id if channel else None,
                "channel_title": channel.title if channel else None,
                "chat_type": channel.chat_type.value if channel else None,
                "permissions_ok": channel.permissions_ok if channel else None,
            }
        )
    return web.json_response(data)


@routes.delete("/api/bots/{bot_id}")
async def delete_bot(request: web.Request) -> web.Response:
    """Botni butunlay uzadi: webhookni bekor qiladi, registrdan chiqaradi va bazadagi
    barcha bog'liq ma'lumotlarni (kanal, obunachilar, tarif rejalari, to'lovlar) o'chiradi.
    """
    session: AsyncSession = request["session"]
    bot_row = await _get_bot_scoped(session, request, int(request.match_info["bot_id"]))

    channel_result = await session.execute(select(Channel).where(Channel.bot_id == bot_row.id))
    channel = channel_result.scalar_one_or_none()
    if channel is not None:
        await session.execute(delete(Payment).where(Payment.channel_id == channel.id))
        await session.execute(delete(Subscriber).where(Subscriber.channel_id == channel.id))
        await session.execute(delete(SubscriptionPlan).where(SubscriptionPlan.channel_id == channel.id))
        await session.execute(delete(PaymentCard).where(PaymentCard.channel_id == channel.id))
        await session.delete(channel)

    live_bot = registry.get_bot_by_telegram_id(bot_row.telegram_bot_id)
    if live_bot is not None:
        try:
            await live_bot.delete_webhook()
        except TelegramAPIError:
            pass
        await live_bot.session.close()
        registry.unregister_bot(live_bot)

    await session.delete(bot_row)
    await session.commit()
    return web.Response(status=204)


# ---------- Kanallar ----------


@routes.get("/api/channels")
async def list_channels(request: web.Request) -> web.Response:
    session: AsyncSession = request["session"]
    admin_id = _scoped_admin_id(request)

    query = (
        select(Channel, Admin, BotModel)
        .join(BotModel, BotModel.id == Channel.bot_id)
        .join(Admin, Admin.id == BotModel.admin_id)
    )
    if admin_id is not None:
        query = query.where(BotModel.admin_id == admin_id)
    elif request["auth"]["role"] != "owner":
        raise web.HTTPForbidden(text="admin_id kerak")

    result = await session.execute(query)
    rows = result.all()

    data = []
    for channel, admin, bot_row in rows:
        active_result = await session.execute(
            select(func.count(Subscriber.id)).where(
                Subscriber.channel_id == channel.id, Subscriber.status == SubscriberStatus.active
            )
        )
        revenue_result = await session.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.channel_id == channel.id,
                Payment.status == PaymentStatus.approved,
                Payment.approved_at >= datetime.now(timezone.utc) - timedelta(days=30),
            )
        )
        data.append(
            {
                "id": channel.id,
                "title": channel.title,
                "chat_type": channel.chat_type.value,
                "permissions_ok": channel.permissions_ok,
                "welcome_message": channel.welcome_message,
                "active_subscribers": active_result.scalar_one(),
                "monthly_revenue": float(revenue_result.scalar_one()),
                "bot_username": bot_row.username,
                "admin_id": admin.id,
                "admin_full_name": admin.full_name,
                "admin_username": admin.username,
                "admin_telegram_id": admin.telegram_id,
            }
        )
    return web.json_response(data)


@routes.get("/api/channels/{channel_id}/growth")
async def channel_growth(request: web.Request) -> web.Response:
    """Obunachilarning kanalga qo'shilish sanalari — dashboard'da o'sib boruvchi
    (kumulyativ) grafik chizish uchun. Har bir obunachi faqat bitta marta —
    birinchi qo'shilgan kunida — hisobga olinadi (`joined_at` yangilanmaydi,
    faqat `end_date` uzaytiriladi), shuning uchun bu ro'yxat haqiqiy "yangi
    qo'shilish" hodisalarini bildiradi, hozir faolligidan qat'i nazar."""
    session: AsyncSession = request["session"]
    channel = await _get_channel_scoped(session, request, int(request.match_info["channel_id"]))

    result = await session.execute(
        select(Subscriber.joined_at).where(Subscriber.channel_id == channel.id)
    )
    joins = [row[0].date().isoformat() for row in result.all()]

    return web.json_response(
        {
            "channel_created_at": channel.created_at.date().isoformat(),
            "joins": joins,
        }
    )


@routes.put("/api/channels/{channel_id}/welcome-message")
async def set_welcome_message(request: web.Request) -> web.Response:
    """Obunachi shaxsiy botga /start bosganda ko'radigan matnni admin shu yerdan
    tahrirlaydi (`app/bot/handlers/subscriber_flow.py:subscriber_start`)."""
    session: AsyncSession = request["session"]
    channel = await _get_channel_scoped(session, request, int(request.match_info["channel_id"]))
    body = await request.json()

    text = (body.get("text") or "").strip()
    channel.welcome_message = text or None
    await session.commit()
    return web.json_response({"id": channel.id, "welcome_message": channel.welcome_message})


async def _get_payment_card_scoped(
    session: AsyncSession, request: web.Request, card_id: int
) -> PaymentCard:
    result = await session.execute(select(PaymentCard).where(PaymentCard.id == card_id))
    card = result.scalar_one_or_none()
    if card is None:
        raise web.HTTPNotFound(text="Karta topilmadi")

    # Egalik tekshiruvi kanal orqali amalga oshadi — `_get_channel_scoped` bilan bir xil qoida.
    await _get_channel_scoped(session, request, card.channel_id)
    return card


@routes.get("/api/channels/{channel_id}/payment-cards")
async def list_payment_cards(request: web.Request) -> web.Response:
    session: AsyncSession = request["session"]
    channel = await _get_channel_scoped(session, request, int(request.match_info["channel_id"]))

    result = await session.execute(
        select(PaymentCard).where(PaymentCard.channel_id == channel.id).order_by(PaymentCard.id)
    )
    cards = result.scalars().all()
    return web.json_response(
        [
            {
                "id": c.id,
                "bank_name": c.bank_name,
                "card_number": c.card_number,
                "owner_name": c.owner_name,
            }
            for c in cards
        ]
    )


@routes.post("/api/channels/{channel_id}/payment-cards")
async def create_payment_card(request: web.Request) -> web.Response:
    session: AsyncSession = request["session"]
    channel = await _get_channel_scoped(session, request, int(request.match_info["channel_id"]))
    body = await request.json()

    bank_name = (body.get("bank_name") or "").strip()
    card_number = (body.get("card_number") or "").strip()
    owner_name = (body.get("owner_name") or "").strip()
    if not bank_name or not card_number or not owner_name:
        raise web.HTTPBadRequest(text="bank_name, card_number va owner_name to'ldirilishi shart")

    card = PaymentCard(
        channel_id=channel.id, bank_name=bank_name, card_number=card_number, owner_name=owner_name
    )
    session.add(card)
    await session.commit()
    return web.json_response(
        {
            "id": card.id,
            "bank_name": card.bank_name,
            "card_number": card.card_number,
            "owner_name": card.owner_name,
        },
        status=201,
    )


@routes.put("/api/payment-cards/{card_id}")
async def update_payment_card(request: web.Request) -> web.Response:
    session: AsyncSession = request["session"]
    card = await _get_payment_card_scoped(session, request, int(request.match_info["card_id"]))
    body = await request.json()

    if "bank_name" in body:
        card.bank_name = (body["bank_name"] or "").strip()
    if "card_number" in body:
        card.card_number = (body["card_number"] or "").strip()
    if "owner_name" in body:
        card.owner_name = (body["owner_name"] or "").strip()
    if not card.bank_name or not card.card_number or not card.owner_name:
        raise web.HTTPBadRequest(text="bank_name, card_number va owner_name bo'sh bo'lmasligi kerak")

    await session.commit()
    return web.json_response(
        {
            "id": card.id,
            "bank_name": card.bank_name,
            "card_number": card.card_number,
            "owner_name": card.owner_name,
        }
    )


@routes.delete("/api/payment-cards/{card_id}")
async def delete_payment_card(request: web.Request) -> web.Response:
    session: AsyncSession = request["session"]
    card = await _get_payment_card_scoped(session, request, int(request.match_info["card_id"]))
    await session.delete(card)
    await session.commit()
    return web.Response(status=204)


@routes.get("/api/channels/{channel_id}/subscribers")
async def list_subscribers(request: web.Request) -> web.Response:
    session: AsyncSession = request["session"]
    channel = await _get_channel_scoped(session, request, int(request.match_info["channel_id"]))

    result = await session.execute(
        select(Subscriber).where(Subscriber.channel_id == channel.id).order_by(Subscriber.joined_at.desc())
    )
    subscribers = result.scalars().all()
    return web.json_response(
        [
            {
                "id": s.id,
                "user_id": s.user_id,
                "username": s.username,
                "full_name": s.full_name,
                "status": s.status.value,
                "joined_at": s.joined_at.isoformat(),
                "end_date": s.end_date.isoformat() if s.end_date else None,
            }
            for s in subscribers
        ]
    )


@routes.put("/api/subscribers/{subscriber_id}")
async def update_subscriber(request: web.Request) -> web.Response:
    """Admin obunachining tugash sanasini qo'lda o'zgartiradi (uzaytirish/qisqartirish
    yoki umrbodga o'tkazish). Faqat FAOL obunachi uchun — o'chirilgan/muddati
    tugaganlarni qayta faollashtirish alohida amal (qayta taklif havolasi kerak
    bo'lardi), bu yerda qamrovga kirmaydi. Sana o'tmishga o'rnatilsa, obunachi
    navbatdagi scheduler tsiklida (`_kick_expired_subscribers`) avtomatik chiqariladi
    — bu yerda alohida Telegram chaqiruvi shart emas."""
    session: AsyncSession = request["session"]
    subscriber = await _get_subscriber_scoped(session, request, int(request.match_info["subscriber_id"]))

    if subscriber.status != SubscriberStatus.active:
        raise web.HTTPBadRequest(text="Faqat faol obunachining muddatini o'zgartirish mumkin")

    body = await request.json()
    if "end_date" not in body:
        raise web.HTTPBadRequest(text="end_date kerak")

    raw = body["end_date"]
    if raw is None:
        subscriber.end_date = None
    else:
        try:
            subscriber.end_date = datetime.fromisoformat(raw)
        except ValueError as exc:
            raise web.HTTPBadRequest(text="end_date noto'g'ri formatda") from exc

    # Muddat qo'lda o'zgartirilgani uchun eslatmalar yangi sanaga nisbatan qayta yuborilsin.
    subscriber.reminder_3d_sent = False
    subscriber.reminder_1d_sent = False
    subscriber.reminder_0d_sent = False
    await session.commit()

    return web.json_response(
        {"id": subscriber.id, "end_date": subscriber.end_date.isoformat() if subscriber.end_date else None}
    )


@routes.post("/api/subscribers/{subscriber_id}/remove")
async def remove_subscriber_route(request: web.Request) -> web.Response:
    """Admin obunachini qo'lda kanal/guruhdan chiqaradi — muddatini kutmasdan."""
    session: AsyncSession = request["session"]
    subscriber = await _get_subscriber_scoped(session, request, int(request.match_info["subscriber_id"]))

    if subscriber.status != SubscriberStatus.active:
        raise web.HTTPBadRequest(text="Bu obunachi allaqachon faol emas")

    channel, bot = await get_bot_for_channel(session, subscriber.channel_id)
    if bot is None:
        raise web.HTTPServiceUnavailable(text="Bot hozircha ulanmagan, birozdan keyin urinib ko'ring")

    try:
        await remove_subscriber(bot, channel.telegram_channel_id, subscriber.user_id)
    except TelegramBadRequest as exc:
        # Obunachi allaqachon kanal/guruhda emas (masalan o'zi chiqib ketgan) —
        # bu ham "chiqarilgan" holat bilan bir xil natija, xato emas.
        if "USER_NOT_PARTICIPANT" not in str(exc):
            raise web.HTTPBadGateway(text="Telegram orqali chiqarib bo'lmadi") from exc
    except TelegramAPIError as exc:
        raise web.HTTPBadGateway(text="Telegram orqali chiqarib bo'lmadi") from exc

    subscriber.status = SubscriberStatus.removed
    await session.commit()

    kind = "guruhdan" if channel.chat_type == ChatType.group else "kanaldan"
    try:
        await bot.send_message(
            subscriber.user_id,
            f"Siz admin tomonidan «{channel.title}» {kind} chiqarildingiz.",
        )
    except TelegramAPIError:
        pass

    return web.json_response({"id": subscriber.id, "status": subscriber.status.value})


# ---------- Tarif rejalari ----------


@routes.get("/api/plans")
async def list_plans(request: web.Request) -> web.Response:
    session: AsyncSession = request["session"]
    channel_id = request.query.get("channel_id")
    if not channel_id:
        raise web.HTTPBadRequest(text="channel_id kerak")

    channel = await _get_channel_scoped(session, request, int(channel_id))
    result = await session.execute(select(SubscriptionPlan).where(SubscriptionPlan.channel_id == channel.id))
    plans = result.scalars().all()
    return web.json_response(
        [
            {
                "id": p.id,
                "duration_months": p.duration_months,
                "duration_minutes": p.duration_minutes,
                "is_lifetime": p.is_lifetime,
                "price": float(p.price),
                "currency": p.currency,
                "active": p.active,
            }
            for p in plans
        ]
    )


@routes.post("/api/plans")
async def create_plan(request: web.Request) -> web.Response:
    session: AsyncSession = request["session"]
    body = await request.json()
    channel_id = body.get("channel_id")
    if not channel_id:
        raise web.HTTPBadRequest(text="channel_id kerak")
    channel = await _get_channel_scoped(session, request, int(channel_id))

    is_lifetime = bool(body.get("is_lifetime", False))

    try:
        price = float(body["price"])
        if price <= 0:
            raise ValueError
        duration_months = None
        if not is_lifetime:
            duration_months = int(body["duration_months"])
            if duration_months <= 0:
                raise ValueError
    except (KeyError, ValueError) as exc:
        raise web.HTTPBadRequest(text="duration_months yoki price noto'g'ri") from exc

    # Faqat test uchun: o'rnatilsa, `duration_months` o'rniga shu (juda qisqa)
    # muddat ishlatiladi — oy kutmasdan eslatma/kick oqimini tekshirish uchun.
    duration_minutes = None
    if not is_lifetime and body.get("duration_minutes") is not None:
        try:
            duration_minutes = int(body["duration_minutes"])
            if duration_minutes <= 0:
                raise ValueError
        except ValueError as exc:
            raise web.HTTPBadRequest(text="duration_minutes noto'g'ri") from exc

    bot_result = await session.execute(select(BotModel).where(BotModel.id == channel.bot_id))
    bot_row = bot_result.scalar_one()

    plan = SubscriptionPlan(
        admin_id=bot_row.admin_id,
        channel_id=channel.id,
        duration_months=duration_months,
        duration_minutes=duration_minutes,
        is_lifetime=is_lifetime,
        price=price,
        currency=body.get("currency", "UZS"),
        active=True,
    )
    session.add(plan)
    await session.commit()
    return web.json_response({"id": plan.id}, status=201)


@routes.put("/api/plans/{plan_id}")
async def update_plan(request: web.Request) -> web.Response:
    session: AsyncSession = request["session"]
    plan_id = int(request.match_info["plan_id"])
    result = await session.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    if plan is None:
        raise web.HTTPNotFound(text="Tarif topilmadi")

    auth = request["auth"]
    if auth["role"] == "admin" and plan.admin_id != auth["admin_id"]:
        raise web.HTTPForbidden(text="Bu tarif sizga tegishli emas")

    body = await request.json()
    if "price" in body:
        plan.price = float(body["price"])
    if "active" in body:
        plan.active = bool(body["active"])
    await session.commit()
    return web.json_response({"id": plan.id, "price": float(plan.price), "active": plan.active})


# ---------- To'lovlar ----------


@routes.get("/api/payments")
async def list_payments(request: web.Request) -> web.Response:
    session: AsyncSession = request["session"]
    admin_id = _scoped_admin_id(request)

    query = (
        select(Payment, Channel.title, Admin.full_name)
        .join(Channel, Channel.id == Payment.channel_id)
        .join(Admin, Admin.id == Payment.admin_id)
    )
    if admin_id is not None:
        query = query.where(Payment.admin_id == admin_id)
    elif request["auth"]["role"] != "owner":
        raise web.HTTPForbidden(text="admin_id kerak")

    status_param = request.query.get("status")
    if status_param:
        query = query.where(Payment.status == PaymentStatus(status_param))

    result = await session.execute(query.order_by(Payment.created_at.desc()))
    rows = result.all()
    return web.json_response(
        [
            {
                "id": p.id,
                "channel_id": p.channel_id,
                "channel_title": channel_title,
                "admin_full_name": admin_full_name,
                "user_id": p.user_id,
                "subscriber_username": p.username,
                "subscriber_full_name": p.full_name,
                "amount": float(p.amount),
                "status": p.status.value,
                "created_at": p.created_at.isoformat(),
                "has_receipt": p.receipt_file_id is not None,
            }
            for p, channel_title, admin_full_name in rows
        ]
    )


@routes.get("/api/payments/{payment_id}/receipt")
async def get_receipt(request: web.Request) -> web.StreamResponse:
    session: AsyncSession = request["session"]
    payment = await _get_payment_scoped(session, request, int(request.match_info["payment_id"]))
    if not payment.receipt_file_id:
        raise web.HTTPNotFound(text="Chek rasmi yo'q")

    _, bot = await get_bot_for_channel(session, payment.channel_id)
    if bot is None:
        raise web.HTTPServiceUnavailable(text="Bot hozircha ulanmagan")

    file = await bot.get_file(payment.receipt_file_id)
    buffer = await bot.download_file(file.file_path)
    return web.Response(body=buffer.read(), content_type="image/jpeg")


@routes.post("/api/payments/{payment_id}/approve")
async def approve_payment_route(request: web.Request) -> web.Response:
    session: AsyncSession = request["session"]
    payment = await _get_payment_scoped(session, request, int(request.match_info["payment_id"]))

    try:
        await payment_service.approve_payment(session, payment)
    except payment_service.PaymentReviewError as exc:
        raise web.HTTPConflict(text=str(exc)) from exc

    return web.json_response({"id": payment.id, "status": payment.status.value})


@routes.post("/api/payments/{payment_id}/reject")
async def reject_payment_route(request: web.Request) -> web.Response:
    session: AsyncSession = request["session"]
    payment = await _get_payment_scoped(session, request, int(request.match_info["payment_id"]))

    try:
        await payment_service.reject_payment(session, payment)
    except payment_service.PaymentReviewError as exc:
        raise web.HTTPConflict(text=str(exc)) from exc


# ---------- Public: landing sahifadagi ariza forma ----------

_ARIZA_RATE_LIMIT_SECONDS = 60
_ariza_last_submit: dict[str, float] = {}


def _client_ip(request: web.Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote or "unknown"


@routes.post("/api/public/ariza")
async def submit_ariza(request: web.Request) -> web.Response:
    ip = _client_ip(request)
    now = time.monotonic()
    last = _ariza_last_submit.get(ip)
    if last is not None and now - last < _ARIZA_RATE_LIMIT_SECONDS:
        raise web.HTTPTooManyRequests(text="Biroz kutib, keyin qayta urinib ko'ring")

    try:
        body = await request.json()
    except Exception as exc:
        raise web.HTTPBadRequest(text="Noto'g'ri so'rov formati") from exc

    def _clean(key: str, max_len: int, required: bool = True) -> str:
        value = str(body.get(key) or "").strip()
        if required and not value:
            raise web.HTTPBadRequest(text=f"{key} to'ldirilishi shart")
        return value[:max_len]

    full_name = _clean("full_name", 120)
    phone_number = _clean("phone_number", 20)
    telegram_username = _clean("telegram_username", 60)
    channel_topic = _clean("channel_topic", 120)
    subscriber_count = _clean("subscriber_count", 20, required=False)
    message = _clean("message", 2000, required=False)

    if not telegram_username.startswith("@"):
        telegram_username = f"@{telegram_username}"

    subscriber_display = subscriber_count or "ko'rsatilmagan"
    message_display = message or "ko'rsatilmagan"
    text = (
        "📥 Yangi ariza tushdi\n\n"
        f"Ism: {full_name}\n"
        f"Telefon: {phone_number}\n"
        f"Telegram: {telegram_username}\n"
        f"Kanal mavzusi: {channel_topic}\n"
        f"Obunachilar soni: {subscriber_display}\n\n"
        f"Xabar:\n{message_display}"
    )

    main_bot = registry.get_main_bot()
    try:
        await main_bot.send_message(settings.owner_telegram_id, text)
    except TelegramAPIError as exc:
        raise web.HTTPInternalServerError(text="Xabar yuborilmadi, birozdan keyin qayta urinib ko'ring") from exc

    _ariza_last_submit[ip] = now
    return web.json_response({"ok": True})

    return web.json_response({"id": payment.id, "status": payment.status.value})
