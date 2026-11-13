"""What every classification rule looks like."""

from datetime import date
from typing import Protocol

from notes_to_budget.classification.classification_result import (
    ClassificationResult,
    EntryToClassify,
)


class ClassificationRule(Protocol):
    """A rule either decides about an entry or passes it on to the next rule."""

    name: str
    """Written into the ledger, so every decision can be traced to its rule."""

    def classify(self, entry: EntryToClassify) -> ClassificationResult | None:
        """Return the decision, or None when this rule has nothing to say."""
        ...


class CategoryFinder(Protocol):
    """Something that can name a category for a description."""

    def find_category(self, description: str, day: date) -> str | None: ...
