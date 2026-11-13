"""The ``preview`` command: show how the entries of a notes file would be classified.

It changes nothing; it lets a person see which rule decided what and
which entries will need their review.
"""

import argparse
import os

from notes_to_budget.classification.rule_set_builder import build_classification_rules
from notes_to_budget.classification.transaction_classifier import classify_parsed_notes
from notes_to_budget.command_line.read_notes_command import find_notes_file, read_month_option
from notes_to_budget.configuration.configuration import load_configuration
from notes_to_budget.configuration.data_folder import find_data_folder
from notes_to_budget.domain.transaction import Transaction
from notes_to_budget.localization.translator import Translator
from notes_to_budget.notes_parsing.notes_file_reader import read_notes_lines
from notes_to_budget.notes_parsing.notes_parser import parse_notes


def add_preview_command(commands: argparse._SubParsersAction) -> None:
    command = commands.add_parser(
        "preview",
        help="show how the entries of a notes file would be classified (changes nothing)",
        description="Read one notes file and show the type and category chosen for every entry.",
    )
    command.add_argument("notes_file", help="the notes file, or its name inside your notes folder")
    command.add_argument(
        "--month",
        help="the month of the file as YEAR-MONTH, for example 2026-11; "
        "needed when the days are written without month and year",
    )
    command.add_argument(
        "--only-review", action="store_true", help="list only the entries that need your review"
    )
    command.add_argument(
        "--data-folder",
        help="your data folder (or set the NOTES_TO_BUDGET_DATA_FOLDER environment variable)",
    )
    command.set_defaults(run_command=run_preview_command)


def run_preview_command(arguments: argparse.Namespace) -> int:
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
    transactions = classify_parsed_notes(
        parsed_notes, build_classification_rules(configuration), translator
    )

    for line in describe_transactions(transactions, translator, arguments.only_review):
        print(line)
    print(
        translator.translate(
            "preview.summary",
            file=parsed_notes.file_name,
            entries=len(transactions),
            review=sum(1 for transaction in transactions if transaction.needs_review),
        )
    )
    if parsed_notes.problems:
        print(translator.translate("preview.unread_lines", problems=len(parsed_notes.problems)))
    return 0


def describe_transactions(
    transactions: list[Transaction], translator: Translator, only_those_to_review: bool
) -> list[str]:
    lines = []
    for transaction in transactions:
        if only_those_to_review and not transaction.needs_review:
            continue
        lines.append(
            translator.translate(
                "preview.transaction_line",
                day=transaction.day.isoformat(),
                type=translator.translate(f"types.{transaction.transaction_type}"),
                amount=transaction.amount,
                description=transaction.description,
                decision=_describe_decision(transaction, translator),
                rule=transaction.decided_by,
            )
        )
        if transaction.needs_review:
            lines.append(translator.translate("preview.review_line", note=transaction.note))
    return lines


def _describe_decision(transaction: Transaction, translator: Translator) -> str:
    if transaction.is_transfer:
        return f"{transaction.from_account_code} → {transaction.to_account_code}"
    return transaction.category_name or translator.translate("preview.no_category")
