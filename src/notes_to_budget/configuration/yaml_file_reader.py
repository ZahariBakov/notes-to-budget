"""Reads one YAML settings file from disk."""

from pathlib import Path
from typing import Any

import yaml

from notes_to_budget.configuration.configuration_error import ConfigurationError

# "utf-8-sig" also accepts files saved by Windows Notepad, which adds an
# invisible mark at the start of the file.
SETTINGS_FILE_ENCODING = "utf-8-sig"


def read_yaml_mapping(file_path: Path) -> dict[str, Any]:
    """Return the named values of a settings file, or explain what is wrong with it."""
    if not file_path.is_file():
        raise ConfigurationError("configuration.file_missing", file=file_path)

    try:
        content = yaml.safe_load(file_path.read_text(encoding=SETTINGS_FILE_ENCODING))
    except yaml.YAMLError as yaml_problem:
        raise ConfigurationError(
            "configuration.file_not_valid_yaml", file=file_path, reason=yaml_problem
        ) from yaml_problem

    if not isinstance(content, dict):
        raise ConfigurationError("configuration.file_must_hold_named_values", file=file_path)
    return content
