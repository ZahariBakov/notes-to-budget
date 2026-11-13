"""All settings of one person, loaded and checked together."""

from dataclasses import dataclass

from notes_to_budget.configuration.accounts_loader import load_account_catalog
from notes_to_budget.configuration.categories_loader import load_category_catalog
from notes_to_budget.configuration.data_folder import DataFolder
from notes_to_budget.configuration.notes_format import NotesFormat
from notes_to_budget.configuration.notes_format_loader import load_notes_format
from notes_to_budget.configuration.settings import Settings
from notes_to_budget.configuration.settings_loader import load_settings
from notes_to_budget.domain.account_catalog import AccountCatalog
from notes_to_budget.domain.category_catalog import CategoryCatalog


@dataclass(frozen=True)
class Configuration:
    settings: Settings
    categories: CategoryCatalog
    accounts: AccountCatalog
    notes_format: NotesFormat


def load_configuration(data_folder: DataFolder) -> Configuration:
    return Configuration(
        settings=load_settings(data_folder.settings_file),
        categories=load_category_catalog(data_folder.categories_file),
        accounts=load_account_catalog(data_folder.accounts_file),
        notes_format=load_notes_format(data_folder.notes_format_file),
    )
