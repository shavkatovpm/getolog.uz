"""Dashboard uchun bir martalik kirish kodlari (bosh bot orqali yuboriladi).

Foydalanuvchi saytda "kod olish" tugmasini bosib botga o'tadi, bot 6 xonali
kod yuboradi, foydalanuvchi shu kodni saytga kiritadi. Kod xotirada saqlanadi
(baza emas) — juda qisqa muddat (5 daqiqa) amal qiladi va bir martalik, shuning
uchun server qayta ishga tushsa eskirgan kodlar shunchaki yaroqsiz bo'lib
qoladi — bu qabul qilinadi.
"""

import random
import string
import time

_CODE_TTL_SECONDS = 300  # 5 daqiqa
_codes: dict[str, tuple[int, float]] = {}  # code -> (telegram_id, amal qilish muddati)


def generate_login_code(telegram_id: int) -> str:
    """Yangi 6 xonali kod yaratadi va telegram_id bilan bog'lab xotirada saqlaydi."""
    code = "".join(random.choices(string.digits, k=6))
    _codes[code] = (telegram_id, time.time() + _CODE_TTL_SECONDS)
    return code


def verify_login_code(code: str) -> int | None:
    """Kodni tekshiradi: to'g'ri va eskirmagan bo'lsa telegram_id qaytaradi.

    Kod bir martalik ishlatiladi — tekshirilgach (natijasidan qat'i nazar)
    darrov xotiradan o'chiriladi.
    """
    entry = _codes.pop(code, None)
    if entry is None:
        return None
    telegram_id, expires_at = entry
    if time.time() > expires_at:
        return None
    return telegram_id
