from datetime import date
from decimal import Decimal

import pytest

from notes_to_budget.domain.month import Month
from notes_to_budget.notes_parsing.day_header_parser import (
    looks_like_day_header,
    parse_day_header,
)
from notes_to_budget.notes_parsing.parsing_problem import LineNotUnderstood

MARCH_2026 = Month(2026, 3)


def read_header(line_text, month_of_the_file=MARCH_2026, expected_number_of_balances=3):
    return parse_day_header(line_text, month_of_the_file, expected_number_of_balances)


def test_a_day_number_takes_its_month_and_year_from_the_file():
    header = read_header("14 - 120 / 340 / 1500")

    assert header.day == date(2026, 3, 14)
    assert header.balance_amounts == (Decimal("120"), Decimal("340"), Decimal("1500"))


@pytest.mark.parametrize(
    "line_text",
    ["30.09.26 - 3 / 57 / 1777", "30.09.2026 - 3 / 57 / 1777", "30.9.26-3/57/1777"],
)
def test_a_full_date_is_read_with_a_short_or_a_long_year(line_text):
    header = read_header(line_text)

    assert header.day == date(2026, 9, 30)
    assert header.balance_amounts == (Decimal("3"), Decimal("57"), Decimal("1777"))


def test_day_and_month_take_the_year_from_the_file():
    assert read_header("01.04 - 1 / 2 / 3").day == date(2026, 4, 1)


def test_a_full_date_needs_no_month_of_the_file():
    assert read_header("05.10.2026 - 217 / 190 / 1377", month_of_the_file=None).day == date(
        2026, 10, 5
    )


def test_a_negative_balance_is_read_with_or_without_a_space_after_the_minus():
    header = read_header("19 - 5 / 76 / - 691")

    assert header.balance_amounts == (Decimal("5"), Decimal("76"), Decimal("-691"))
    assert read_header("19 - 5 / -76 / 691").balance_amounts[1] == Decimal("-76")


def test_a_long_dash_from_the_phone_keyboard_is_understood():
    assert read_header("14 – 120 / 340 / 1500").day == date(2026, 3, 14)


def test_a_day_may_have_no_balances():
    header = read_header("06 - ")

    assert header.day == date(2026, 3, 6)
    assert header.balance_amounts is None
    assert not header.balances_were_not_understood


@pytest.mark.parametrize("line_text", ["07", " 07 ", "07.03.26"])
def test_a_day_may_be_written_without_the_dash(line_text):
    assert looks_like_day_header(line_text)
    assert read_header(line_text).day == date(2026, 3, 7)
    assert read_header(line_text).balance_amounts is None


def test_a_note_in_brackets_after_the_balances_is_ignored():
    header = read_header("20 - 52 / 170 / 1584 (300)")

    assert header.balance_amounts == (Decimal("52"), Decimal("170"), Decimal("1584"))


@pytest.mark.parametrize(
    "line_text", ["11 - 279 - 59 / 236", "17 - 66 / 1 - 421 / 522", "11 - 5 / 6"]
)
def test_balances_that_cannot_be_read_keep_the_day_but_are_reported(line_text):
    header = read_header(line_text)

    assert header.day.month == 3
    assert header.balance_amounts is None
    assert header.balances_were_not_understood


def test_only_a_day_number_without_a_known_month_is_refused():
    with pytest.raises(LineNotUnderstood) as problem:
        read_header("14 - 120 / 340 / 1500", month_of_the_file=None)

    assert problem.value.message_key == "notes.problem.month_unknown"


def test_a_date_that_does_not_exist_is_refused():
    with pytest.raises(LineNotUnderstood) as problem:
        read_header("30 - 1 / 2 / 3", month_of_the_file=Month(2026, 2))

    assert problem.value.message_key == "notes.problem.date_not_valid"
    assert problem.value.details == {"day": 30, "month": 2, "year": 2026}


@pytest.mark.parametrize(
    "line_text", ["14 - 120 / 340 / 1500", "30.09.26 - 3 / 57 / 1777", " 06 -"]
)
def test_lines_that_start_a_day_are_recognised(line_text):
    assert looks_like_day_header(line_text)


@pytest.mark.parametrize(
    "line_text",
    [
        " - 12 - lunch - R",
        " + 300 - rent - C",
        "12 - lunch - R",
        "just some words",
        "2026 - 1 / 2 / 3",
    ],
)
def test_lines_that_do_not_start_a_day_are_not_taken_for_one(line_text):
    assert not looks_like_day_header(line_text)
