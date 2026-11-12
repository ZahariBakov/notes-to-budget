"""Creates a new data folder filled with starter settings."""

from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path

from notes_to_budget.configuration.configuration_error import ConfigurationError
from notes_to_budget.configuration.data_folder import DataFolder
from notes_to_budget.configuration.settings_loader import load_settings

STARTER_CONFIGURATION_FOLDER_NAME = "starter_configuration"


def create_data_folder(root: Path, language: str) -> DataFolder:
    """Create the folder, copy the starter settings and make the sub-folders.

    Refuses to touch a folder that already has settings, so nobody loses
    their own rules by running the command twice.
    """
    data_folder = DataFolder(root=root)
    if data_folder.configuration_folder.exists():
        raise ConfigurationError(
            "init.settings_already_exist", folder=data_folder.configuration_folder
        )

    data_folder.configuration_folder.mkdir(parents=True)
    for starter_file in _starter_settings_files(language):
        destination = data_folder.configuration_folder / starter_file.name
        destination.write_bytes(starter_file.read_bytes())

    settings = load_settings(data_folder.settings_file)
    for folder_name in (
        settings.notes_folder_name,
        settings.ledger_folder_name,
        settings.review_folder_name,
    ):
        data_folder.folder_named(folder_name).mkdir(exist_ok=True)
    return data_folder


def _starter_settings_files(language: str) -> list[Traversable]:
    starter_folder = resources.files("notes_to_budget").joinpath(
        STARTER_CONFIGURATION_FOLDER_NAME, language
    )
    return sorted(
        (file for file in starter_folder.iterdir() if file.name.endswith(".yaml")),
        key=lambda file: file.name,
    )
