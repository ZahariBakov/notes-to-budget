"""A place where money is kept: cash, a bank card, an online wallet."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Account:
    code: str
    """The short code written in the notes, for example ``C`` for cash."""
    name: str
    is_reconciled: bool
    """Whether the notes carry a balance for this account to check against."""
    balance_position: int | None = None
    """Position of this account in the balances line of the notes (1 = first)."""
    also_written_as: tuple[str, ...] = ()
    """Other ways the account appears in the notes: words or frequent typos."""
    is_credit_card: bool = False
    """Money moved out of this account is owed until it is paid back."""
