import pytest

from notes_to_budget.configuration.configuration_error import ConfigurationError
from notes_to_budget.configuration.notes_format_loader import load_notes_format

VALID_NOTES_FORMAT = """
    balance_line_is: morning
    newest_day_first: true
    transfer_phrases:
      - "from {from} to {to}"
    savings_phrases:
      taken_out: [from savings]
      put_in: [saved]
    investment_phrases: [invested]
    uncertain_marker: "?"
"""


def test_a_valid_notes_format_is_loaded(write_settings_file):
    notes_format = load_notes_format(write_settings_file("notes_format.yaml", VALID_NOTES_FORMAT))

    assert notes_format.balances_are_written_in_the_morning
    assert notes_format.newest_day_first
    assert notes_format.transfer_phrases == ("from {from} to {to}",)
    assert notes_format.savings_taken_out_phrases == ("from savings",)
    assert notes_format.savings_put_in_phrases == ("saved",)
    assert notes_format.investment_phrases == ("invested",)
    assert notes_format.uncertain_marker == "?"


def test_balances_may_be_written_in_the_evening(write_settings_file):
    notes_format = load_notes_format(
        write_settings_file("notes_format.yaml", "balance_line_is: evening\n")
    )

    assert not notes_format.balances_are_written_in_the_morning


def test_everything_except_the_balance_time_has_a_sensible_default(write_settings_file):
    notes_format = load_notes_format(
        write_settings_file("notes_format.yaml", "balance_line_is: morning\n")
    )

    assert notes_format.newest_day_first
    assert notes_format.uncertain_marker == "?"
    assert notes_format.transfer_phrases == ()
    assert notes_format.savings_put_in_phrases == ()


def test_an_unknown_time_for_the_balances_is_reported(write_settings_file):
    notes_format_file = write_settings_file("notes_format.yaml", "balance_line_is: noon\n")

    with pytest.raises(ConfigurationError) as problem:
        load_notes_format(notes_format_file)

    assert problem.value.message_key == "configuration.value_not_one_of"
    assert problem.value.details["allowed"] == "morning, evening"


def test_a_transfer_phrase_without_the_destination_is_reported(write_settings_file):
    notes_format_file = write_settings_file(
        "notes_format.yaml", VALID_NOTES_FORMAT.replace("from {from} to {to}", "from {from}")
    )

    with pytest.raises(ConfigurationError) as problem:
        load_notes_format(notes_format_file)

    assert problem.value.message_key == "configuration.transfer_phrase_needs_destination"
