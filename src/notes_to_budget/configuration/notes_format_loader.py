"""Reads ``notes_format.yaml``."""

from pathlib import Path

from notes_to_budget.configuration.configuration_error import ConfigurationError
from notes_to_budget.configuration.notes_format import NotesFormat
from notes_to_budget.configuration.yaml_file_reader import read_yaml_mapping
from notes_to_budget.configuration.yaml_values import (
    read_optional_text,
    read_optional_text_list,
    read_optional_yes_or_no,
    read_required_text,
    require_named_values,
)

BALANCES_IN_THE_MORNING = "morning"
BALANCES_IN_THE_EVENING = "evening"
DESTINATION_PLACEHOLDER = "{to}"
DEFAULT_UNCERTAIN_MARKER = "?"


def load_notes_format(notes_format_file: Path) -> NotesFormat:
    values = read_yaml_mapping(notes_format_file)
    savings_phrases = require_named_values(
        values.get("savings_phrases") or {}, notes_format_file, "savings_phrases"
    )

    notes_format = NotesFormat(
        balances_are_written_in_the_morning=_read_when_balances_are_written(
            values, notes_format_file
        ),
        newest_day_first=read_optional_yes_or_no(
            values, "newest_day_first", notes_format_file, default=True
        ),
        uncertain_marker=read_optional_text(
            values, "uncertain_marker", notes_format_file, default=DEFAULT_UNCERTAIN_MARKER
        ),
        transfer_phrases=read_optional_text_list(values, "transfer_phrases", notes_format_file),
        savings_taken_out_phrases=read_optional_text_list(
            savings_phrases, "taken_out", notes_format_file, "savings_phrases"
        ),
        savings_put_in_phrases=read_optional_text_list(
            savings_phrases, "put_in", notes_format_file, "savings_phrases"
        ),
        investment_phrases=read_optional_text_list(values, "investment_phrases", notes_format_file),
    )
    _check_every_transfer_phrase_names_the_destination(notes_format, notes_format_file)
    return notes_format


def _read_when_balances_are_written(values: dict, notes_format_file: Path) -> bool:
    when_written = read_required_text(values, "balance_line_is", notes_format_file)
    allowed_answers = (BALANCES_IN_THE_MORNING, BALANCES_IN_THE_EVENING)
    if when_written not in allowed_answers:
        raise ConfigurationError(
            "configuration.value_not_one_of",
            file=notes_format_file,
            place="balance_line_is",
            allowed=", ".join(allowed_answers),
        )
    return when_written == BALANCES_IN_THE_MORNING


def _check_every_transfer_phrase_names_the_destination(
    notes_format: NotesFormat, notes_format_file: Path
) -> None:
    for transfer_phrase in notes_format.transfer_phrases:
        if DESTINATION_PLACEHOLDER not in transfer_phrase:
            raise ConfigurationError(
                "configuration.transfer_phrase_needs_destination",
                file=notes_format_file,
                phrase=transfer_phrase,
            )
