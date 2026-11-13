from decimal import Decimal

import pytest

from notes_to_budget.notes_parsing.amount_parser import (
    parse_amount,
    split_amount_from_following_words,
)


@pytest.mark.parametrize(
    ("written", "expected"),
    [
        ("12", "12"),
        (" 249 ", "249"),
        ("37.44", "37.44"),
        ("16,25", "16.25"),
        ("2700.46", "2700.46"),
    ],
)
def test_amounts_are_read_with_a_dot_or_a_comma(written, expected):
    assert parse_amount(written) == Decimal(expected)


@pytest.mark.parametrize("not_an_amount", ["", "lunch", "12 lunch", "-5", "1.2.3", "5€"])
def test_text_that_is_not_only_an_amount_is_not_read(not_an_amount):
    assert parse_amount(not_an_amount) is None


def test_amount_is_split_from_the_words_that_follow_it():
    assert split_amount_from_following_words("5 socks for John") == (Decimal("5"), "socks for John")
    assert split_amount_from_following_words("63 for 60 from wallet to cash") == (
        Decimal("63"),
        "for 60 from wallet to cash",
    )


@pytest.mark.parametrize("text", ["5", "socks 5", "socks"])
def test_text_that_does_not_start_with_an_amount_and_words_is_not_split(text):
    assert split_amount_from_following_words(text) is None
