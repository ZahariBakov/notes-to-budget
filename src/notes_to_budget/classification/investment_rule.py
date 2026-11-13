"""Rule: money invested (positive) or taken out of an investment (negative)."""

from collections.abc import Sequence

from notes_to_budget.classification.classification_result import (
    ClassificationResult,
    EntryToClassify,
)
from notes_to_budget.classification.text_matching import contains_any_keyword
from notes_to_budget.domain.transaction_type import TransactionType


class InvestmentRule:
    name = "investment_rule"

    def __init__(self, investment_phrases: Sequence[str], investments_category_name: str) -> None:
        self._investment_phrases = investment_phrases
        self._investments_category_name = investments_category_name

    def classify(self, entry: EntryToClassify) -> ClassificationResult | None:
        if not contains_any_keyword(entry.description, self._investment_phrases):
            return None
        return ClassificationResult(
            transaction_type=TransactionType.INVESTMENT,
            amount=entry.amount_as_an_expense(),
            category_name=self._investments_category_name,
        )
