import pytest

from notes_to_budget.configuration.categories_loader import load_category_catalog
from notes_to_budget.configuration.configuration_error import ConfigurationError

VALID_CATEGORIES = """
    expense_groups:
      - name: Everyday
        categories:
          - name: Groceries
            includes: supermarkets
          - name: Eating out
      - name: Other
        categories:
          - name: Other
          - name: Lost
    income_categories: [Salary, Rent]
    savings_category: Savings
    investments_category: Investments
    fallback_category: Other
    lost_money_category: Lost
"""


def load_changed_categories(write_settings_file, old_text, new_text):
    assert old_text in VALID_CATEGORIES
    changed_file = write_settings_file(
        "categories.yaml", VALID_CATEGORIES.replace(old_text, new_text)
    )
    return load_category_catalog(changed_file)


def test_valid_categories_are_loaded(write_settings_file):
    catalog = load_category_catalog(write_settings_file("categories.yaml", VALID_CATEGORIES))

    assert [group.name for group in catalog.expense_groups] == ["Everyday", "Other"]
    assert catalog.expense_category_names() == ("Groceries", "Eating out", "Other", "Lost")
    assert catalog.income_category_names == ("Salary", "Rent")
    assert catalog.savings_category_name == "Savings"
    assert catalog.investments_category_name == "Investments"


def test_a_category_remembers_its_group_and_what_it_includes(write_settings_file):
    catalog = load_category_catalog(write_settings_file("categories.yaml", VALID_CATEGORIES))
    groceries = catalog.expense_categories()[0]

    assert groceries.group_name == "Everyday"
    assert groceries.includes == "supermarkets"


def test_a_category_listed_twice_is_reported(write_settings_file):
    with pytest.raises(ConfigurationError) as problem:
        load_changed_categories(write_settings_file, "- name: Eating out", "- name: Groceries")

    assert problem.value.message_key == "configuration.category_listed_twice"
    assert problem.value.details["category"] == "Groceries"


def test_an_income_category_named_like_an_expense_category_is_reported(write_settings_file):
    with pytest.raises(ConfigurationError) as problem:
        load_changed_categories(write_settings_file, "[Salary, Rent]", "[Salary, Other]")

    assert problem.value.message_key == "configuration.category_listed_twice"


def test_a_fallback_category_that_does_not_exist_is_reported(write_settings_file):
    with pytest.raises(ConfigurationError) as problem:
        load_changed_categories(
            write_settings_file, "fallback_category: Other", "fallback_category: Misc"
        )

    assert problem.value.message_key == "configuration.special_category_not_among_expenses"
    assert problem.value.details["place"] == "fallback_category"
    assert problem.value.details["category"] == "Misc"


def test_a_category_without_a_name_is_reported_with_its_place(write_settings_file):
    with pytest.raises(ConfigurationError) as problem:
        load_changed_categories(write_settings_file, "- name: Eating out", "- includes: food")

    assert problem.value.message_key == "configuration.value_missing"
    assert problem.value.details["place"] == "expense_groups[1].categories[2].name"


def test_no_income_categories_is_reported(write_settings_file):
    with pytest.raises(ConfigurationError) as problem:
        load_changed_categories(write_settings_file, "[Salary, Rent]", "[]")

    assert problem.value.message_key == "configuration.no_income_categories"


def test_expense_groups_must_be_a_list(write_settings_file):
    categories_file = write_settings_file("categories.yaml", "expense_groups: Everyday\n")

    with pytest.raises(ConfigurationError) as problem:
        load_category_catalog(categories_file)

    assert problem.value.message_key == "configuration.value_must_be_list"
