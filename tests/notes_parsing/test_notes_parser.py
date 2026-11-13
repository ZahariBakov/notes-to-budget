from datetime import date
from decimal import Decimal

from notes_to_budget.domain.month import Month


def problem_keys(parsed_notes):
    return [(problem.line_number, problem.message_key) for problem in parsed_notes.problems]


def test_days_and_their_entries_are_read_in_the_order_of_the_file(parse_text):
    parsed_notes = parse_text(
        """
        02 - 47 / 153 / 1500
         + 2000 - salary - B
         - 8 - lunch - R

        01 - 50 / 200 / 1500
         - 12 - lunch - R
        """
    )

    assert [parsed_day.day for parsed_day in parsed_notes.days] == [
        date(2026, 3, 2),
        date(2026, 3, 1),
    ]
    assert [entry.description for entry in parsed_notes.days[0].entries] == ["salary", "lunch"]
    assert parsed_notes.number_of_entries() == 3
    assert parsed_notes.problems == ()


def test_balances_are_matched_to_the_reconciled_accounts_by_position(parse_text):
    parsed_notes = parse_text("14 - 120 / 340 / 1500")
    balance = parsed_notes.days[0].balance

    assert balance.day == date(2026, 3, 14)
    assert balance.amount_for("C") == Decimal("120")
    assert balance.amount_for("R") == Decimal("340")
    assert balance.amount_for("B") == Decimal("1500")
    assert balance.amount_for("CC") is None


def test_a_day_without_balances_still_holds_its_entries(parse_text):
    parsed_notes = parse_text(
        """
        06 -
         - 300 - from credit card to Revolut
        """
    )

    assert parsed_notes.days[0].balance is None
    assert len(parsed_notes.days[0].entries) == 1
    assert parsed_notes.problems == ()


def test_a_line_that_is_neither_a_day_nor_an_entry_is_reported_not_dropped(parse_text):
    parsed_notes = parse_text(
        """
        02 - 47 / 153 / 1500
         remember to ask about the rent
         - 8 - lunch - R
        """
    )

    assert problem_keys(parsed_notes) == [(3, "notes.problem.line_not_understood")]
    assert parsed_notes.problems[0].line_text == "remember to ask about the rent"
    assert parsed_notes.number_of_entries() == 1


def test_an_entry_with_a_forgotten_sign_is_not_taken_for_a_day(parse_text):
    parsed_notes = parse_text(
        """
        02 - 47 / 153 / 1500
        12 - lunch - R
         - 8 - coffee - R
        """
    )

    assert problem_keys(parsed_notes) == [(3, "notes.problem.line_not_understood")]
    assert len(parsed_notes.days) == 1
    assert parsed_notes.days[0].entries[0].description == "coffee"


def test_an_entry_before_the_first_day_is_reported(parse_text):
    parsed_notes = parse_text(
        """
         - 8 - lunch - R
        02 - 47 / 153 / 1500
        """
    )

    assert problem_keys(parsed_notes) == [(2, "notes.problem.entry_without_day")]


def test_entries_under_a_date_that_does_not_exist_are_not_moved_to_another_day(parse_text):
    parsed_notes = parse_text(
        """
        31 - 1 / 2 / 3
         - 5 - coffee - C
        30 - 4 / 5 / 6
         - 9 - lunch - R
        """,
        month_of_the_file=Month(2026, 4),
    )

    assert problem_keys(parsed_notes) == [
        (2, "notes.problem.date_not_valid"),
        (3, "notes.problem.entry_without_day"),
    ]
    assert [parsed_day.day for parsed_day in parsed_notes.days] == [date(2026, 4, 30)]
    assert parsed_notes.number_of_entries() == 1


def test_unreadable_balances_are_reported_but_the_day_and_entries_are_kept(parse_text):
    parsed_notes = parse_text(
        """
        11 - 279 - 59 / 236
         - 8 - lunch - R
        """
    )

    assert problem_keys(parsed_notes) == [(2, "notes.problem.balances_not_understood")]
    assert parsed_notes.problems[0].details == {"expected": 3}
    assert parsed_notes.days[0].balance is None
    assert parsed_notes.number_of_entries() == 1


