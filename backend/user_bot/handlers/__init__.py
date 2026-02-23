from aiogram import Router

from user_bot.handlers.start import router as start_router
from user_bot.handlers.payment import router as payment_router
from user_bot.handlers.support import router as support_router
from user_bot.middlewares.ad_inject import BrandingMiddleware


def get_user_bot_router() -> Router:
    router = Router()
    router.message.middleware(BrandingMiddleware())
    router.include_router(start_router)
    router.include_router(payment_router)
    router.include_router(support_router)
    return router
