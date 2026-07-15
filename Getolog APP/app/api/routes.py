"""GETOLOG dashboard API — barcha /api/* yo'llar shu yerda ro'yxatdan o'tkaziladi.

Avtorizatsiya middleware (`app/api/middlewares.py`) allaqachon `request["auth"]`
ichiga `{"role": "owner"|"admin", "admin_id": int|None, "telegram_id": int}`
qo'yib beradi (faqat `/api/auth/*` bundan mustasno) — bu yerda faqat rolga
qarab qo'shimcha ega bo'lish (ownership) tekshiruvlari qo'llanadi.
"""

from datetime import date, datetime, timedelta, timezone

from aiohttp import web
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import AuthError, issue_jwt, resolve_role, verify_webapp_init_data
from app.bot import registry
from app.bot.keyboards import TARIFF_LABELS
from app.db.models import (
    Admin,
    Bot as BotModel,
    Channel,
    Payment,
    PaymentStatus,
    Subscriber,
    SubscriberStatus,
    SubscriptionPlan,
    TariffPlan,
)
from app.services.channel_service import create_single_use_invite_link, get_bot_for_channel
from app.services.login_codes import verify_login_code
from app.services.subscription_service import count_active_subscribers, count_lifetime_subscribers

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


async def _get_payment_scoped(session: AsyncSession, request: web.Request, payment_id: int) -> Payment:
    result = await session.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if payment is None:
        raise web.HTTPNotFound(text="To'lov topilmadi")

    auth = request["auth"]
    if auth["role"] == "admin" and payment.admin_id != auth["admin_id"]:
        raise web.HTTPForbidden(text="Bu to'lov sizga tegishli emas")
    return payment


# ---------- Adminlar (faqat owner) ----------


@routes.get("/api/admins")
async def list_admins(request: web.Request) -> web.Response:
    _require_owner(request)
    session: AsyncSession = request["session"]
    result = await session.execute(select(Admin).order_by(Admin.created_at.desc()))
    admins = result.scalars().all()

    data = []
    for admin in admins:
        data.append(
            {
                "id": admin.id,
                "telegram_id": admin.telegram_id,
                "full_name": admin.full_name,
                "tariff_plan": admin.tariff_plan.value,
                "tariff_label": TARIFF_LABELS[admin.tariff_plan],
                "tariff_expiry": admin.tariff_expiry.isoformat() if admin.tariff_expiry else None,
                "active_subscribers": await count_active_subscribers(session, admin.id),
                "lifetime_subscribers": await count_lifetime_subscribers(session, admin.id),
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
    admin.tariff_expiry = date.today() + timedelta(days=30 * months)
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
                    "telegram_id": a.telegram_id,
                    "tariff_label": TARIFF_LABELS[a.tariff_plan],
                    "tariff_expiry": a.tariff_expiry.isoformat(),
                    "days_left": (a.tariff_expiry - date.today()).days,
                }
                for a in expiring_admins
            ],
        }
    )


# ---------- Kanallar ----------


@routes.get("/api/channels")
async def list_channels(request: web.Request) -> web.Response:
    session: AsyncSession = request["session"]
    admin_id = _scoped_admin_id(request)

    query = (
        select(Channel, Admin)
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
    for channel, admin in rows:
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
                "permissions_ok": channel.permissions_ok,
                "payment_instructions": channel.payment_instructions,
                "active_subscribers": active_result.scalar_one(),
                "monthly_revenue": float(revenue_result.scalar_one()),
                "admin_id": admin.id,
                "admin_full_name": admin.full_name,
            }
        )
    return web.json_response(data)


@routes.put("/api/channels/{channel_id}/payment-instructions")
async def set_payment_instructions(request: web.Request) -> web.Response:
    session: AsyncSession = request["session"]
    channel = await _get_channel_scoped(session, request, int(request.match_info["channel_id"]))
    body = await request.json()
    text = (body.get("text") or "").strip()
    if not text:
        raise web.HTTPBadRequest(text="text bo'sh bo'lmasligi kerak")

    channel.payment_instructions = text
    await session.commit()
    return web.json_response({"id": channel.id, "payment_instructions": channel.payment_instructions})


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
                "status": s.status.value,
                "joined_at": s.joined_at.isoformat(),
                "end_date": s.end_date.isoformat(),
            }
            for s in subscribers
        ]
    )


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

    try:
        duration_months = int(body["duration_months"])
        price = float(body["price"])
        if duration_months <= 0 or price <= 0:
            raise ValueError
    except (KeyError, ValueError) as exc:
        raise web.HTTPBadRequest(text="duration_months yoki price noto'g'ri") from exc

    bot_result = await session.execute(select(BotModel).where(BotModel.id == channel.bot_id))
    bot_row = bot_result.scalar_one()

    plan = SubscriptionPlan(
        admin_id=bot_row.admin_id,
        channel_id=channel.id,
        duration_months=duration_months,
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
async def approve_payment(request: web.Request) -> web.Response:
    session: AsyncSession = request["session"]
    payment = await _get_payment_scoped(session, request, int(request.match_info["payment_id"]))

    if payment.status != PaymentStatus.pending:
        raise web.HTTPConflict(text="Bu to'lov allaqachon ko'rib chiqilgan")

    plan_result = await session.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == payment.plan_id))
    plan = plan_result.scalar_one()
    channel, bot = await get_bot_for_channel(session, payment.channel_id)
    if bot is None:
        raise web.HTTPServiceUnavailable(text="Bot hozircha ulanmagan, birozdan keyin urinib ko'ring")

    end_date = date.today() + timedelta(days=30 * plan.duration_months)

    sub_result = await session.execute(
        select(Subscriber).where(
            Subscriber.channel_id == payment.channel_id, Subscriber.user_id == payment.user_id
        )
    )
    subscriber = sub_result.scalar_one_or_none()
    if subscriber is None:
        subscriber = Subscriber(channel_id=payment.channel_id, user_id=payment.user_id, end_date=end_date)
        session.add(subscriber)
    else:
        subscriber.status = SubscriberStatus.active
        subscriber.end_date = end_date
        subscriber.reminder_3d_sent = False
        subscriber.reminder_1d_sent = False
        subscriber.reminder_0d_sent = False

    payment.status = PaymentStatus.approved
    payment.approved_at = datetime.now(timezone.utc)
    await session.commit()

    invite_link = await create_single_use_invite_link(bot, channel.telegram_channel_id)
    await bot.send_message(
        payment.user_id,
        f"To'lovingiz tasdiqlandi ✅\n\nKanalga kirish havolasi (bir martalik, faqat "
        f"siz uchun):\n{invite_link}",
    )
    return web.json_response({"id": payment.id, "status": payment.status.value})


@routes.post("/api/payments/{payment_id}/reject")
async def reject_payment(request: web.Request) -> web.Response:
    session: AsyncSession = request["session"]
    payment = await _get_payment_scoped(session, request, int(request.match_info["payment_id"]))

    if payment.status != PaymentStatus.pending:
        raise web.HTTPConflict(text="Bu to'lov allaqachon ko'rib chiqilgan")

    payment.status = PaymentStatus.rejected
    await session.commit()

    _, bot = await get_bot_for_channel(session, payment.channel_id)
    if bot is not None:
        await bot.send_message(
            payment.user_id, "Afsuski, to'lovingiz tasdiqlanmadi. Admin bilan bog'lanib ko'ring."
        )

    return web.json_response({"id": payment.id, "status": payment.status.value})
