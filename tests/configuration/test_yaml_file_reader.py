import pytest

from notes_to_budget.configuration.configuration_error import ConfigurationError
from notes_to_budget.configuration.yaml_file_reader import read_yaml_mapping


def test_named_values_are_read(write_settings_file):
    settings_file = write_settings_file("settings.yaml", "language: bg\ncurrency_symbol: лв\n")

    assert read_yaml_mapping(settings_file) == {"language": "bg", "currency_symbol": "лв"}


def test_a_file_saved_by_windows_notepad_is_read(tmp_path):
    notepad_file = tmp_path / "settings.yaml"
    notepad_file.write_text("language: bg\n", encoding="utf-8-sig")

    assert read_yaml_mapping(notepad_file) == {"language": "bg"}


def test_a_missing_file_is_reported(tmp_path):
    with pytest.raises(ConfigurationError) as problem:
        read_yaml_mapping(tmp_path / "nowhere.yaml")

    assert problem.value.message_key == "configuration.file_missing"


def test_a_file_that_is_not_yaml_is_reported(write_settings_file):
    broken_file = write_settings_file("settings.yaml", "language: [bg\n")

    with pytest.raises(ConfigurationError) as problem:
        read_yaml_mapping(broken_file)

    assert problem.value.message_key == "configuration.file_not_valid_yaml"


@pytest.mark.parametrize("content", ["", "- just\n- a list\n", "only text\n"])
def test_a_file_without_named_values_is_reported(write_settings_file, content):
    settings_file = write_settings_file("settings.yaml", content)

    with pytest.raises(ConfigurationError) as problem:
        read_yaml_mapping(settings_file)

    assert problem.value.message_key == "configuration.file_must_hold_named_values"
