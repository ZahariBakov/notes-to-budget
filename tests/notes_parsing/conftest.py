"""Accounts and a notes format shared by the note-reading tests."""

from collections.abc import Callable

import pytest

from notes_to_budget.configuration.notes_format import NotesFormat
from notes_to_budget.domain.account import Account
from notes_to_budget.domain.account_catalog import AccountCatalog
from notes_to_budget.domain.month import Month
from notes_to_budget.notes_parsing.notes_file_reader import NumberedLine
from notes_to_budget.notes_parsing.notes_parser import parse_notes
from notes_to_budget.notes_parsing.parsed_notes import ParsedNotes


@pytest.fixture
def accounts() -> AccountCatalog:
    return AccountCatalog(
        accounts=(
            Account("C", "Cash", is_reconciled=True, balance_position=1, also_written_as=("cash",)),
            Account(
                "R",
                "Online wallet",
                is_reconciled=True,
                balance_position=2,
                also_written_as=("Revolut", "E"),
            ),
            Account("B", "Bank card", is_reconciled=True, balance_position=3),
            Account("CC", "Credit card", is_reconciled=False, also_written_as=("credit card",)),
        )
    )


@pytest.fixture
def notes_format() -> NotesFormat:
    return NotesFormat(
        balances_are_written_in_the_morning=True,
        newest_day_first=True,
        uncertain_marker="?",
        transfer_phrases=("from {from} to {to}",),
        savings_taken_out_phrases=("from savings",),
        savings_put_in_phrases=("saved",),
        investment_phrases=("invested",),
    )


@pytest.fixture
def parse_text(accounts, notes_format) -> Callable[..., ParsedNotes]:
    """Parse notes written inside a test, as if they were a file for March 2026."""

    def parse(notes_text: str, month_of_the_file: Month | None = Month(2026, 3)) -> ParsedNotes:  # noqa: B008
        lines = [
            NumberedLine(number=line_number, text=line_text)
            for line_number, line_text in enumerate(notes_text.splitlines(), start=1)
            if line_text.strip()
        ]
        return parse_notes(
            lines,
            file_name="test-notes.txt",
            month_of_the_file=month_of_the_file,
            accounts=accounts,
            notes_format=notes_format,
            currency_symbol="€",
        )

    return parse
