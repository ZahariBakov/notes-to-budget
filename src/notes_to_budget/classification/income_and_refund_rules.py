"""Rules for money coming in: real income, or money that came back.

"+ 2000 - salary" is income. "+ 5 - from John for lunch" is not: it is
part of a lunch coming back, so it lowers the lunch category instead.
"""

from collections.abc import Sequence

from notes_to_budget.classification.classification_result import (
    ClassificationResult,
    EntryToClassify,
)
from notes_to_budget.classification.classification_rule import CategoryFinder
from notes_to_budget.classification.text_matching import contains_keyword
from notes_to_budget.domain.category_catalog import CategoryCatalog
from notes_to_budget.domain.transaction_type import TransactionType


class IncomeRule:
    name = "income_rule"

    def __init__(
        self, categories: CategoryCatalog, category_finders: Sequence[CategoryFinder]
    ) -> None:
        self._categories = categories
        self._category_finders = category_finders

    def classify(self, entry: EntryToClassify) -> ClassificationResult | None:
        if not entry.is_money_in:
            return None
        income_category_name = self._find_income_category(entry)
        if income_category_name is None:
            return None
        return ClassificationResult(
            transaction_type=TransactionType.INCOME,
            amount=entry.entry.amount,
            category_name=income_category_name,
        )

    def _find_income_category(self, entry: EntryToClassify) -> str | None:
        """An income category is found by its own name or through the person's rules."""
        for income_category_name in self._categories.income_category_names:
            if contains_keyword(entry.description, income_category_name):
                return income_category_name
        for category_finder in self._category_finders:
            category_name = category_finder.find_category(entry.description, entry.day)
            if category_name in self._categories.income_category_names:
                return category_name
        return None


class RefundRule:
    name = "refund_rule"

    def __init__(
        self, categories: CategoryCatalog, category_finders: Sequence[CategoryFinder]
    ) -> None:
        self._categories = categories
        self._category_finders = category_finders

    def classify(self, entry: EntryToClassify) -> ClassificationResult | None:
        if not entry.is_money_in:
            return None
        for category_finder in self._category_finders:
            category_name = category_finder.find_category(entry.description, entry.day)
            if category_name in self._categories.expense_category_names():
                return ClassificationResult(
                    transaction_type=TransactionType.EXPENSE,
                    amount=entry.amount_as_an_expense(),
                    category_name=category_name,
                )
        return None
