"""Finds the person's own data folder and the files inside it."""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from notes_to_budget.configuration.configuration_error import ConfigurationError

DATA_FOLDER_ENVIRONMENT_VARIABLE = "NOTES_TO_BUDGET_DATA_FOLDER"
CONFIGURATION_FOLDER_NAME = "config"


@dataclass(frozen=True)
class DataFolder:
    """The folder with one person's notes, settings, ledger and workbook.

    It lives outside the program's repository and is never published.
    """

    root: Path

    @property
    def configuration_folder(self) -> Path:
        return self.root / CONFIGURATION_FOLDER_NAME

    @property
    def settings_file(self) -> Path:
        return self.configuration_folder / "settings.yaml"

    @property
    def categories_file(self) -> Path:
        return self.configuration_folder / "categories.yaml"

    @property
    def accounts_file(self) -> Path:
        return self.configuration_folder / "accounts.yaml"

    @property
    def notes_format_file(self) -> Path:
        return self.configuration_folder / "notes_format.yaml"

    @property
    def keyword_rules_file(self) -> Path:
        return self.configuration_folder / "keyword_rules.yaml"

    @property
    def people_file(self) -> Path:
        return self.configuration_folder / "people.yaml"

    @property
    def learned_rules_file(self) -> Path:
        return self.configuration_folder / "learned_rules.yaml"

    @property
    def special_periods_file(self) -> Path:
        return self.configuration_folder / "special_periods.yaml"

    def folder_named(self, folder_name: str) -> Path:
        return self.root / folder_name


def find_data_folder(
    folder_from_command_line: str | None, environment: Mapping[str, str]
) -> DataFolder:
    """Use the folder given on the command line, or else the environment variable."""
    folder_text = folder_from_command_line or environment.get(DATA_FOLDER_ENVIRONMENT_VARIABLE)
    if not folder_text:
        raise ConfigurationError(
            "configuration.data_folder_not_given", variable=DATA_FOLDER_ENVIRONMENT_VARIABLE
        )

    data_folder = DataFolder(root=Path(folder_text).expanduser())
    if not data_folder.root.is_dir():
        raise ConfigurationError("configuration.data_folder_missing", folder=data_folder.root)
    return data_folder
