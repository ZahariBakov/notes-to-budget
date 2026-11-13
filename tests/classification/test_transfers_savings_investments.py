from decimal import Decimal

from notes_to_budget.domain.transaction_type import TransactionType


def test_money_moved_between_own_accounts_is_a_transfer_not_an_expense(classify_one):
    transfer = classify_one("- 300 - from card to cash")

    assert transfer.transaction_type is TransactionType.TRANSFER
    assert transfer.amount == Decimal("300")
    assert transfer.from_account_code == "B"
    assert transfer.to_account_code == "C"
    assert transfer.category_name == ""
    assert transfer.decided_by == "transfer_rule"
    assert not transfer.needs_review


def test_the_longest_account_name_wins(classify_one):
    transfer = classify_one("- 200 - from credit card to Revolut")

    assert (transfer.from_account_code, transfer.to_account_code) == ("CC", "R")


def test_account_codes_and_any_letter_case_work_in_a_transfer(classify_one):
    transfer = classify_one("- 50 - From B to c")

    assert (transfer.from_account_code, transfer.to_account_code) == ("B", "C")


def test_a_transfer_may_name_only_the_destination_when_the_account_is_written(classify_one):
    transfer = classify_one("- 300 - to credit card - B")

    assert transfer.transaction_type is TransactionType.TRANSFER
    assert (transfer.from_account_code, transfer.to_account_code) == ("B", "CC")


def test_a_short_transfer_phrase_inside_a_longer_description_is_not_a_transfer(classify_one):
    expense = classify_one("- 9 - lunch on the way to cash machine - R")

    assert expense.transaction_type is TransactionType.EXPENSE


def test_a_transfer_with_other_words_is_kept_but_flagged(classify_one):
    transfer = classify_one("- 63 for 60 from Revolut to cash")

    assert transfer.transaction_type is TransactionType.TRANSFER
    assert transfer.amount == Decimal("63")
    assert transfer.needs_review
    assert "fee" in transfer.note


def test_a_sentence_that_names_no_known_account_is_not_a_transfer(classify_one):
    saving = classify_one("- 500 - from savings to cash")

    assert saving.transaction_type is TransactionType.SAVING


def test_money_put_into_savings_is_a_positive_saving(classify_one):
    saving = classify_one("- 100 - saved - C")

    assert saving.transaction_type is TransactionType.SAVING
    assert saving.amount == Decimal("100")
    assert saving.category_name == "Savings"
    assert saving.from_account_code == "C"
    assert saving.decided_by == "savings_rule"
    assert not saving.needs_review


def test_money_taken_out_of_savings_is_negative_whatever_the_sign_in_the_notes(classify_one):
    with_minus = classify_one("- 500 - from savings to cash")
    with_plus = classify_one("+ 20 - to cash - from savings")

    assert with_minus.amount == Decimal("-500")
    assert with_plus.amount == Decimal("-20")


def test_the_account_of_a_saving_is_taken_from_the_words_when_not_written(classify_one):
    saving = classify_one("- 500 - from savings to cash")

    assert saving.from_account_code == "C"
    assert not saving.needs_review


def test_savings_spent_straight_away_are_flagged_because_the_expense_is_missing(classify_one):
    saving = classify_one("- 60 - from savings for Yana - C")

    assert saving.transaction_type is TransactionType.SAVING
    assert saving.needs_review
    assert "spent" in saving.note


def test_invested_money_is_an_investment(classify_one):
    investment = classify_one("- 100 - invested - R")

    assert investment.transaction_type is TransactionType.INVESTMENT
    assert investment.amount == Decimal("100")
    assert investment.category_name == "Investments"
    assert investment.decided_by == "investment_rule"


def test_money_coming_back_from_an_investment_is_negative(classify_one):
    assert classify_one("+ 290 - invested money back - R").amount == Decimal("-290")
