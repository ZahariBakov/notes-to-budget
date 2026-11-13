from decimal import Decimal

import pytest

from notes_to_budget.notes_parsing.account_code_resolver import AccountCodeResolver
from notes_to_budget.notes_parsing.entry_line_parser import (
    looks_like_entry_line,
    parse_entry_line,
)
from notes_to_budget.notes_parsing.parsing_problem import LineNotUnderstood


@pytest.fixture
def read_entry(accounts):
    def read(line_text):
        return parse_entry_line(
            line_text,
            line_number=7,
            account_code_resolver=AccountCodeResolver(accounts),
            uncertain_marker="?",
        )

    return read


def test_an_expense_has_an_amount_a_description_and_an_account(read_entry):
    entry = read_entry(" - 249 - bills - B")

    assert not entry.is_money_in
    assert entry.amount == Decimal("249")
    assert entry.description == "bills"
    assert entry.account_code == "B"
    assert not entry.is_uncertain
    assert entry.line_number == 7
    assert entry.original_text == "- 249 - bills - B"


def test_a_plus_sign_means_money_coming_in(read_entry):
    entry = read_entry(" + 340 - rent - C")

    assert entry.is_money_in
    assert entry.amount == Decimal("340")
    assert entry.account_code == "C"


def test_an_entry_without_an_account_keeps_its_whole_description(read_entry):
    entry = read_entry(" - 300 - from credit card to Revolut")

    assert entry.description == "from credit card to Revolut"
    assert entry.account_code is None


def test_a_last_part_that_is_not_an_account_stays_in_the_description(read_entry):
    entry = read_entry(" - 100 - gift for George - from savings")

    assert entry.description == "gift for George - from savings"
    assert entry.account_code is None


def test_amount_and_description_written_in_the_wrong_order_are_understood(read_entry):
    entry = read_entry(" - lunch - 10 - R")

    assert entry.amount == Decimal("10")
    assert entry.description == "lunch"
    assert entry.account_code == "R"


def test_a_forgotten_dash_after_the_amount_is_understood(read_entry):
    entry = read_entry(" - 5 socks John - C")

    assert entry.amount == Decimal("5")
    assert entry.description == "socks John"
    assert entry.account_code == "C"


def test_a_dash_glued_to_the_amount_is_understood(read_entry):
    entry = read_entry(" - 56- lunch - R")

    assert entry.amount == Decimal("56")
    assert entry.description == "lunch"


def test_a_long_dash_from_the_phone_keyboard_is_understood(read_entry):
    entry = read_entry(" + 2382 —salary - B")

    assert entry.is_money_in
    assert entry.amount == Decimal("2382")
    assert entry.description == "salary"
    assert entry.account_code == "B"


def test_an_entry_may_have_no_description(read_entry):
    entry = read_entry(" + 2700.46 - B")

    assert entry.amount == Decimal("2700.46")
    assert entry.description == ""
    assert entry.account_code == "B"


def test_the_account_is_recognised_whatever_the_letter_case_or_typo(read_entry):
    assert read_entry(" - 4 - coffee - r").account_code == "R"
    assert read_entry(" + 10 - from Ferry - E").account_code == "R"


@pytest.mark.parametrize(
    "line_text", [" - 17 - lunch - C -?", " - 17 - lunch - C - ?", " - 17 - lunch - C ?"]
)
def test_a_question_mark_at_the_end_marks_the_entry_as_uncertain(read_entry, line_text):
    entry = read_entry(line_text)

    assert entry.is_uncertain
    assert entry.amount == Decimal("17")
    assert entry.description == "lunch"
    assert entry.account_code == "C"


def test_a_hyphen_inside_a_word_does_not_split_the_description(read_entry):
    entry = read_entry(" - 3 - Coca-Cola - C")

    assert entry.description == "Coca-Cola"


def test_an_amount_inside_the_words_after_the_first_amount_stays_in_the_description(read_entry):
    entry = read_entry(" - 63 for 60 from Revolut to cash")

    assert entry.amount == Decimal("63")
    assert entry.description == "for 60 from Revolut to cash"
    assert entry.account_code is None


@pytest.mark.parametrize("line_text", [" - lunch - R", " - ", " + rent"])
def test_an_entry_without_an_amount_is_refused(read_entry, line_text):
    with pytest.raises(LineNotUnderstood) as problem:
        read_entry(line_text)

    assert problem.value.message_key == "notes.problem.amount_missing"


@pytest.mark.parametrize(
    "line_text", [" - 12 - lunch - R", "+ 300 - rent - C", " – 5 - coffee - C"]
)
def test_lines_that_start_with_a_sign_are_entries(line_text):
    assert looks_like_entry_line(line_text)


@pytest.mark.parametrize("line_text", ["14 - 120 / 340 / 1500", "lunch 12", ""])
def test_other_lines_are_not_entries(line_text):
    assert not looks_like_entry_line(line_text)
