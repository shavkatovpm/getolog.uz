"""aiohttp server: bot webhooklari va dashboard API'si shu bitta ilovada birlashadi.

Arxitektura spec talabiga mos: `domen.com/webhook/{token}` — token URL'da,
server shu token bo'yicha qaysi bot ekanini registrdan topadi va tegishli
Dispatcher'ga (bosh bot yoki admin boti) uzatadi. Dashboard uchun `/api/*`
yo'llari xuddi shu serverga qo'shiladi (`app/api/routes.py`), chunki ikkinchi
freymvork/port kiritish shart emas.
"""

from aiohttp import web
from aiogram.types import Update

from app.api.middlewares import auth_middleware, cors_middleware, db_session_middleware
from app.api.routes import routes as api_routes
from app.bot import registry
from app.bot.dispatcher import child_dp, main_dp
from app.config import settings


async def webhook_handler(request: web.Request) -> web.Response:
    token = request.match_info["token"]
    bot = registry.get_bot_by_token(token)
    if bot is None:
        # Noma'lum token — soxta so'rov yoki eskirgan webhook. Jim javob qaytariladi.
        return web.Response(status=403)

    data = await request.json()
    update = Update.model_validate(data, context={"bot": bot})

    dp = main_dp if token == settings.main_bot_token else child_dp
    await dp.feed_update(bot=bot, update=update)
    return web.Response()


def create_app() -> web.Application:
    app = web.Application(middlewares=[db_session_middleware, cors_middleware, auth_middleware])
    app.router.add_post("/webhook/{token}", webhook_handler)
    app.router.add_route("OPTIONS", "/api/{tail:.*}", lambda request: web.Response())
    app.add_routes(api_routes)
    return app
