"""Picks single values out of a settings file and checks their kind.

Every function takes the file and the place inside it (``inside``), so an
error can say exactly where to look: ``accounts[2].code``.
"""

from collections.abc import Mapping
from datetime import date, datetime
from pathlib import Path
from typing import Any

from notes_to_budget.configuration.configuration_error import ConfigurationError


def read_required_text(values: Mapping[str, Any], key: str, file: Path, inside: str = "") -> str:
    place = describe_place(inside, key)
    if values.get(key) is None:
        raise ConfigurationError("configuration.value_missing", file=file, place=place)
    return _as_text(values[key], file, place)


def read_optional_text(
    values: Mapping[str, Any], key: str, file: Path, inside: str = "", default: str = ""
) -> str:
    if values.get(key) in (None, ""):
        return default
    return _as_text(values[key], file, describe_place(inside, key))


def read_optional_list(
    values: Mapping[str, Any], key: str, file: Path, inside: str = ""
) -> list[Any]:
    if values.get(key) is None:
        return []
    return _as_list(values[key], file, describe_place(inside, key))


def read_required_date(values: Mapping[str, Any], key: str, file: Path, inside: str = "") -> date:
    """Read a date written as ``2026-07-10``."""
    place = describe_place(inside, key)
    value = values.get(key)
    if value is None:
        raise ConfigurationError("configuration.value_missing", file=file, place=place)
    if isinstance(value, datetime) or not isinstance(value, date):
        raise ConfigurationError("configuration.value_must_be_date", file=file, place=place)
    return value


def read_required_list(
    values: Mapping[str, Any], key: str, file: Path, inside: str = ""
) -> list[Any]:
    place = describe_place(inside, key)
    if values.get(key) is None:
        raise ConfigurationError("configuration.value_missing", file=file, place=place)
    return _as_list(values[key], file, place)


def read_optional_text_list(
    values: Mapping[str, Any], key: str, file: Path, inside: str = ""
) -> tuple[str, ...]:
    if values.get(key) is None:
        return ()
    place = describe_place(inside, key)
    items = _as_list(values[key], file, place)
    return tuple(
        _as_text(item, file, f"{place}[{position}]") for position, item in enumerate(items, start=1)
    )


def read_optional_yes_or_no(
    values: Mapping[str, Any], key: str, file: Path, inside: str = "", *, default: bool
) -> bool:
    value = values.get(key)
    if value is None:
        return default
    if not isinstance(value, bool):
        raise ConfigurationError(
            "configuration.value_must_be_yes_or_no", file=file, place=describe_place(inside, key)
        )
    return value


def read_optional_whole_number(
    values: Mapping[str, Any], key: str, file: Path, inside: str = ""
) -> int | None:
    value = values.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigurationError(
            "configuration.value_must_be_whole_number",
            file=file,
            place=describe_place(inside, key),
        )
    return value


def require_named_values(item: Any, file: Path, place: str) -> Mapping[str, Any]:
    """Check that a list item is a group of named values, like ``name: ...``."""
    if not isinstance(item, dict):
        raise ConfigurationError(
            "configuration.value_must_hold_named_values", file=file, place=place
        )
    return item


def describe_place(inside: str, key: str) -> str:
    return f"{inside}.{key}" if inside else key


def _as_text(value: Any, file: Path, place: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError("configuration.value_must_be_text", file=file, place=place)
    return value.strip()


def _as_list(value: Any, file: Path, place: str) -> list[Any]:
    if not isinstance(value, list):
        raise ConfigurationError("configuration.value_must_be_list", file=file, place=place)
    return value