def test_an_entry_without_an_amount_is_reported_and_the_rest_is_read(parse_text):
    parsed_notes = parse_text(
        """
        02 - 47 / 153 / 1500
         - lunch - R
         - 8 - coffee - R
        """
    )

    assert problem_keys(parsed_notes) == [(3, "notes.problem.amount_missing")]
    assert parsed_notes.number_of_entries() == 1


def test_a_day_written_twice_is_reported(parse_text):
    parsed_notes = parse_text(
        """
        22 - 1 / 2 / 3
         - 8 - lunch - R
        22 - 1 / 2 / 3
         - 5 - coffee - C
        """
    )

    assert problem_keys(parsed_notes) == [(4, "notes.problem.day_repeated")]
    assert parsed_notes.problems[0].details == {"day": "2026-03-22"}
    assert parsed_notes.number_of_entries() == 2


def test_a_day_out_of_order_is_reported_because_its_date_may_be_wrong(parse_text):
    parsed_notes = parse_text(
        """
        06 -
         - 300 - from credit card to Revolut
        30 - 5 / 42 / 2520
        29 - 10 / 57 / 2521
        """
    )

    assert problem_keys(parsed_notes) == [(4, "notes.problem.day_out_of_order_newest_first")]


def test_only_day_numbers_without_a_month_are_reported_line_by_line(parse_text):
    parsed_notes = parse_text(
        """
        02 - 47 / 153 / 1500
         - 8 - lunch - R
        """,
        month_of_the_file=None,
    )

    assert problem_keys(parsed_notes) == [
        (2, "notes.problem.month_unknown"),
        (3, "notes.problem.entry_without_day"),
    ]
    assert parsed_notes.days == ()


def test_full_dates_need_no_month_of_the_file(parse_text):
    parsed_notes = parse_text(
        """
        02.10.26 - 14 / 220 / 1577
         - 3 - lunch - R
        01.10.26 - 20 / 230 / 1577
        """,
        month_of_the_file=None,
    )

    assert [parsed_day.day for parsed_day in parsed_notes.days] == [
        date(2026, 10, 2),
        date(2026, 10, 1),
    ]
    assert parsed_notes.problems == ()


def test_the_currency_symbol_after_a_number_is_ignored(parse_text):
    parsed_notes = parse_text(
        """
        23 - 164 / 338€ / 4155
         - 115€ - skating card - C
         - 3 € - bread - R
        """
    )
    entries = parsed_notes.days[0].entries

    assert parsed_notes.problems == ()
    assert parsed_notes.days[0].balance.amount_for("R") == Decimal("338")
    assert [entry.amount for entry in entries] == [Decimal("115"), Decimal("3")]
    assert entries[0].original_text == "- 115€ - skating card - C"


def test_a_day_that_is_not_in_the_month_of_the_file_is_kept_but_reported(parse_text):
    parsed_notes = parse_text(
        """
        02.09.26 - 2 / 135 / 1172
         - 8 - groceries - R
        01.06 - 22 / 176 / 1372
         - 200 - from card to credit card
        """,
        month_of_the_file=Month(2026, 9),
    )

    assert problem_keys(parsed_notes) == [(4, "notes.problem.day_in_another_month")]
    assert parsed_notes.problems[0].details == {"day": "2026-06-01", "month": "2026-09"}
    assert parsed_notes.number_of_entries() == 2


def test_a_year_typed_wrong_is_noticed_because_the_day_leaves_the_month(parse_text):
    parsed_notes = parse_text(
        """
        31.10.16 - 356 / 129 / 1243
        30.10.26 - 346 / 202 / 1243
        """,
        month_of_the_file=Month(2026, 10),
    )

    assert (2, "notes.problem.day_in_another_month") in problem_keys(parsed_notes)
