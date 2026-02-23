import logging

from aiogram import Bot
from aiohttp import web

from api.auth import get_authenticated_admin
from core.encryption import decrypt_token
from core.invite_link import create_invite_link
from db.engine import async_session
from services.bot_service import get_bot_by_id
from services.payment_service import (
    approve_payment,
    get_payment_by_id,
    get_pending_payments,
    reject_payment,
)
from services.subscription_service import create_subscription

logger = logging.getLogger(__name__)


async def list_payments(request: web.Request):
    """GET /api/payments"""
    auth = await get_authenticated_admin(request)
    if not auth:
        return web.json_response({"error": "unauthorized"}, status=401)

    admin_id, user_bot_id = auth

    async with async_session() as session:
        pending = await get_pending_payments(session, user_bot_id)
        result = []
        for p in pending:
            result.append({
                "id": p.id,
                "amount": float(p.amount),
                "status": p.status,
                "screenshot_file_id": p.screenshot_file_id,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "end_user": {
                    "id": p.end_user.id,
                    "telegram_id": p.end_user.telegram_id,
                    "username": p.end_user.username,
                },
                "channel": {
                    "id": p.channel.id,
                    "title": p.channel.title,
                },
            })

    return web.json_response({"payments": result})


async def get_screenshot(request: web.Request):
    """GET /api/payments/{id}/screenshot"""
    auth = await get_authenticated_admin(request)
    if not auth:
        return web.json_response({"error": "unauthorized"}, status=401)

    admin_id, user_bot_id = auth
    payment_id = int(request.match_info["id"])

    async with async_session() as session:
        payment = await get_payment_by_id(session, payment_id)
        if not payment or payment.user_bot_id != user_bot_id:
            return web.json_response({"error": "not_found"}, status=404)

        if not payment.screenshot_file_id:
            return web.json_response({"error": "no_screenshot"}, status=404)

        user_bot = await get_bot_by_id(session, user_bot_id)
        token = decrypt_token(user_bot.bot_token)

    bot = Bot(token=token)
    try:
        file = await bot.get_file(payment.screenshot_file_id)
        file_url = f"https://api.telegram.org/file/bot{token}/{file.file_path}"
        return web.json_response({"url": file_url})
    finally:
        await bot.session.close()


async def approve(request: web.Request):
    """POST /api/payments/{id}/approve"""
    auth = await get_authenticated_admin(request)
    if not auth:
        return web.json_response({"error": "unauthorized"}, status=401)

    admin_id, user_bot_id = auth
    payment_id = int(request.match_info["id"])

    async with async_session() as session:
        payment = await get_payment_by_id(session, payment_id)
        if not payment or payment.user_bot_id != user_bot_id:
            return web.json_response({"error": "not_found"}, status=404)

        from utils.constants import PaymentStatus
        if payment.status != PaymentStatus.PENDING:
            return web.json_response({"error": "already_processed"}, status=400)

        channel = payment.channel
        end_user = payment.end_user
        user_bot = await get_bot_by_id(session, user_bot_id)

        # Create invite link BEFORE approving payment
        token = decrypt_token(user_bot.bot_token)
        bot = Bot(token=token)
        try:
            invite_link = await create_invite_link(bot, channel.telegram_chat_id)
        except Exception as e:
            logger.error(f"Failed to create invite link: {e}")
            return web.json_response(
                {"error": "invite_link_failed", "message": "Bot kanalda admin ekanligini tekshiring."},
                status=500,
            )
        finally:
            await bot.session.close()

        # Invite link ready — now approve payment
        payment = await approve_payment(session, payment_id)
        if not payment:
            return web.json_response({"error": "already_processed"}, status=400)

        # Create subscription
        await create_subscription(
            session,
            end_user_id=end_user.id,
            channel_id=channel.id,
            payment_id=payment.id,
            invite_link=invite_link,
            duration_months=channel.duration_months,
        )

    # Notify end user
    notify_failed = False
    bot_manager = request.app.get("bot_manager")
    bot_instance = bot_manager.bots.get(user_bot_id) if bot_manager else None
    if bot_instance:
        try:
            duration_text = {0: "umrbod", 1: "1 oy", 6: "6 oy", 12: "12 oy"}.get(
                channel.duration_months, f"{channel.duration_months} oy"
            )
            await bot_instance.send_message(
                end_user.telegram_id,
                f"✅ <b>To'lov tasdiqlandi!</b>\n\n"
                f"📢 {channel.title}\n"
                f"📅 Muddat: {duration_text}\n\n"
                f"🔗 Kanalga kirish:\n{invite_link}\n\n"
                f"⚠️ Bu link faqat 1 marta ishlaydi!",
            )
        except Exception:
            notify_failed = True

    return web.json_response({"ok": True, "notification_sent": not notify_failed})


async def reject(request: web.Request):
    """POST /api/payments/{id}/reject"""
    auth = await get_authenticated_admin(request)
    if not auth:
        return web.json_response({"error": "unauthorized"}, status=401)

    admin_id, user_bot_id = auth
    payment_id = int(request.match_info["id"])

    async with async_session() as session:
        payment = await get_payment_by_id(session, payment_id)
        if not payment or payment.user_bot_id != user_bot_id:
            return web.json_response({"error": "not_found"}, status=404)

        payment = await reject_payment(session, payment_id)
        if not payment:
            return web.json_response({"error": "already_processed"}, status=400)

        payment = await get_payment_by_id(session, payment_id)
        end_user = payment.end_user
        channel = payment.channel

    # Notify end user
    bot_manager = request.app.get("bot_manager")
    bot_instance = bot_manager.bots.get(user_bot_id) if bot_manager else None
    if bot_instance:
        try:
            await bot_instance.send_message(
                end_user.telegram_id,
                f"❌ <b>To'lov rad etildi</b>\n\n"
                f"📢 {channel.title}\n\n"
                "To'lov tasdiqlana olmadi. Qayta urinib ko'ring.",
            )
        except Exception:
            pass

    return web.json_response({"ok": True})
