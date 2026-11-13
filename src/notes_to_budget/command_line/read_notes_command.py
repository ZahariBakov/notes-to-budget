"""The ``read-notes`` command: show what the program understands in a notes file.

It changes nothing; it is a way to check your notes (and the program)
before the entries are categorised.
"""

import argparse
import os
from pathlib import Path

from notes_to_budget.configuration.configuration import Configuration, load_configuration
from notes_to_budget.configuration.data_folder import DataFolder, find_data_folder
from notes_to_budget.domain.month import Month
from notes_to_budget.localization.translator import Translator
from notes_to_budget.notes_parsing.notes_file_reader import read_notes_lines
from notes_to_budget.notes_parsing.notes_parser import parse_notes
from notes_to_budget.notes_parsing.parsed_notes import ParsedNotes
from notes_to_budget.user_facing_error import UserFacingError


def add_read_notes_command(commands: argparse._SubParsersAction) -> None:
    command = commands.add_parser(
        "read-notes",
        help="show what is understood in a notes file (changes nothing)",
        description="Read one notes file and list the lines that need your attention.",
    )
    command.add_argument("notes_file", help="the notes file, or its name inside your notes folder")
    command.add_argument(
        "--month",
        help="the month of the file as YEAR-MONTH, for example 2026-11; "
        "needed when the days are written without month and year",
    )
    command.add_argument(
        "--show-entries", action="store_true", help="also list every entry that was read"
    )
    command.add_argument(
        "--data-folder",
        help="your data folder (or set the NOTES_TO_BUDGET_DATA_FOLDER environment variable)",
    )
    command.set_defaults(run_command=run_read_notes_command)


def run_read_notes_command(arguments: argparse.Namespace) -> int:
    data_folder = find_data_folder(arguments.data_folder, os.environ)
    configuration = load_configuration(data_folder)
    translator = Translator(configuration.settings.language)

    notes_file = find_notes_file(arguments.notes_file, data_folder, configuration)
    parsed_notes = parse_notes(
        read_notes_lines(notes_file),
        file_name=notes_file.name,
        month_of_the_file=read_month_option(arguments.month),
        accounts=configuration.accounts,
        notes_format=configuration.notes_format,
        currency_symbol=configuration.settings.currency_symbol,
    )

    for line in describe_parsed_notes(parsed_notes, translator, arguments.show_entries):
        print(line)
    return 0


def find_notes_file(
    written_path: str, data_folder: DataFolder, configuration: Configuration
) -> Path:
    """Accept a full path, or just a file name inside the notes folder."""
    notes_file = Path(written_path).expanduser()
    if notes_file.is_file():
        return notes_file
    file_in_notes_folder = (
        data_folder.folder_named(configuration.settings.notes_folder_name) / written_path
    )
    return file_in_notes_folder if file_in_notes_folder.is_file() else notes_file


def read_month_option(written_month: str | None) -> Month | None:
    if written_month is None:
        return None
    try:
        return Month.from_text(written_month)
    except ValueError:
        raise UserFacingError("notes.month_not_understood", month=written_month) from None


def describe_parsed_notes(
    parsed_notes: ParsedNotes, translator: Translator, show_entries: bool
) -> list[str]:
    lines = [
        translator.translate(
            "notes.summary",
            file=parsed_notes.file_name,
            days=len(parsed_notes.days),
            entries=parsed_notes.number_of_entries(),
        )
    ]
    if show_entries:
        lines.extend(_describe_entries(parsed_notes, translator))

    if not parsed_notes.problems:
        lines.append(translator.translate("notes.no_problems"))
        return lines

    lines.append(
        translator.translate("notes.problems_heading", problems=len(parsed_notes.problems))
    )
    for problem in parsed_notes.problems:
        explanation = translator.translate(problem.message_key, **problem.details)
        lines.append(
            translator.translate(
                "notes.problem_line", line_number=problem.line_number, explanation=explanation
            )
        )
        lines.append(
            translator.translate("notes.problem_original_line", line_text=problem.line_text)
        )
    return lines


def _describe_entries(parsed_notes: ParsedNotes, translator: Translator) -> list[str]:
    lines = [translator.translate("notes.entries_heading")]
    for parsed_day in parsed_notes.days:
        for entry in parsed_day.entries:
            lines.append(
                translator.translate(
                    "notes.entry_line",
                    day=parsed_day.day.isoformat(),
                    sign="+" if entry.is_money_in else "-",
                    amount=entry.amount,
                    description=entry.description,
                    account=entry.account_code or translator.translate("notes.account_not_written"),
                    uncertain=translator.translate("notes.uncertain_mark")
                    if entry.is_uncertain
                    else "",
                )
            )
    return lines
