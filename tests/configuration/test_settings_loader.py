import pytest

from notes_to_budget.configuration.configuration_error import ConfigurationError
from notes_to_budget.configuration.settings_loader import load_settings

VALID_SETTINGS = """
    language: bg
    currency_symbol: "€"
    folders:
      notes: Записки
      ledger: Дневник
      review: За проверка
    workbook_file_name: "Бюджет {year}.xlsx"
"""


def test_valid_settings_are_loaded(write_settings_file):
    settings = load_settings(write_settings_file("settings.yaml", VALID_SETTINGS))

    assert settings.language == "bg"
    assert settings.currency_symbol == "€"
    assert settings.notes_folder_name == "Записки"
    assert settings.ledger_folder_name == "Дневник"
    assert settings.review_folder_name == "За проверка"
    assert settings.workbook_file_name(2026) == "Бюджет 2026.xlsx"


def test_an_unsupported_language_is_reported(write_settings_file):
    settings_file = write_settings_file(
        "settings.yaml", VALID_SETTINGS.replace("language: bg", "language: fr")
    )

    with pytest.raises(ConfigurationError) as problem:
        load_settings(settings_file)

    assert problem.value.message_key == "configuration.language_not_supported"
    assert problem.value.details["language"] == "fr"


def test_a_missing_folder_name_is_reported_with_its_place(write_settings_file):
    settings_file = write_settings_file(
        "settings.yaml", VALID_SETTINGS.replace("      ledger: Дневник\n", "")
    )

    with pytest.raises(ConfigurationError) as problem:
        load_settings(settings_file)

    assert problem.value.message_key == "configuration.value_missing"
    assert problem.value.details["place"] == "folders.ledger"


def test_missing_folders_section_is_reported(write_settings_file):
    settings_file = write_settings_file(
        "settings.yaml", 'language: en\ncurrency_symbol: "$"\nworkbook_file_name: "B {year}.xlsx"\n'
    )

    with pytest.raises(ConfigurationError) as problem:
        load_settings(settings_file)

    assert problem.value.message_key == "configuration.value_must_hold_named_values"
    assert problem.value.details["place"] == "folders"


def test_a_workbook_name_without_the_year_is_reported(write_settings_file):
    settings_file = write_settings_file(
        "settings.yaml", VALID_SETTINGS.replace("Бюджет {year}.xlsx", "Бюджет.xlsx")
    )

    with pytest.raises(ConfigurationError) as problem:
        load_settings(settings_file)

    assert problem.value.message_key == "configuration.workbook_file_name_needs_year"
