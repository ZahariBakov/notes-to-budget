import json
import re

import pytest

from notes_to_budget.command_line.main import main
from notes_to_budget.configuration.configuration import load_configuration
from notes_to_budget.configuration.data_folder_creator import create_data_folder
from notes_to_budget.google_form.form_script_builder import (
    SETUP_PLACEHOLDER,
    build_form_script,
)
from notes_to_budget.google_form.form_setup import FORM_LABEL_NAMES, build_form_setup
from notes_to_budget.localization.translator import SUPPORTED_LANGUAGES, Translator


@pytest.fixture
def english_setup(tmp_path):
    configuration = load_configuration(create_data_folder(tmp_path, "en"))
    return build_form_setup(configuration, Translator("en"))


def read_setup_from(script: str) -> dict:
    """Take the SETUP block back out of a finished script."""
    start = script.index("const SETUP = ") + len("const SETUP = ")
    end = script.index(";\n", start)
    return json.loads(script[start:end])


def test_the_form_offers_expenses_first_then_income_savings_and_a_transfer(english_setup):
    category_names = [category["name"] for category in english_setup["categories"]]

    assert category_names[0] == "Bills"
    assert category_names[-6:] == [
        "Salary",
        "Rent",
        "Additional",
        "Savings",
        "Investments",
        "Transfer between accounts",
    ]


def test_every_choice_knows_its_kind_and_group(english_setup):
    by_name = {category["name"]: category for category in english_setup["categories"]}

    assert by_name["Groceries"]["kind"] == "expense"
    assert by_name["Groceries"]["group"] == "Everyday"
    assert by_name["Salary"]["kind"] == "income"
    assert by_name["Savings"]["kind"] == "saving"
    assert by_name["Investments"]["kind"] == "investment"
    assert by_name["Transfer between accounts"]["kind"] == "transfer"


def test_accounts_are_shown_with_code_and_name_and_know_if_they_are_reconciled(english_setup):
    assert english_setup["accounts"] == [
        {"code": "C", "label": "C – Cash", "reconciled": True},
        {"code": "R", "label": "R – Online wallet", "reconciled": True},
        {"code": "B", "label": "B – Bank card", "reconciled": True},
        {"code": "CC", "label": "CC – Credit card", "reconciled": False},
    ]


@pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
def test_every_label_the_script_uses_is_translated(tmp_path, language):
    configuration = load_configuration(create_data_folder(tmp_path, language))
    setup = build_form_setup(configuration, Translator(language))

    assert set(setup["labels"]) == set(FORM_LABEL_NAMES)
    for label_name, label in setup["labels"].items():
        assert not label.startswith("form."), f"{label_name} is not translated"


def test_the_script_uses_only_labels_that_the_setup_provides(tmp_path):
    configuration = load_configuration(create_data_folder(tmp_path, "en"))
    script = build_form_script(configuration, Translator("en"))
    script_code = script[script.index("// Columns of the sheet") :]

    used_label_names = set(re.findall(r"labels\.(\w+)", script_code))

    assert used_label_names
    assert used_label_names <= set(FORM_LABEL_NAMES)


def test_the_script_holds_the_persons_own_settings_in_bulgarian(tmp_path):
    configuration = load_configuration(create_data_folder(tmp_path, "bg"))

    script = build_form_script(configuration, Translator("bg"))
    setup = read_setup_from(script)

    assert SETUP_PLACEHOLDER not in script
    assert "function createBudgetForm()" in script
    assert setup["currencySymbol"] == "€"
    assert setup["labels"]["formTitle"] == "Бюджет – нов запис"
    assert setup["accounts"][0]["label"] == "Б – Кеш"
    assert "Пазар" in [category["name"] for category in setup["categories"]]
    assert setup["categories"][-1]["name"] == "Прехвърляне между сметки"


def test_the_command_writes_the_script_into_the_data_folder(tmp_path, capsys):
    main(["init", str(tmp_path), "--language", "bg"])
    capsys.readouterr()

    exit_code = main(["form-script", "--data-folder", str(tmp_path)])

    script_file = tmp_path / "create_budget_form.gs"
    printed = capsys.readouterr().out
    assert exit_code == 0
    assert "function createBudgetForm()" in script_file.read_text(encoding="utf-8")
    assert str(script_file) in printed
    assert "script.google.com" in printed


def test_the_command_writes_where_it_is_told(tmp_path, capsys):
    main(["init", str(tmp_path), "--language", "en"])
    chosen_file = tmp_path / "my-form.gs"

    main(["form-script", "--output", str(chosen_file), "--data-folder", str(tmp_path)])

    assert chosen_file.is_file()
