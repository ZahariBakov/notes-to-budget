"""The ``app-settings`` command: write your categories and accounts for the phone app."""

import argparse
import os
from pathlib import Path

from notes_to_budget.budget_app.personal_settings_builder import (
    PERSONAL_SETTINGS_FILE_NAME,
    build_personal_settings_file,
)
from notes_to_budget.configuration.configuration import load_configuration
from notes_to_budget.configuration.data_folder import find_data_folder
from notes_to_budget.localization.translator import Translator


def add_app_settings_command(commands: argparse._SubParsersAction) -> None:
    command = commands.add_parser(
        "app-settings",
        help="write your categories and accounts for the phone app",
        description="Write a script file with your categories and accounts. The phone app "
        "copies them into its spreadsheet when it prepares it.",
    )
    command.add_argument(
        "--output",
        help=f"where to write the file (default: {PERSONAL_SETTINGS_FILE_NAME} "
        "in your data folder); put it in the apps_script folder before you upload the app",
    )
    command.add_argument(
        "--data-folder",
        help="your data folder (or set the NOTES_TO_BUDGET_DATA_FOLDER environment variable)",
    )
    command.set_defaults(run_command=run_app_settings_command)


def run_app_settings_command(arguments: argparse.Namespace) -> int:
    data_folder = find_data_folder(arguments.data_folder, os.environ)
    configuration = load_configuration(data_folder)
    translator = Translator(configuration.settings.language)

    settings_file = (
        Path(arguments.output).expanduser()
        if arguments.output
        else data_folder.root / PERSONAL_SETTINGS_FILE_NAME
    )
    settings_file.write_text(build_personal_settings_file(configuration), encoding="utf-8")

    print(translator.translate("app_settings.written", file=settings_file))
    print(translator.translate("app_settings.next_steps"))
    return 0
