"""The ``init`` command: create a data folder with starter settings."""

import argparse
from pathlib import Path

from notes_to_budget.configuration.data_folder_creator import create_data_folder
from notes_to_budget.configuration.settings_loader import load_settings
from notes_to_budget.localization.translator import (
    FALLBACK_LANGUAGE,
    SUPPORTED_LANGUAGES,
    Translator,
)


def add_init_command(commands: argparse._SubParsersAction) -> None:
    command = commands.add_parser(
        "init",
        help="create your data folder with starter settings",
        description="Create a folder for your notes, settings, ledger and workbook.",
    )
    command.add_argument("folder", help="where to create your data folder")
    command.add_argument(
        "--language",
        choices=SUPPORTED_LANGUAGES,
        default=FALLBACK_LANGUAGE,
        help="language of the starter settings and of the messages (default: en)",
    )
    command.set_defaults(run_command=run_init_command)


def run_init_command(arguments: argparse.Namespace) -> int:
    translator = Translator(arguments.language)
    data_folder = create_data_folder(Path(arguments.folder).expanduser(), arguments.language)
    settings = load_settings(data_folder.settings_file)

    print(translator.translate("init.created", folder=data_folder.root))
    print(
        translator.translate(
            "init.next_steps",
            folder=data_folder.root,
            configuration_folder=data_folder.configuration_folder,
            notes_folder=data_folder.folder_named(settings.notes_folder_name),
        )
    )
    return 0
