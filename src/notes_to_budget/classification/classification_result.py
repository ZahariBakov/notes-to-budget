"""What a rule decided about one entry."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from notes_to_budget.domain.transaction_type import TransactionType
from notes_to_budget.notes_parsing.parsed_notes import ParsedEntry


@dataclass(frozen=True)
class EntryToClassify:
    """One entry from the notes, together with the day it was written under."""

    day: date
    entry: ParsedEntry

    @property
    def description(self) -> str:
        return self.entry.description

    @property
    def is_money_in(self) -> bool:
        return self.entry.is_money_in

    def amount_as_an_expense(self) -> Decimal:
        """Money out is a positive expense; money back is a negative one (a refund)."""
        return -self.entry.amount if self.entry.is_money_in else self.entry.amount


@dataclass(frozen=True)
class ClassificationResult:
    transaction_type: TransactionType
    amount: Decimal
    """The amount as it goes into the ledger (see ``Transaction``)."""
    category_name: str = ""
    from_account_code: str = ""
    """Empty means: use the account written at the end of the entry."""
    to_account_code: str = ""
    is_one_off: bool = False
    review_reason_key: str = ""
    """Why a person should look at this entry; empty when the rule is sure."""
