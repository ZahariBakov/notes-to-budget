"""One calendar month, the period a budget sheet covers."""

import calendar
import re
from dataclasses import dataclass
from datetime import date

_YEAR_DASH_MONTH = re.compile(r"(\d{4})-(\d{1,2})")


@dataclass(frozen=True, order=True)
class Month:
    year: int
    month_number: int

    def __post_init__(self) -> None:
        if not 1 <= self.month_number <= 12:
            raise ValueError(f"A month number is between 1 and 12, not {self.month_number}.")

    @classmethod
    def from_text(cls, text: str) -> "Month":
        """Read a month written as ``2026-11``."""
        match = _YEAR_DASH_MONTH.fullmatch(text.strip())
        if match is None:
            raise ValueError(f"Write the month as YEAR-MONTH, for example 2026-11, not '{text}'.")
        return cls(year=int(match.group(1)), month_number=int(match.group(2)))

    @classmethod
    def of_day(cls, day: date) -> "Month":
        return cls(year=day.year, month_number=day.month)

    @property
    def first_day(self) -> date:
        return date(self.year, self.month_number, 1)

    @property
    def last_day(self) -> date:
        number_of_days = calendar.monthrange(self.year, self.month_number)[1]
        return date(self.year, self.month_number, number_of_days)

    def contains(self, day: date) -> bool:
        return self.first_day <= day <= self.last_day

    def next_month(self) -> "Month":
        if self.month_number == 12:
            return Month(self.year + 1, 1)
        return Month(self.year, self.month_number + 1)

    def previous_month(self) -> "Month":
        if self.month_number == 1:
            return Month(self.year - 1, 12)
        return Month(self.year, self.month_number - 1)

    def __str__(self) -> str:
        return f"{self.year}-{self.month_number:02d}"
