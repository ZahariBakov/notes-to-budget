import json

import pytest

from notes_to_budget.budget_app.personal_settings_builder import (
    PERSONAL_SETTINGS_FILE_NAME,
    build_personal_settings,
    build_personal_settings_file,
)
from notes_to_budget.command_line.main import main
from notes_to_budget.configuration.configuration import load_configuration
from notes_to_budget.configuration.data_folder_creator import create_data_folder
from notes_to_budget.localization.translator import SUPPORTED_LANGUAGES


@pytest.fixture
def english_configuration(tmp_path):
    return load_configuration(create_data_folder(tmp_path, "en"))


def read_settings_from(file_text: str) -> dict:
    """Take the settings back out of the written script file."""
    start = file_text.index("const PERSONAL_SETTINGS = ") + len("const PERSONAL_SETTINGS = ")
    end = file_text.index(";\n", start)
    return json.loads(file_text[start:end])


def test_expenses_come_first_then_income_savings_and_investments(english_configuration):
    settings = build_personal_settings(english_configuration)
    names = [category["name"] for category in settings["categories"]]

    assert names[0] == "Bills"
    assert names[-5:] == ["Salary", "Rent", "Additional", "Savings", "Investments"]


def test_every_category_knows_its_kind_and_only_expenses_carry_a_group(english_configuration):
    by_name = {
        category["name"]: category
        for category in build_personal_settings(english_configuration)["categories"]
    }

    assert by_name["Groceries"] == {"name": "Groceries", "group": "Everyday", "kind": "expense"}
    assert by_name["Salary"] == {"name": "Salary", "group": "", "kind": "income"}
    assert by_name["Savings"]["kind"] == "saving"
    assert by_name["Investments"]["kind"] == "investment"


def test_accounts_know_if_they_are_reconciled_or_a_credit_card(english_configuration):
    accounts = build_personal_settings(english_configuration)["accounts"]

    assert accounts[0] == {"code": "C", "name": "Cash", "reconciled": True, "creditCard": False}
    assert accounts[-1] == {
        "code": "CC",
        "name": "Credit card",
        "reconciled": False,
        "creditCard": True,
    }


@pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
def test_the_file_is_a_script_that_holds_the_settings(tmp_path, language):
    configuration = load_configuration(create_data_folder(tmp_path, language))

    settings = read_settings_from(build_personal_settings_file(configuration))

    assert settings == build_personal_settings(configuration)
    assert settings["language"] == language


def test_the_command_writes_the_file_into_the_data_folder(tmp_path, capsys):
    main(["init", str(tmp_path), "--language", "bg"])
    capsys.readouterr()

    exit_code = main(["app-settings", "--data-folder", str(tmp_path)])

    settings_file = tmp_path / PERSONAL_SETTINGS_FILE_NAME
    printed = capsys.readouterr().out
    assert exit_code == 0
    assert read_settings_from(settings_file.read_text(encoding="utf-8"))["language"] == "bg"
    assert str(settings_file) in printed
    assert "clasp push" in printed


def test_the_command_writes_where_it_is_told(tmp_path, capsys):
    main(["init", str(tmp_path), "--language", "en"])
    chosen_file = tmp_path / "apps_script" / "personal_settings.js"
    chosen_file.parent.mkdir()

    main(["app-settings", "--output", str(chosen_file), "--data-folder", str(tmp_path)])

    assert chosen_file.is_file()
