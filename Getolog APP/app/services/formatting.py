"""Foydalanuvchiga ko'rsatiladigan summa va sanalarni formatlash — botning
barcha xabarlarida bir xil ko'rinish uchun."""

from datetime import datetime, timedelta, timezone

# Baza va server UTC'da ishlaydi, obunachilar esa O'zbekistonda — muddat
# ularning soatiga ko'ra ko'rsatilishi kerak, aks holda 09:00 da tugaydigan
# obuna xabarda 04:00 deb chiqadi. O'zbekistonda yozgi vaqt yo'q, shuning
# uchun qat'iy +5 yetarli (tashqi tzdata bog'liqligi ham kerak emas).
TASHKENT_TZ = timezone(timedelta(hours=5))


def format_expiry(end_date: datetime | None) -> str:
    """Obuna tugash vaqti — Toshkent vaqtida. `None` = umrbod obuna."""
    if end_date is None:
        return "Umrbod (muddatsiz)"
    return end_date.astimezone(TASHKENT_TZ).strftime("%d.%m.%Y %H:%M")


def format_amount(value: float) -> str:
    """1000 -> "1,000", 20000 -> "20,000", 1500.5 -> "1,500.5"."""
    value = float(value)
    if value == int(value):
        return f"{int(value):,}"
    return f"{value:,.2f}"
