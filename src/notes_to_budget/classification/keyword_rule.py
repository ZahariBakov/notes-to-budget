"""Rule: a word in the description points to a category.

The rules are tried from the top; the first one that matches decides.
A rule may name another category for Saturday and Sunday, for example
lunch at work on working days and eating out at the weekend.
"""

from collections.abc import Sequence
from datetime import date

from notes_to_budget.classification.classification_result import (
    ClassificationResult,
    EntryToClassify,
)
from notes_to_budget.classification.text_matching import contains_any_keyword
from notes_to_budget.configuration.classification_rules import KeywordRule
from notes_to_budget.domain.transaction_type import TransactionType

SATURDAY = 5


class KeywordCategoryRule:
    name = "keyword_rule"

    def __init__(self, keyword_rules: Sequence[KeywordRule]) -> None:
        self._keyword_rules = keyword_rules

    def classify(self, entry: EntryToClassify) -> ClassificationResult | None:
        if entry.is_money_in:
            return None
        category_name = self.find_category(entry.description, entry.day)
        if category_name is None:
            return None
        return ClassificationResult(
            transaction_type=TransactionType.EXPENSE,
            amount=entry.entry.amount,
            category_name=category_name,
        )

    def find_category(self, description: str, day: date) -> str | None:
        for keyword_rule in self._keyword_rules:
            if not contains_any_keyword(description, keyword_rule.keywords):
                continue
            if contains_any_keyword(description, keyword_rule.excluded_keywords):
                continue
            is_weekend = day.weekday() >= SATURDAY
            if is_weekend and keyword_rule.weekend_category_name:
                return keyword_rule.weekend_category_name
            return keyword_rule.category_name
        return None
