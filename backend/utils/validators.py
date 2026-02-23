# Known Uzbek card prefixes that don't follow Luhn
_UZ_PREFIXES = ("8600", "9860")


def luhn_check(card_number: str) -> bool:
    """Validate card number using Luhn algorithm."""
    digits = [int(d) for d in card_number if d.isdigit()]
    if len(digits) != 16:
        return False

    checksum = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d

    return checksum % 10 == 0


def validate_card(raw: str) -> str | None:
    """Validate and format card number. Returns formatted card or None.

    Uzcard (8600) and Humo (9860) cards don't follow Luhn algorithm,
    so we only check prefix + 16 digits for them.
    """
    card = raw.strip().replace(" ", "")
    if not card.isdigit() or len(card) != 16:
        return None

    # Uzbek cards: skip Luhn, just check known prefix
    if card.startswith(_UZ_PREFIXES):
        return " ".join(card[i:i+4] for i in range(0, 16, 4))

    # International cards: apply Luhn
    if not luhn_check(card):
        return None

    return " ".join(card[i:i+4] for i in range(0, 16, 4))
