"""The ``form-script`` command: write the script that creates your Google Form.

The form lets you enter an expense on the phone by typing the amount and
choosing a category. The script builds the form and its spreadsheet from
your own categories and accounts, in your own Google account.
"""

import argparse
import os
from pathlib import Path

from notes_to_budget.configuration.configuration import load_configuration
from notes_to_budget.configuration.data_folder import find_data_folder
from notes_to_budget.google_form.form_script_builder import (
    SCRIPT_TEMPLATE_FILE_NAME,
    build_form_script,
)
from notes_to_budget.localization.translator import Translator


def add_form_script_command(commands: argparse._SubParsersAction) -> None:
    command = commands.add_parser(
        "form-script",
        help="write the script that creates your Google Form and month spreadsheet",
        description="Write a Google Apps Script file made from your categories and accounts.",
    )
    command.add_argument(
        "--output",
        help=f"where to write the script (default: {SCRIPT_TEMPLATE_FILE_NAME} "
        "in your data folder)",
    )
    command.add_argument(
        "--data-folder",
        help="your data folder (or set the NOTES_TO_BUDGET_DATA_FOLDER environment variable)",
    )
    command.set_defaults(run_command=run_form_script_command)


def run_form_script_command(arguments: argparse.Namespace) -> int:
    data_folder = find_data_folder(arguments.data_folder, os.environ)
    configuration = load_configuration(data_folder)
    translator = Translator(configuration.settings.language)

    script_file = (
        Path(arguments.output).expanduser()
        if arguments.output
        else data_folder.root / SCRIPT_TEMPLATE_FILE_NAME
    )
    script_file.write_text(build_form_script(configuration, translator), encoding="utf-8")

    print(translator.translate("form_script.written", file=script_file))
    print(translator.translate("form_script.next_steps"))
    return 0
