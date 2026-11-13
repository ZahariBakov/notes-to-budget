"""Rule: during a holiday, everything spent goes to the holiday's category.

A period may list categories it leaves alone, because a bill or a loan
payment that falls on a holiday is still a bill or a loan payment.
"""

from collections.abc import Sequence

from notes_to_budget.classification.classification_result import (
    ClassificationResult,
    EntryToClassify,
)
from notes_to_budget.classification.classification_rule import CategoryFinder
from notes_to_budget.configuration.classification_rules import SpecialPeriod
from notes_to_budget.domain.transaction_type import TransactionType


class SpecialPeriodRule:
    name = "special_period_rule"

    def __init__(
        self, special_periods: Sequence[SpecialPeriod], category_finders: Sequence[CategoryFinder]
    ) -> None:
        self._special_periods = special_periods
        self._category_finders = category_finders

    def classify(self, entry: EntryToClassify) -> ClassificationResult | None:
        if entry.is_money_in:
            return None
        for period in self._special_periods:
            if not period.contains(entry.day):
                continue
            if self._usual_category_of(entry) in period.categories_that_stay:
                return None
            return ClassificationResult(
                transaction_type=TransactionType.EXPENSE,
                amount=entry.entry.amount,
                category_name=period.category_name,
            )
        return None

    def _usual_category_of(self, entry: EntryToClassify) -> str | None:
        """The category the entry would get on an ordinary day."""
        for category_finder in self._category_finders:
            category_name = category_finder.find_category(entry.description, entry.day)
            if category_name is not None:
                return category_name
        return None
