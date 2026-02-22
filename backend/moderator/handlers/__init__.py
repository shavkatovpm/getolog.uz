from aiogram import Router

from moderator.handlers.dashboard import router as dashboard_router
from moderator.handlers.manage_admins import router as manage_admins_router


def get_moderator_router() -> Router:
    router = Router()
    router.include_router(dashboard_router)
    router.include_router(manage_admins_router)
    return router
