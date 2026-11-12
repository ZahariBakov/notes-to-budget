from datetime import date
from decimal import Decimal

import pytest

from notes_to_budget.domain.transaction import Transaction
from notes_to_budget.domain.transaction_type import TransactionType


def test_an_expense_needs_only_the_account_it_was_paid_from():
    lunch = Transaction(
        day=date(2026, 10, 1),
        amount=Decimal("10"),
        description="lunch",
        transaction_type=TransactionType.EXPENSE,
        from_account_code="R",
        category_name="Food at work",
    )

    assert not lunch.is_transfer
    assert not lunch.is_one_off
    assert not lunch.needs_review


def test_a_transfer_names_both_accounts():
    withdrawal = Transaction(
        day=date(2026, 10, 11),
        amount=Decimal("100"),
        description="from card to cash",
        transaction_type=TransactionType.TRANSFER,
        from_account_code="B",
        to_account_code="C",
    )

    assert withdrawal.is_transfer


def test_a_transfer_without_a_destination_account_is_refused():
    with pytest.raises(ValueError):
        Transaction(
            day=date(2026, 10, 11),
            amount=Decimal("100"),
            description="from card to ...",
            transaction_type=TransactionType.TRANSFER,
            from_account_code="B",
        )


def test_only_a_transfer_may_have_a_destination_account():
    with pytest.raises(ValueError):
        Transaction(
            day=date(2026, 10, 1),
            amount=Decimal("10"),
            description="lunch",
            transaction_type=TransactionType.EXPENSE,
            from_account_code="R",
            to_account_code="C",
        )


def test_transaction_types_are_stored_as_language_neutral_codes():
    assert TransactionType("expense") is TransactionType.EXPENSE
    assert str(TransactionType.SAVING) == "saving"
