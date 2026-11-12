"""Reads ``categories.yaml``."""

from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from notes_to_budget.configuration.configuration_error import ConfigurationError
from notes_to_budget.configuration.yaml_file_reader import read_yaml_mapping
from notes_to_budget.configuration.yaml_values import (
    read_optional_text,
    read_optional_text_list,
    read_required_list,
    read_required_text,
    require_named_values,
)
from notes_to_budget.domain.category import Category, CategoryGroup
from notes_to_budget.domain.category_catalog import CategoryCatalog


def load_category_catalog(categories_file: Path) -> CategoryCatalog:
    values = read_yaml_mapping(categories_file)
    listed_groups = read_required_list(values, "expense_groups", categories_file)

    catalog = CategoryCatalog(
        expense_groups=tuple(
            _read_expense_group(listed_group, f"expense_groups[{position}]", categories_file)
            for position, listed_group in enumerate(listed_groups, start=1)
        ),
        income_category_names=read_optional_text_list(values, "income_categories", categories_file),
        savings_category_name=read_required_text(values, "savings_category", categories_file),
        investments_category_name=read_required_text(
            values, "investments_category", categories_file
        ),
        fallback_category_name=read_required_text(values, "fallback_category", categories_file),
        lost_money_category_name=read_required_text(values, "lost_money_category", categories_file),
    )
    _check_there_is_at_least_one_of_each_kind(catalog, categories_file)
    _check_no_name_is_used_twice(catalog, categories_file)
    _check_special_expense_categories_exist(catalog, categories_file)
    return catalog


def _read_expense_group(listed_group: Any, place: str, categories_file: Path) -> CategoryGroup:
    group_values = require_named_values(listed_group, categories_file, place)
    group_name = read_required_text(group_values, "name", categories_file, place)
    listed_categories = read_required_list(group_values, "categories", categories_file, place)
    return CategoryGroup(
        name=group_name,
        categories=tuple(
            _read_category(
                listed_category, group_name, f"{place}.categories[{position}]", categories_file
            )
            for position, listed_category in enumerate(listed_categories, start=1)
        ),
    )


def _read_category(
    listed_category: Any, group_name: str, place: str, categories_file: Path
) -> Category:
    category_values: Mapping[str, Any] = require_named_values(
        listed_category, categories_file, place
    )
    return Category(
        name=read_required_text(category_values, "name", categories_file, place),
        group_name=group_name,
        includes=read_optional_text(category_values, "includes", categories_file, place),
    )


def _check_there_is_at_least_one_of_each_kind(
    catalog: CategoryCatalog, categories_file: Path
) -> None:
    if not catalog.expense_categories():
        raise ConfigurationError("configuration.no_expense_categories", file=categories_file)
    if not catalog.income_category_names:
        raise ConfigurationError("configuration.no_income_categories", file=categories_file)


def _check_no_name_is_used_twice(catalog: CategoryCatalog, categories_file: Path) -> None:
    times_used = Counter(catalog.all_category_names())
    names_used_twice = [name for name, times in times_used.items() if times > 1]
    if names_used_twice:
        raise ConfigurationError(
            "configuration.category_listed_twice",
            file=categories_file,
            category=names_used_twice[0],
        )


def _check_special_expense_categories_exist(
    catalog: CategoryCatalog, categories_file: Path
) -> None:
    special_categories = {
        "fallback_category": catalog.fallback_category_name,
        "lost_money_category": catalog.lost_money_category_name,
    }
    for setting_name, category_name in special_categories.items():
        if category_name not in catalog.expense_category_names():
            raise ConfigurationError(
                "configuration.special_category_not_among_expenses",
                file=categories_file,
                place=setting_name,
                category=category_name,
            )
