import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, and_

from db.engine import async_session
from db.models import Subscription, AdminSubscription, UserBot
from core.encryption import decrypt_token
from utils.constants import PlanName, SubStatus

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self, bot_manager):
        self.bot_manager = bot_manager
        self.scheduler = AsyncIOScheduler()

    def start(self):
        # Every 10 minutes: kick expired end users, expire admin subs
        self.scheduler.add_job(
            self.kick_expired_users,
            "interval",
            minutes=10,
            id="kick_expired",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self.expire_admin_subscriptions,
            "interval",
            minutes=10,
            id="expire_admin_subs",
            replace_existing=True,
        )

        # Every 6 hours: send notifications, health check
        self.scheduler.add_job(
            self.send_expiry_notifications,
            "interval",
            hours=6,
            id="expiry_notifications",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self.bot_health_check,
            "interval",
            hours=6,
            id="health_check",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info("Scheduler started")

    async def kick_expired_users(self):
        """Kick end users whose subscription has expired."""
        now = datetime.now(timezone.utc)

        async with async_session() as session:
            result = await session.execute(
                select(Subscription).where(
                    and_(
                        Subscription.status == SubStatus.ACTIVE,
                        Subscription.expires_at is not None,
                        Subscription.expires_at <= now,
                    )
                )
            )
            expired_subs = result.scalars().all()

            for sub in expired_subs:
                try:
                    from core.invite_link import kick_member

                    # Get the bot for this channel
                    channel = sub.channel
                    bot = self.bot_manager.bots.get(channel.user_bot_id)
                    if bot:
                        success = await kick_member(
                            bot, channel.telegram_chat_id, sub.end_user.telegram_id
                        )
                        if success:
                            sub.status = SubStatus.KICKED
                            sub.kicked_at = now
                            logger.info(
                                f"Kicked user {sub.end_user.telegram_id} from {channel.title}"
                            )

                            # Notify end user
                            try:
                                await bot.send_message(
                                    sub.end_user.telegram_id,
                                    "⏰ Obuna muddatingiz tugadi. Qayta obuna bo'lish uchun /start bosing.",
                                )
                            except Exception:
                                pass

                            # Notify admin
                            try:
                                admin_tg_id = channel.bot.admin.telegram_id
                                username = sub.end_user.username or sub.end_user.telegram_id
                                await bot.send_message(
                                    admin_tg_id,
                                    f"🚪 <b>Foydalanuvchi chiqarildi</b>\n\n"
                                    f"👤 @{username}\n"
                                    f"📢 {channel.title}\n"
                                    f"📅 Obuna muddati tugagan",
                                )
                            except Exception:
                                pass
                except Exception as e:
                    logger.error(f"Error kicking user sub={sub.id}: {e}")

            await session.commit()

    async def expire_admin_subscriptions(self):
        """Expire admin subscriptions that have ended."""
        now = datetime.now(timezone.utc)

        async with async_session() as session:
            result = await session.execute(
                select(AdminSubscription).where(
                    and_(
                        AdminSubscription.status == SubStatus.ACTIVE,
                        AdminSubscription.plan != PlanName.FREE,
                        AdminSubscription.expires_at is not None,
                        AdminSubscription.expires_at <= now,
                    )
                )
            )
            expired = result.scalars().all()

            for admin_sub in expired:
                admin_sub.status = SubStatus.EXPIRED
                # Create new free subscription
                free_sub = AdminSubscription(
                    user_admin_id=admin_sub.user_admin_id,
                    plan=PlanName.FREE,
                    status=SubStatus.ACTIVE,
                )
                session.add(free_sub)
                logger.info(f"Admin {admin_sub.user_admin_id} downgraded to free")

            await session.commit()

    async def send_expiry_notifications(self):
        """Send 3-day and 1-day expiry warnings."""
        now = datetime.now(timezone.utc)
        three_days = now + timedelta(days=3)
        one_day = now + timedelta(days=1)

        async with async_session() as session:
            # End user 3-day warning
            result = await session.execute(
                select(Subscription).where(
                    and_(
                        Subscription.status == SubStatus.ACTIVE,
                        Subscription.notified_3day == False,
                        Subscription.expires_at is not None,
                        Subscription.expires_at <= three_days,
                        Subscription.expires_at > one_day,
                    )
                )
            )
            for sub in result.scalars().all():
                try:
                    channel = sub.channel
                    bot = self.bot_manager.bots.get(channel.user_bot_id)
                    if bot:
                        await bot.send_message(
                            sub.end_user.telegram_id,
                            "⚠️ Obuna muddatingiz 3 kundan keyin tugaydi. Qayta obuna bo'ling!",
                        )
                        sub.notified_3day = True

                        # Notify admin
                        try:
                            admin_tg_id = channel.bot.admin.telegram_id
                            username = sub.end_user.username or sub.end_user.telegram_id
                            await bot.send_message(
                                admin_tg_id,
                                f"⚠️ <b>Obuna 3 kundan tugaydi</b>\n\n"
                                f"👤 @{username}\n"
                                f"📢 {channel.title}",
                            )
                        except Exception:
                            pass
                except Exception as e:
                    logger.error(f"3-day notification error: {e}")

            # End user 1-day warning
            result = await session.execute(
                select(Subscription).where(
                    and_(
                        Subscription.status == SubStatus.ACTIVE,
                        Subscription.notified_1day == False,
                        Subscription.expires_at is not None,
                        Subscription.expires_at <= one_day,
                        Subscription.expires_at > now,
                    )
                )
            )
            for sub in result.scalars().all():
                try:
                    channel = sub.channel
                    bot = self.bot_manager.bots.get(channel.user_bot_id)
                    if bot:
                        await bot.send_message(
                            sub.end_user.telegram_id,
                            "🔴 Obuna muddatingiz ertaga tugaydi! Hoziroq uzaytiring.",
                        )
                        sub.notified_1day = True

                        # Notify admin
                        try:
                            admin_tg_id = channel.bot.admin.telegram_id
                            username = sub.end_user.username or sub.end_user.telegram_id
                            await bot.send_message(
                                admin_tg_id,
                                f"🔴 <b>Obuna ertaga tugaydi</b>\n\n"
                                f"👤 @{username}\n"
                                f"📢 {channel.title}",
                            )
                        except Exception:
                            pass
                except Exception as e:
                    logger.error(f"1-day notification error: {e}")

            await session.commit()

    async def bot_health_check(self):
        """Check all registered bots' health."""
        results = await self.bot_manager.health_check()
        dead_bots = [bid for bid, status in results.items() if status == "dead"]
        if dead_bots:
            logger.warning(f"Dead bots detected: {dead_bots}")
            # Try to restart dead bots
            async with async_session() as session:
                for bot_id in dead_bots:
                    result = await session.execute(
                        select(UserBot).where(
                            and_(UserBot.id == bot_id, UserBot.is_active == True)
                        )
                    )
                    user_bot = result.scalar_one_or_none()
                    if user_bot:
                        await self.bot_manager.stop_bot(bot_id)
                        await self.bot_manager.register_bot(
                            bot_id, user_bot.bot_token
                        )
                        logger.info(f"Restarted bot {bot_id}")

    def stop(self):
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
