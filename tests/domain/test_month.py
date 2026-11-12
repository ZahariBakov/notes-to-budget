from datetime import date

import pytest

from notes_to_budget.domain.month import Month


def test_month_is_read_from_year_dash_month_text():
    assert Month.from_text("2026-11") == Month(2026, 11)
    assert Month.from_text(" 2026-3 ") == Month(2026, 3)


@pytest.mark.parametrize("unclear_text", ["November 2026", "2026/11", "11-2026", "", "2026-13"])
def test_unclear_month_text_is_refused_with_an_explanation(unclear_text):
    with pytest.raises(ValueError):
        Month.from_text(unclear_text)


def test_month_knows_its_first_and_last_day():
    assert Month(2026, 2).first_day == date(2026, 2, 1)
    assert Month(2026, 2).last_day == date(2026, 2, 28)
    assert Month(2028, 2).last_day == date(2028, 2, 29)


def test_month_tells_whether_a_day_belongs_to_it():
    october = Month(2026, 10)

    assert october.contains(date(2026, 10, 1))
    assert october.contains(date(2026, 10, 31))
    assert not october.contains(date(2026, 11, 1))


def test_next_and_previous_month_cross_the_year_boundary():
    assert Month(2026, 12).next_month() == Month(2027, 1)
    assert Month(2026, 1).previous_month() == Month(2025, 12)
    assert Month(2026, 5).next_month() == Month(2026, 6)


def test_month_of_a_day():
    assert Month.of_day(date(2026, 8, 19)) == Month(2026, 8)


def test_month_is_written_with_a_two_digit_month_number():
    assert str(Month(2026, 3)) == "2026-03"


def test_months_are_ordered_by_time():
    assert Month(2025, 12) < Month(2026, 1) < Month(2026, 2)
