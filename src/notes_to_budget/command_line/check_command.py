"""The ``check`` command: read the settings and say whether they are valid."""

import argparse
import os

from notes_to_budget.configuration.configuration import Configuration, load_configuration
from notes_to_budget.configuration.data_folder import find_data_folder
from notes_to_budget.localization.translator import Translator


def add_check_command(commands: argparse._SubParsersAction) -> None:
    command = commands.add_parser(
        "check",
        help="check that your settings are valid",
        description="Read the settings in your data folder and report any problem.",
    )
    command.add_argument(
        "--data-folder",
        help="your data folder (or set the NOTES_TO_BUDGET_DATA_FOLDER environment variable)",
    )
    command.set_defaults(run_command=run_check_command)


def run_check_command(arguments: argparse.Namespace) -> int:
    data_folder = find_data_folder(arguments.data_folder, os.environ)
    configuration = load_configuration(data_folder)
    translator = Translator(configuration.settings.language)

    print(translator.translate("check.settings_are_valid", folder=data_folder.root))
    for line in describe_configuration(configuration, translator):
        print(line)
    return 0


def describe_configuration(configuration: Configuration, translator: Translator) -> list[str]:
    """A short summary, so the person sees the program understood their settings."""
    categories = configuration.categories
    lines = [
        translator.translate("check.language", language=configuration.settings.language),
        translator.translate(
            "check.expense_categories",
            categories=len(categories.expense_categories()),
            groups=len(categories.expense_groups),
        ),
        translator.translate(
            "check.income_categories", names=", ".join(categories.income_category_names)
        ),
        translator.translate("check.accounts_heading"),
    ]
    for account in configuration.accounts.accounts:
        reconciliation_key = "check.reconciled" if account.is_reconciled else "check.not_reconciled"
        lines.append(
            translator.translate(
                "check.account_line",
                code=account.code,
                name=account.name,
                reconciliation=translator.translate(reconciliation_key),
            )
        )
    return lines
