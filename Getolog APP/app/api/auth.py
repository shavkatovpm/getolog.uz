"""Telegram orqali autentifikatsiya: bir martalik kod (websayt) va Mini App initData.

Websaytda foydalanuvchi botdan bir martalik kod oladi (`app/services/login_codes.py`)
va shu kodni kiritadi — bu Login Widget'ga qaraganda soddaroq va domenga bog'liq
BotFather sozlamasini talab qilmaydi. Mini App (Telegram ichida ochilganda) esa
Telegram tomonidan HMAC bilan imzolangan `initData` orqali avtomatik autentifikatsiya
qilinadi — buni `MAIN_BOT_TOKEN` yordamida qayta hisoblab tekshiramiz.
"""

import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import Admin

AUTH_MAX_AGE_SECONDS = 86400  # initData 24 soatdan eski bo'lmasin
JWT_EXPIRY_SECONDS = 30 * 86400  # dashboard sessiyasi 30 kun amal qiladi


class AuthError(Exception):
    """Telegram autentifikatsiyasi muvaffaqiyatsiz bo'lganda ko'tariladi."""


def verify_webapp_init_data(init_data: str) -> int:
    """Telegram Mini App initData'sini tekshiradi, muvaffaqiyatli bo'lsa telegram_id qaytaradi."""
    parsed = dict(parse_qsl(init_data, strict_parsing=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise AuthError("hash yo'q")

    data_check_string = "\n".join(f"{k}={parsed[k]}" for k in sorted(parsed))

    secret_key = hmac.new(b"WebAppData", settings.main_bot_token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        raise AuthError("imzo mos kelmadi")

    auth_date = int(parsed.get("auth_date", 0))
    if time.time() - auth_date > AUTH_MAX_AGE_SECONDS:
        raise AuthError("login ma'lumoti eskirgan")

    user = json.loads(parsed["user"])
    return int(user["id"])


async def resolve_role(session: AsyncSession, telegram_id: int) -> dict:
    """Telegram ID bo'yicha foydalanuvchi rolini aniqlaydi: owner yoki admin.

    Dashboard orqali ro'yxatdan o'tish yo'q — admin avval botga /start yuborib
    onboarding'dan o'tgan bo'lishi shart.
    """
    if telegram_id == settings.owner_telegram_id:
        return {"role": "owner", "admin_id": None, "telegram_id": telegram_id}

    result = await session.execute(select(Admin).where(Admin.telegram_id == telegram_id))
    admin = result.scalar_one_or_none()
    if admin is None:
        raise AuthError(
            "Siz hali GETOLOG'da ro'yxatdan o'tmagansiz — avval botga /start yuboring"
        )

    return {"role": "admin", "admin_id": admin.id, "telegram_id": telegram_id}


def issue_jwt(claims: dict) -> str:
    """Rolga oid ma'lumotlar asosida dashboard uchun JWT token yaratadi."""
    payload = {**claims, "exp": int(time.time()) + JWT_EXPIRY_SECONDS}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")


def decode_jwt(token: str) -> dict:
    """JWT tokenni tekshiradi va ichidagi claims'ni qaytaradi. Yaroqsiz bo'lsa xato ko'taradi."""
    return jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
