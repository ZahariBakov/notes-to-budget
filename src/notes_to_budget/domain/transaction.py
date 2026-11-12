"""One movement of money: a single row of the ledger."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from notes_to_budget.domain.transaction_type import TransactionType


@dataclass(frozen=True)
class Transaction:
    """One movement of money.

    A negative ``amount`` on an expense means money that came back
    (a refund), which lowers the total of its category.
    """

    day: date
    amount: Decimal
    description: str
    transaction_type: TransactionType
    from_account_code: str
    to_account_code: str = ""
    category_name: str = ""
    is_one_off: bool = False
    needs_review: bool = False
    note: str = ""
    decided_by: str = ""
    """Which rule chose the category and type; helps to trace mistakes."""
    source: str = ""
    """Where the entry came from, for example ``October-2026.txt:214``."""

    def __post_init__(self) -> None:
        if self.is_transfer and not self.to_account_code:
            raise ValueError("A transfer needs the account the money goes to.")
        if not self.is_transfer and self.to_account_code:
            raise ValueError("Only a transfer can have an account the money goes to.")

    @property
    def is_transfer(self) -> bool:
        return self.transaction_type is TransactionType.TRANSFER
