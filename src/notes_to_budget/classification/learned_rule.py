"""Rule: the person already answered for exactly this description.

It is tried first, so a person's own decision is never overridden by a
general rule.
"""

from collections.abc import Sequence

from notes_to_budget.classification.classification_result import (
    ClassificationResult,
    EntryToClassify,
)
from notes_to_budget.classification.text_matching import is_the_same_text
from notes_to_budget.configuration.classification_rules import LearnedRule
from notes_to_budget.domain.category_catalog import CategoryCatalog
from notes_to_budget.domain.transaction_type import TransactionType


class LearnedAnswerRule:
    name = "learned_rule"

    def __init__(self, learned_rules: Sequence[LearnedRule], categories: CategoryCatalog) -> None:
        self._learned_rules = learned_rules
        self._categories = categories

    def classify(self, entry: EntryToClassify) -> ClassificationResult | None:
        for learned_rule in self._learned_rules:
            if is_the_same_text(learned_rule.description, entry.description):
                return self._apply(learned_rule, entry)
        return None

    def _apply(self, learned_rule: LearnedRule, entry: EntryToClassify) -> ClassificationResult:
        transaction_type = self._categories.transaction_type_of(learned_rule.category_name)
        if transaction_type is TransactionType.INCOME:
            amount = entry.entry.amount
        else:
            # Expenses, savings and investments: money out is positive,
            # money coming back is negative.
            amount = entry.amount_as_an_expense()
        return ClassificationResult(
            transaction_type=transaction_type,
            amount=amount,
            category_name=learned_rule.category_name,
            is_one_off=learned_rule.is_one_off,
        )
