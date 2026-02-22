from aiogram import Router

from bot.handlers.start import router as start_router
from bot.handlers.register import router as register_router
from bot.handlers.settings import router as settings_router
from bot.handlers.stats import router as stats_router
from bot.handlers.manage_users import router as manage_users_router
from bot.handlers.payments import router as payments_router
from bot.handlers.subscription import router as subscription_router


def get_main_bot_router() -> Router:
    router = Router()
    router.include_router(start_router)
    router.include_router(register_router)
    router.include_router(settings_router)
    router.include_router(stats_router)
    router.include_router(manage_users_router)
    router.include_router(payments_router)
    router.include_router(subscription_router)
    return router
