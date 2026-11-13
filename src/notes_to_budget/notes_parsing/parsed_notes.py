"""What the notes say, before any category is chosen."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from notes_to_budget.domain.daily_balance import DailyBalance
from notes_to_budget.notes_parsing.parsing_problem import ParsingProblem


@dataclass(frozen=True)
class ParsedEntry:
    """One line of the notes that moves money."""

    line_number: int
    is_money_in: bool
    """True for a line that starts with ``+``, false for ``-``."""
    amount: Decimal
    description: str
    account_code: str | None
    """The account written at the end of the line, if any."""
    is_uncertain: bool
    original_text: str


@dataclass(frozen=True)
class ParsedDay:
    day: date
    line_number: int
    balance: DailyBalance | None
    """The balances written next to the day, if they could be read."""
    entries: tuple[ParsedEntry, ...]


@dataclass(frozen=True)
class ParsedNotes:
    file_name: str
    days: tuple[ParsedDay, ...]
    """The days in the order they appear in the file."""
    problems: tuple[ParsingProblem, ...]

    def number_of_entries(self) -> int:
        return sum(len(day.entries) for day in self.days)
