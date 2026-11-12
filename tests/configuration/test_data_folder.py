import pytest

from notes_to_budget.configuration.configuration import load_configuration
from notes_to_budget.configuration.configuration_error import ConfigurationError
from notes_to_budget.configuration.data_folder import (
    DATA_FOLDER_ENVIRONMENT_VARIABLE,
    DataFolder,
    find_data_folder,
)
from notes_to_budget.configuration.data_folder_creator import create_data_folder
from notes_to_budget.localization.translator import SUPPORTED_LANGUAGES


def test_data_folder_knows_where_its_settings_files_are(tmp_path):
    data_folder = DataFolder(root=tmp_path)

    assert data_folder.settings_file == tmp_path / "config" / "settings.yaml"
    assert data_folder.categories_file == tmp_path / "config" / "categories.yaml"
    assert data_folder.accounts_file == tmp_path / "config" / "accounts.yaml"


def test_folder_from_the_command_line_wins_over_the_environment(tmp_path):
    folder_from_command_line = tmp_path / "from-command-line"
    folder_from_command_line.mkdir()
    environment = {DATA_FOLDER_ENVIRONMENT_VARIABLE: str(tmp_path / "from-environment")}

    data_folder = find_data_folder(str(folder_from_command_line), environment)

    assert data_folder.root == folder_from_command_line


def test_folder_is_taken_from_the_environment_when_not_given(tmp_path):
    data_folder = find_data_folder(None, {DATA_FOLDER_ENVIRONMENT_VARIABLE: str(tmp_path)})

    assert data_folder.root == tmp_path


def test_not_knowing_the_data_folder_is_reported():
    with pytest.raises(ConfigurationError) as problem:
        find_data_folder(None, {})

    assert problem.value.message_key == "configuration.data_folder_not_given"


def test_a_data_folder_that_does_not_exist_is_reported(tmp_path):
    with pytest.raises(ConfigurationError) as problem:
        find_data_folder(str(tmp_path / "nowhere"), {})

    assert problem.value.message_key == "configuration.data_folder_missing"


@pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
def test_a_new_data_folder_gets_starter_settings_that_are_valid(tmp_path, language):
    data_folder = create_data_folder(tmp_path / "my-budget", language)

    configuration = load_configuration(data_folder)

    assert configuration.settings.language == language
    assert len(configuration.categories.expense_categories()) > 10
    assert len(configuration.accounts.reconciled_accounts_in_balance_order()) == 3


@pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
def test_a_new_data_folder_gets_all_settings_files_and_the_sub_folders(tmp_path, language):
    data_folder = create_data_folder(tmp_path / "my-budget", language)
    configuration = load_configuration(data_folder)

    settings_file_names = sorted(file.name for file in data_folder.configuration_folder.iterdir())
    assert settings_file_names == [
        "accounts.yaml",
        "categories.yaml",
        "keyword_rules.yaml",
        "learned_rules.yaml",
        "notes_format.yaml",
        "people.yaml",
        "settings.yaml",
        "special_periods.yaml",
    ]
    assert data_folder.folder_named(configuration.settings.notes_folder_name).is_dir()
    assert data_folder.folder_named(configuration.settings.ledger_folder_name).is_dir()
    assert data_folder.folder_named(configuration.settings.review_folder_name).is_dir()


def test_existing_settings_are_never_overwritten(tmp_path):
    data_folder = create_data_folder(tmp_path, "bg")
    data_folder.settings_file.write_text("my own settings", encoding="utf-8")

    with pytest.raises(ConfigurationError) as problem:
        create_data_folder(tmp_path, "en")

    assert problem.value.message_key == "init.settings_already_exist"
    assert data_folder.settings_file.read_text(encoding="utf-8") == "my own settings"
