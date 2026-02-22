def format_price(amount: float, currency: str = "UZS") -> str:
    """Format price with thousands separator."""
    return f"{amount:,.0f}".replace(",", " ") + f" {currency}"


def truncate(text: str, max_length: int = 50) -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
