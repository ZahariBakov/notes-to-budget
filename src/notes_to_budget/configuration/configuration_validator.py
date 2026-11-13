"""Checks that the settings files agree with each other."""

from pathlib import Path

from notes_to_budget.configuration.classification_rules import (
    KeywordRule,
    LearnedRule,
    PersonRule,
    SpecialPeriod,
)
from notes_to_budget.configuration.configuration_error import ConfigurationError
from notes_to_budget.configuration.data_folder import DataFolder
from notes_to_budget.domain.category_catalog import CategoryCatalog


def check_rules_use_known_categories(
    categories: CategoryCatalog,
    data_folder: DataFolder,
    keyword_rules: tuple[KeywordRule, ...],
    person_rules: tuple[PersonRule, ...],
    learned_rules: tuple[LearnedRule, ...],
    special_periods: tuple[SpecialPeriod, ...],
) -> None:
    """A rule that names a category with a typo would never work; say so early."""
    for position, keyword_rule in enumerate(keyword_rules, start=1):
        place = f"rules[{position}]"
        _check(categories, keyword_rule.category_name, data_folder.keyword_rules_file, place)
        _check(
            categories, keyword_rule.weekend_category_name, data_folder.keyword_rules_file, place
        )
    for position, person_rule in enumerate(person_rules, start=1):
        _check(
            categories, person_rule.category_name, data_folder.people_file, f"people[{position}]"
        )
    for position, learned_rule in enumerate(learned_rules, start=1):
        _check(
            categories,
            learned_rule.category_name,
            data_folder.learned_rules_file,
            f"rules[{position}]",
        )
    for position, period in enumerate(special_periods, start=1):
        for category_name in (period.category_name, *period.categories_that_stay):
            _check(
                categories,
                category_name,
                data_folder.special_periods_file,
                f"periods[{position}]",
            )


def _check(categories: CategoryCatalog, category_name: str, rules_file: Path, place: str) -> None:
    if category_name and not categories.is_known_category(category_name):
        raise ConfigurationError(
            "configuration.rule_uses_unknown_category",
            file=rules_file,
            place=place,
            category=category_name,
        )
