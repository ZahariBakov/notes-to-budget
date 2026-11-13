"""How one person writes their notes."""

from dataclasses import dataclass


@dataclass(frozen=True)
class NotesFormat:
    balances_are_written_in_the_morning: bool
    """True: the balances line shows the money before that day's entries."""
    newest_day_first: bool
    uncertain_marker: str
    """The mark a person adds to an entry they are not sure about."""
    transfer_phrases: tuple[str, ...]
    """Sentences for moving money between accounts, with {from} and {to}."""
    savings_taken_out_phrases: tuple[str, ...]
    savings_put_in_phrases: tuple[str, ...]
    investment_phrases: tuple[str, ...]
