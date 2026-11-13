"""Small repairs to the text that phones and keyboards like to change."""

import re

# Phones often replace the plain minus with a longer dash.
DASH_LOOKALIKES = ("–", "—", "−")


def use_plain_dashes(text: str) -> str:
    for dash_lookalike in DASH_LOOKALIKES:
        text = text.replace(dash_lookalike, "-")
    return text


def remove_currency_symbol_after_numbers(text: str, currency_symbol: str) -> str:
    """Read ``115€`` and ``115 €`` as the plain number ``115``."""
    if not currency_symbol:
        return text
    symbol_after_a_digit = re.compile(rf"(?<=\d)\s?{re.escape(currency_symbol)}")
    return symbol_after_a_digit.sub("", text)
