from aiohttp import web

from api.routes_messaging import broadcast, send_message
from api.routes_payments import approve, get_screenshot, list_payments, reject
from api.routes_settings import get_settings, update_settings
from api.routes_stats import get_stats
from api.routes_users import ban_user, list_users, unban_user


def setup_api_routes(app: web.Application):
    """Register all Mini App API routes."""
    # Stats
    app.router.add_get("/api/stats", get_stats)

    # Payments
    app.router.add_get("/api/payments", list_payments)
    app.router.add_get("/api/payments/{id}/screenshot", get_screenshot)
    app.router.add_post("/api/payments/{id}/approve", approve)
    app.router.add_post("/api/payments/{id}/reject", reject)

    # Users
    app.router.add_get("/api/users", list_users)
    app.router.add_post("/api/users/{id}/ban", ban_user)
    app.router.add_post("/api/users/{id}/unban", unban_user)

    # Messaging
    app.router.add_post("/api/users/{id}/message", send_message)
    app.router.add_post("/api/broadcast", broadcast)

    # Settings
    app.router.add_get("/api/settings", get_settings)
    app.router.add_put("/api/settings", update_settings)
