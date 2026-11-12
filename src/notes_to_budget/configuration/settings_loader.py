"""Reads ``settings.yaml``."""

from pathlib import Path

from notes_to_budget.configuration.configuration_error import ConfigurationError
from notes_to_budget.configuration.settings import Settings
from notes_to_budget.configuration.yaml_file_reader import read_yaml_mapping
from notes_to_budget.configuration.yaml_values import (
    read_required_text,
    require_named_values,
)
from notes_to_budget.localization.translator import SUPPORTED_LANGUAGES

YEAR_PLACEHOLDER = "{year}"


def load_settings(settings_file: Path) -> Settings:
    values = read_yaml_mapping(settings_file)
    folder_names = require_named_values(values.get("folders"), settings_file, "folders")

    settings = Settings(
        language=read_required_text(values, "language", settings_file),
        currency_symbol=read_required_text(values, "currency_symbol", settings_file),
        notes_folder_name=read_required_text(folder_names, "notes", settings_file, "folders"),
        ledger_folder_name=read_required_text(folder_names, "ledger", settings_file, "folders"),
        review_folder_name=read_required_text(folder_names, "review", settings_file, "folders"),
        workbook_file_name_pattern=read_required_text(values, "workbook_file_name", settings_file),
    )
    _check_language_is_supported(settings, settings_file)
    _check_workbook_file_name_has_the_year(settings, settings_file)
    return settings


def _check_language_is_supported(settings: Settings, settings_file: Path) -> None:
    if settings.language not in SUPPORTED_LANGUAGES:
        raise ConfigurationError(
            "configuration.language_not_supported",
            file=settings_file,
            language=settings.language,
            supported=", ".join(SUPPORTED_LANGUAGES),
        )


def _check_workbook_file_name_has_the_year(settings: Settings, settings_file: Path) -> None:
    if YEAR_PLACEHOLDER not in settings.workbook_file_name_pattern:
        raise ConfigurationError("configuration.workbook_file_name_needs_year", file=settings_file)
