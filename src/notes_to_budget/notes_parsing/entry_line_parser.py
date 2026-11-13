"""Reads one line that moves money.

Understood forms::

    - 12 - lunch - R         an expense from account R
    + 300 - rent - C         money in, to account C
    - 200 - from card to cash    no account at the end (a transfer)
    - lunch - 12 - R         amount and description swapped
    - 5 socks - C            the dash after the amount forgotten
    + 2700.46 - B            no description
    - 17 - lunch - C - ?     marked as uncertain
"""

import re
from decimal import Decimal

from notes_to_budget.notes_parsing.account_code_resolver import AccountCodeResolver
from notes_to_budget.notes_parsing.amount_parser import (
    parse_amount,
    split_amount_from_following_words,
)
from notes_to_budget.notes_parsing.parsed_notes import ParsedEntry
from notes_to_budget.notes_parsing.parsing_problem import LineNotUnderstood
from notes_to_budget.notes_parsing.text_cleaning import use_plain_dashes

MONEY_IN_SIGN = "+"
MONEY_OUT_SIGN = "-"

# A dash separates the parts of an entry when it has a space on at least
# one side, so "Coca-Cola" stays one word but "56- lunch" is still split.
_PART_SEPARATOR = re.compile(r"\s+-\s*|\s*-\s+")
_JOINER_FOR_DESCRIPTION_PARTS = " - "


def looks_like_entry_line(line_text: str) -> bool:
    first_character = use_plain_dashes(line_text).strip()[:1]
    return first_character in (MONEY_IN_SIGN, MONEY_OUT_SIGN)


def parse_entry_line(
    line_text: str,
    line_number: int,
    account_code_resolver: AccountCodeResolver,
    uncertain_marker: str,
) -> ParsedEntry:
    cleaned_line = use_plain_dashes(line_text).strip()
    is_money_in = cleaned_line.startswith(MONEY_IN_SIGN)
    text_after_sign, is_uncertain = _remove_uncertain_marker(cleaned_line[1:], uncertain_marker)

    parts = [part.strip() for part in _PART_SEPARATOR.split(text_after_sign) if part.strip()]
    amount, parts_without_amount = _take_the_amount(parts)
    account_code, description_parts = _take_the_account(parts_without_amount, account_code_resolver)

    return ParsedEntry(
        line_number=line_number,
        is_money_in=is_money_in,
        amount=amount,
        description=_JOINER_FOR_DESCRIPTION_PARTS.join(description_parts),
        account_code=account_code,
        is_uncertain=is_uncertain,
        original_text=line_text.strip(),
    )


def _remove_uncertain_marker(text: str, uncertain_marker: str) -> tuple[str, bool]:
    """Take ``?`` (and the dash before it) off the end of the line."""
    text = text.strip()
    if not text.endswith(uncertain_marker):
        return text, False
    text_without_marker = text.removesuffix(uncertain_marker).rstrip()
    return text_without_marker.removesuffix(MONEY_OUT_SIGN).rstrip(), True


def _take_the_amount(parts: list[str]) -> tuple[Decimal, list[str]]:
    """Find the amount among the parts and return it with the remaining parts."""
    if not parts:
        raise LineNotUnderstood("notes.problem.amount_missing")

    amount_in_first_place = parse_amount(parts[0])
    if amount_in_first_place is not None:
        return amount_in_first_place, parts[1:]

    amount_then_words = split_amount_from_following_words(parts[0])
    if amount_then_words is not None:
        amount, following_words = amount_then_words
        return amount, [following_words, *parts[1:]]

    for position, part in enumerate(parts):
        swapped_amount = parse_amount(part)
        if swapped_amount is not None:
            return swapped_amount, parts[:position] + parts[position + 1 :]

    raise LineNotUnderstood("notes.problem.amount_missing")


def _take_the_account(
    parts: list[str], account_code_resolver: AccountCodeResolver
) -> tuple[str | None, list[str]]:
    """The account, when written, is the last part of the line."""
    if not parts:
        return None, parts
    account_code = account_code_resolver.resolve(parts[-1])
    if account_code is None:
        return None, parts
    return account_code, parts[:-1]
