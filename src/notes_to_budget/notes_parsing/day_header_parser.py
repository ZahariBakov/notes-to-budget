"""Reads the line that starts a day: the date and the balances.

Understood forms::

    14 - 120 / 340 / 1500          only the day; the month comes from the file
    14.03 - 120 / 340 / 1500       day and month
    14.03.26 - 120 / 340 / 1500    full date, short year
    14.03.2026 - 120 / 340 / 1500  full date
    14 -                           a day without balances
    14                             the same, with the dash left out
"""

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from notes_to_budget.domain.month import Month
from notes_to_budget.notes_parsing.parsing_problem import LineNotUnderstood
from notes_to_budget.notes_parsing.text_cleaning import use_plain_dashes

_DAY_HEADER = re.compile(
    r"\s*(?P<day>\d{1,2})"
    r"(?:\.(?P<month>\d{1,2}))?"
    r"(?:\.(?P<year>\d{4}|\d{2}))?"
    r"\s*(?:-(?P<balances>.*))?"
)
_ONE_BALANCE = re.compile(r"(-?)\s*(\d+(?:[.,]\d+)?)")
_NOTE_IN_BRACKETS = re.compile(r"\(.*?\)")
_BALANCE_SEPARATOR = "/"
_FIRST_YEAR_OF_THE_CENTURY = 2000


@dataclass(frozen=True)
class DayHeader:
    day: date
    balance_amounts: tuple[Decimal, ...] | None
    """The balances in the order written; None when there are none."""
    balances_were_not_understood: bool = False


def looks_like_day_header(line_text: str) -> bool:
    """A day header is a day number, a dash and then only numbers.

    Words after the dash mean it is something else, most often an entry
    whose ``-`` or ``+`` was forgotten; treating it as a day would put
    the entries below it under a wrong date.
    """
    match = _DAY_HEADER.fullmatch(use_plain_dashes(line_text))
    if match is None:
        return False
    balances_text = _NOTE_IN_BRACKETS.sub("", match.group("balances") or "")
    return not any(character.isalpha() for character in balances_text)


def parse_day_header(
    line_text: str, month_of_the_file: Month | None, expected_number_of_balances: int
) -> DayHeader:
    """Read the date and the balances, or explain why the date cannot be known."""
    match = _DAY_HEADER.fullmatch(use_plain_dashes(line_text))
    if match is None:
        raise LineNotUnderstood("notes.problem.line_not_understood")

    day = _read_date(match, month_of_the_file)
    balance_amounts = _read_balances(match.group("balances") or "")
    if balance_amounts is not None and len(balance_amounts) != expected_number_of_balances:
        return DayHeader(day=day, balance_amounts=None, balances_were_not_understood=True)
    return DayHeader(day=day, balance_amounts=balance_amounts)


def _read_date(match: re.Match[str], month_of_the_file: Month | None) -> date:
    day_number = int(match.group("day"))
    month_number = _read_month_number(match, month_of_the_file, day_number)
    year = _read_year(match, month_of_the_file)
    try:
        return date(year, month_number, day_number)
    except ValueError:
        raise LineNotUnderstood(
            "notes.problem.date_not_valid", day=day_number, month=month_number, year=year
        ) from None


def _read_month_number(
    match: re.Match[str], month_of_the_file: Month | None, day_number: int
) -> int:
    if match.group("month") is not None:
        return int(match.group("month"))
    if month_of_the_file is None:
        raise LineNotUnderstood("notes.problem.month_unknown", day=day_number)
    return month_of_the_file.month_number


def _read_year(match: re.Match[str], month_of_the_file: Month | None) -> int:
    written_year = match.group("year")
    if written_year is None:
        if month_of_the_file is None:
            raise LineNotUnderstood("notes.problem.month_unknown", day=match.group("day"))
        return month_of_the_file.year
    if len(written_year) == 2:
        return _FIRST_YEAR_OF_THE_CENTURY + int(written_year)
    return int(written_year)


def _read_balances(balances_text: str) -> tuple[Decimal, ...] | None:
    """Read ``120 / 340 / - 15``; an unreadable line gives an empty result."""
    balances_text = _NOTE_IN_BRACKETS.sub("", balances_text).strip()
    if not balances_text:
        return None

    amounts = []
    for written_balance in balances_text.split(_BALANCE_SEPARATOR):
        match = _ONE_BALANCE.fullmatch(written_balance.strip())
        if match is None:
            return ()
        amount = Decimal(match.group(2).replace(",", "."))
        amounts.append(-amount if match.group(1) else amount)
    return tuple(amounts)
