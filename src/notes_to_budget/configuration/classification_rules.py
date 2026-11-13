"""The rules a person writes (or teaches) for choosing categories."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class KeywordRule:
    """Words in the description that point to a category."""

    keywords: tuple[str, ...]
    category_name: str
    weekend_category_name: str = ""
    """A different category on Saturday and Sunday; empty means the same one."""
    excluded_keywords: tuple[str, ...] = ()
    """Words that switch the rule off, so a later rule can decide."""


@dataclass(frozen=True)
class PersonRule:
    """A person whose name in the description decides the category."""

    names: tuple[str, ...]
    category_name: str
    """Empty means the name is only a label and decides nothing."""
    excluded_keywords: tuple[str, ...] = ()


@dataclass(frozen=True)
class LearnedRule:
    """An answer the person gave once for an exact description."""

    description: str
    category_name: str
    is_one_off: bool = False


@dataclass(frozen=True)
class SpecialPeriod:
    """Days, such as a holiday, when everything spent goes to one category."""

    name: str
    first_day: date
    last_day: date
    category_name: str
    spending_is_worked_out_from_balances: bool = False
    """True when no detailed notes are written on those days."""
    categories_that_stay: tuple[str, ...] = ()
    """Categories the period leaves alone: a bill paid on holiday is still a bill."""

    def contains(self, day: date) -> bool:
        return self.first_day <= day <= self.last_day
