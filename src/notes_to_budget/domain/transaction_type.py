"""The kinds of money movement the program knows about."""

from enum import StrEnum


class TransactionType(StrEnum):
    """What a transaction means for the budget.

    The values are language-neutral codes, so the same ledger file can be
    shown in any language.
    """

    EXPENSE = "expense"
    INCOME = "income"
    TRANSFER = "transfer"
    """Money moved between two of your own accounts; not an expense."""
    SAVING = "saving"
    """Positive: put into savings. Negative: taken back out."""
    INVESTMENT = "investment"
