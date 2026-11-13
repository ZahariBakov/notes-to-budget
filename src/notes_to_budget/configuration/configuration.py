"""All settings of one person, loaded and checked together."""

from dataclasses import dataclass

from notes_to_budget.configuration.accounts_loader import load_account_catalog
from notes_to_budget.configuration.categories_loader import load_category_catalog
from notes_to_budget.configuration.classification_rules import (
    KeywordRule,
    LearnedRule,
    PersonRule,
    SpecialPeriod,
)
from notes_to_budget.configuration.classification_rules_loader import (
    load_keyword_rules,
    load_learned_rules,
    load_person_rules,
    load_special_periods,
)
from notes_to_budget.configuration.configuration_validator import (
    check_rules_use_known_categories,
)
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
    keyword_rules: tuple[KeywordRule, ...] = ()
    person_rules: tuple[PersonRule, ...] = ()
    learned_rules: tuple[LearnedRule, ...] = ()
    special_periods: tuple[SpecialPeriod, ...] = ()


def load_configuration(data_folder: DataFolder) -> Configuration:
    configuration = Configuration(
        settings=load_settings(data_folder.settings_file),
        categories=load_category_catalog(data_folder.categories_file),
        accounts=load_account_catalog(data_folder.accounts_file),
        notes_format=load_notes_format(data_folder.notes_format_file),
        keyword_rules=load_keyword_rules(data_folder.keyword_rules_file),
        person_rules=load_person_rules(data_folder.people_file),
        learned_rules=load_learned_rules(data_folder.learned_rules_file),
        special_periods=load_special_periods(data_folder.special_periods_file),
    )
    check_rules_use_known_categories(
        configuration.categories,
        data_folder,
        configuration.keyword_rules,
        configuration.person_rules,
        configuration.learned_rules,
        configuration.special_periods,
    )
    return configuration
