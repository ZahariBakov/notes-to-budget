"""Rule: money put into savings or taken back out.

Savings are not an expense and not income; the ledger shows them apart.
A positive amount is money put in, a negative amount is money taken out.
"""

from collections.abc import Sequence

from notes_to_budget.classification.classification_result import (
    ClassificationResult,
    EntryToClassify,
)
from notes_to_budget.classification.text_matching import contains_any_keyword, remove_keywords
from notes_to_budget.domain.transaction_type import TransactionType
from notes_to_budget.notes_parsing.account_code_resolver import AccountCodeResolver

# Words this short ("to", "for", "в", "за") do not say what the money was for.
LONGEST_WORD_THAT_SAYS_NOTHING = 2


class SavingsRule:
    name = "savings_rule"

    def __init__(
        self,
        taken_out_phrases: Sequence[str],
        put_in_phrases: Sequence[str],
        savings_category_name: str,
        accounts: AccountCodeResolver,
    ) -> None:
        self._taken_out_phrases = taken_out_phrases
        self._put_in_phrases = put_in_phrases
        self._savings_category_name = savings_category_name
        self._accounts = accounts

    def classify(self, entry: EntryToClassify) -> ClassificationResult | None:
        # "from savings" is checked first because it contains "savings".
        if contains_any_keyword(entry.description, self._taken_out_phrases):
            amount = -entry.entry.amount
        elif contains_any_keyword(entry.description, self._put_in_phrases):
            amount = entry.entry.amount
        else:
            return None

        return ClassificationResult(
            transaction_type=TransactionType.SAVING,
            amount=amount,
            category_name=self._savings_category_name,
            from_account_code=entry.entry.account_code
            or self._accounts.find_account_named_in(entry.description)
            or "",
            review_reason_key="review.saving_with_other_words"
            if self._says_what_the_money_was_for(entry.description)
            else "",
        )

    def _says_what_the_money_was_for(self, description: str) -> bool:
        """ "from savings for the trip" is also an expense the person must add."""
        other_text = remove_keywords(description, (*self._taken_out_phrases, *self._put_in_phrases))
        other_text = self._accounts.remove_account_names_from(other_text)
        other_words = [word.strip(".,-") for word in other_text.split()]
        return any(len(word) > LONGEST_WORD_THAT_SAYS_NOTHING for word in other_words)
