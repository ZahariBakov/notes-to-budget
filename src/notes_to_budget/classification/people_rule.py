"""Rule: a person's name in the description decides the category.

"shoes Mimi" goes to Children whatever was bought. A person listed
without a category is only a label and decides nothing.
"""

from collections.abc import Sequence
from datetime import date

from notes_to_budget.classification.classification_result import (
    ClassificationResult,
    EntryToClassify,
)
from notes_to_budget.classification.text_matching import contains_any_keyword
from notes_to_budget.configuration.classification_rules import PersonRule
from notes_to_budget.domain.transaction_type import TransactionType


class PeopleRule:
    name = "people_rule"

    def __init__(self, person_rules: Sequence[PersonRule]) -> None:
        self._person_rules = person_rules

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
        for person_rule in self._person_rules:
            if not person_rule.category_name:
                continue
            if not contains_any_keyword(description, person_rule.names):
                continue
            if contains_any_keyword(description, person_rule.excluded_keywords):
                continue
            return person_rule.category_name
        return None
