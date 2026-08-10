"""Foydalanuvchiga ko'rsatiladigan summalarni formatlash — botning barcha
xabarlarida bir xil ko'rinish uchun (minglik ajratkichi bilan)."""


def format_amount(value: float) -> str:
    """1000 -> "1,000", 20000 -> "20,000", 1500.5 -> "1,500.5"."""
    value = float(value)
    if value == int(value):
        return f"{int(value):,}"
    return f"{value:,.2f}"
