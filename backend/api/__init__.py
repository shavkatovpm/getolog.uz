from aiohttp import web

from api.routes_messaging import broadcast, send_message
from api.routes_payments import approve, get_screenshot, list_payments, reject
from api.routes_settings import get_settings, update_settings
from api.routes_stats import get_stats
from api.routes_users import ban_user, list_users, unban_user
from api.mod_routes import (
    mod_get_stats, mod_list_admins, mod_ban_admin, mod_unban_admin,
    mod_list_bots, mod_change_password,
)


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

    # Moderator API
    app.router.add_get("/api/mod/stats", mod_get_stats)
    app.router.add_get("/api/mod/admins", mod_list_admins)
    app.router.add_post("/api/mod/admins/{id}/ban", mod_ban_admin)
    app.router.add_post("/api/mod/admins/{id}/unban", mod_unban_admin)
    app.router.add_get("/api/mod/bots", mod_list_bots)
    app.router.add_post("/api/mod/password", mod_change_password)
