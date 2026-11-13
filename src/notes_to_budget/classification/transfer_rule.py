"""Rule: money moved between two of the person's own accounts.

"from card to cash" is not an expense. The sentences come from the
person's settings, with ``{from}`` and ``{to}`` standing for accounts.
"""

import re
from collections.abc import Sequence
from dataclasses import dataclass

from notes_to_budget.classification.classification_result import (
    ClassificationResult,
    EntryToClassify,
)
from notes_to_budget.domain.transaction_type import TransactionType
from notes_to_budget.notes_parsing.account_code_resolver import AccountCodeResolver

SOURCE_PLACEHOLDER = "{from}"
DESTINATION_PLACEHOLDER = "{to}"


@dataclass(frozen=True)
class _TransferPhrase:
    pattern: re.Pattern[str]
    names_the_source_account: bool


class TransferRule:
    name = "transfer_rule"

    def __init__(self, transfer_phrases: Sequence[str], accounts: AccountCodeResolver) -> None:
        self._accounts = accounts
        self._phrases = [self._compile(phrase) for phrase in transfer_phrases]

    def classify(self, entry: EntryToClassify) -> ClassificationResult | None:
        for phrase in self._phrases:
            result = self._classify_with(phrase, entry)
            if result is not None:
                return result
        return None

    def _classify_with(
        self, phrase: _TransferPhrase, entry: EntryToClassify
    ) -> ClassificationResult | None:
        description = entry.description.strip()
        if phrase.names_the_source_account:
            match = phrase.pattern.search(description)
        else:
            # A short phrase like "to {to}" could appear inside any sentence,
            # so it must be the whole description.
            match = phrase.pattern.fullmatch(description)
        if match is None:
            return None

        to_account_code = self._accounts.resolve(match.group("to"))
        if phrase.names_the_source_account:
            from_account_code = self._accounts.resolve(match.group("from"))
        else:
            from_account_code = entry.entry.account_code
        if not from_account_code or not to_account_code or from_account_code == to_account_code:
            return None

        has_other_words = bool(description.replace(match.group(0), "").strip())
        return ClassificationResult(
            transaction_type=TransactionType.TRANSFER,
            amount=entry.entry.amount,
            from_account_code=from_account_code,
            to_account_code=to_account_code,
            review_reason_key="review.transfer_with_other_words" if has_other_words else "",
        )

    def _compile(self, phrase: str) -> _TransferPhrase:
        """Turn "from {from} to {to}" into a pattern that finds the two accounts."""
        any_account = "|".join(
            re.escape(way_of_writing) for way_of_writing in self._accounts.all_ways_of_writing()
        )
        pattern_text = re.escape(phrase).replace(r"\ ", r"\s+")
        pattern_text = pattern_text.replace(
            re.escape(SOURCE_PLACEHOLDER), rf"(?P<from>{any_account})"
        ).replace(re.escape(DESTINATION_PLACEHOLDER), rf"(?P<to>{any_account})")
        return _TransferPhrase(
            pattern=re.compile(rf"(?<!\w){pattern_text}(?!\w)", re.IGNORECASE),
            names_the_source_account=SOURCE_PLACEHOLDER in phrase,
        )
