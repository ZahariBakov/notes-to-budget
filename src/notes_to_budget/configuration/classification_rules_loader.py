"""Reads the four files with rules for choosing categories.

``keyword_rules.yaml``, ``people.yaml``, ``learned_rules.yaml`` and
``special_periods.yaml`` all hold a list of small rules, so they are read
the same way: item by item, each with its place for error messages.
"""

from pathlib import Path
from typing import Any

from notes_to_budget.configuration.classification_rules import (
    KeywordRule,
    LearnedRule,
    PersonRule,
    SpecialPeriod,
)
from notes_to_budget.configuration.configuration_error import ConfigurationError
from notes_to_budget.configuration.yaml_file_reader import read_yaml_mapping
from notes_to_budget.configuration.yaml_values import (
    read_optional_list,
    read_optional_text,
    read_optional_text_list,
    read_optional_yes_or_no,
    read_required_date,
    read_required_text,
    require_named_values,
)

SPENDING_WORKED_OUT_FROM_BALANCES = "spend_by_balances"


def load_keyword_rules(keyword_rules_file: Path) -> tuple[KeywordRule, ...]:
    return tuple(
        _read_keyword_rule(rule_values, place, keyword_rules_file)
        for rule_values, place in _read_listed_items(keyword_rules_file, "rules")
    )


def load_person_rules(people_file: Path) -> tuple[PersonRule, ...]:
    return tuple(
        _read_person_rule(rule_values, place, people_file)
        for rule_values, place in _read_listed_items(people_file, "people")
    )


def load_learned_rules(learned_rules_file: Path) -> tuple[LearnedRule, ...]:
    return tuple(
        LearnedRule(
            description=read_required_text(rule_values, "description", learned_rules_file, place),
            category_name=read_required_text(rule_values, "category", learned_rules_file, place),
            is_one_off=read_optional_yes_or_no(
                rule_values, "one_off", learned_rules_file, place, default=False
            ),
        )
        for rule_values, place in _read_listed_items(learned_rules_file, "rules")
    )


def load_special_periods(special_periods_file: Path) -> tuple[SpecialPeriod, ...]:
    return tuple(
        _read_special_period(period_values, place, special_periods_file)
        for period_values, place in _read_listed_items(special_periods_file, "periods")
    )


def _read_listed_items(rules_file: Path, list_name: str) -> list[tuple[Any, str]]:
    """Return every item of the list with its place, such as ``rules[3]``."""
    listed_items = read_optional_list(read_yaml_mapping(rules_file), list_name, rules_file)
    return [
        (
            require_named_values(item, rules_file, f"{list_name}[{position}]"),
            f"{list_name}[{position}]",
        )
        for position, item in enumerate(listed_items, start=1)
    ]


def _read_keyword_rule(rule_values: Any, place: str, rules_file: Path) -> KeywordRule:
    keywords = read_optional_text_list(rule_values, "when_description_contains", rules_file, place)
    if not keywords:
        raise ConfigurationError(
            "configuration.value_missing",
            file=rules_file,
            place=f"{place}.when_description_contains",
        )
    return KeywordRule(
        keywords=keywords,
        category_name=read_required_text(rule_values, "category", rules_file, place),
        weekend_category_name=read_optional_text(
            rule_values, "category_on_weekends", rules_file, place
        ),
        excluded_keywords=read_optional_text_list(
            rule_values, "unless_description_contains", rules_file, place
        ),
    )


def _read_person_rule(rule_values: Any, place: str, people_file: Path) -> PersonRule:
    names = read_optional_text_list(rule_values, "names", people_file, place)
    if not names:
        raise ConfigurationError(
            "configuration.value_missing", file=people_file, place=f"{place}.names"
        )
    return PersonRule(
        names=names,
        category_name=read_optional_text(rule_values, "category", people_file, place),
        excluded_keywords=read_optional_text_list(
            rule_values, "unless_description_contains", people_file, place
        ),
    )


def _read_special_period(period_values: Any, place: str, periods_file: Path) -> SpecialPeriod:
    period = SpecialPeriod(
        name=read_required_text(period_values, "name", periods_file, place),
        first_day=read_required_date(period_values, "from", periods_file, place),
        last_day=read_required_date(period_values, "to", periods_file, place),
        category_name=read_required_text(period_values, "everything_goes_to", periods_file, place),
        spending_is_worked_out_from_balances=(
            read_optional_text(period_values, "days_without_notes", periods_file, place)
            == SPENDING_WORKED_OUT_FROM_BALANCES
        ),
        categories_that_stay=read_optional_text_list(
            period_values, "except_categories", periods_file, place
        ),
    )
    if period.last_day < period.first_day:
        raise ConfigurationError(
            "configuration.period_ends_before_it_starts", file=periods_file, place=place
        )
    return period
