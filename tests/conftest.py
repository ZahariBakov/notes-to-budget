"""Helpers shared by all tests."""

import textwrap
from collections.abc import Callable
from pathlib import Path

import pytest


@pytest.fixture
def write_settings_file(tmp_path: Path) -> Callable[[str, str], Path]:
    """Write a small settings file for one test and return its path."""

    def write(file_name: str, content: str) -> Path:
        settings_file = tmp_path / file_name
        settings_file.write_text(textwrap.dedent(content), encoding="utf-8")
        return settings_file

    return write
