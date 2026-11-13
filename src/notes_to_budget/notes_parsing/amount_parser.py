"""Reads amounts of money written as text."""

import re
from decimal import Decimal

_AMOUNT = r"\d+(?:[.,]\d+)?"
_WHOLE_TEXT_IS_AN_AMOUNT = re.compile(_AMOUNT)
_AMOUNT_THEN_WORDS = re.compile(rf"({_AMOUNT})\s+(\S.*)")


def parse_amount(text: str) -> Decimal | None:
    """Read ``12``, ``37.44`` or ``16,25``; return None for anything else."""
    cleaned_text = text.strip()
    if _WHOLE_TEXT_IS_AN_AMOUNT.fullmatch(cleaned_text) is None:
        return None
    return Decimal(cleaned_text.replace(",", "."))


def split_amount_from_following_words(text: str) -> tuple[Decimal, str] | None:
    """Read ``5 socks`` as the amount 5 and the words ``socks``.

    Helps with entries where the dash after the amount was forgotten.
    """
    match = _AMOUNT_THEN_WORDS.fullmatch(text.strip())
    if match is None:
        return None
    return Decimal(match.group(1).replace(",", ".")), match.group(2).strip()
