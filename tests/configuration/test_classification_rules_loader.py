from datetime import date

import pytest

from notes_to_budget.configuration.classification_rules_loader import (
    load_keyword_rules,
    load_learned_rules,
    load_person_rules,
    load_special_periods,
)
from notes_to_budget.configuration.configuration import load_configuration
from notes_to_budget.configuration.configuration_error import ConfigurationError
from notes_to_budget.configuration.data_folder_creator import create_data_folder


def test_keyword_rules_are_loaded_in_their_order(write_settings_file):
    rules = load_keyword_rules(
        write_settings_file(
            "keyword_rules.yaml",
            """
            rules:
              - when_description_contains: [Lidl, bread]
                category: Groceries
              - when_description_contains: [lunch]
                category: Food at work
                category_on_weekends: Eating out
                unless_description_contains: [team]
            """,
        )
    )

    assert rules[0].keywords == ("Lidl", "bread")
    assert rules[0].category_name == "Groceries"
    assert rules[0].weekend_category_name == ""
    assert rules[1].weekend_category_name == "Eating out"
    assert rules[1].excluded_keywords == ("team",)


def test_a_keyword_rule_without_keywords_is_reported_with_its_place(write_settings_file):
    rules_file = write_settings_file("keyword_rules.yaml", "rules:\n  - category: Groceries\n")

    with pytest.raises(ConfigurationError) as problem:
        load_keyword_rules(rules_file)

    assert problem.value.message_key == "configuration.value_missing"
    assert problem.value.details["place"] == "rules[1].when_description_contains"


def test_people_are_loaded_and_an_empty_category_means_a_label_only(write_settings_file):
    people = load_person_rules(
        write_settings_file(
            "people.yaml",
            """
            people:
              - names: [Mimi, Maria]
                category: Children
                unless_description_contains: [gift]
              - names: [John]
                category: ""
            """,
        )
    )

    assert people[0].names == ("Mimi", "Maria")
    assert people[0].category_name == "Children"
    assert people[0].excluded_keywords == ("gift",)
    assert people[1].category_name == ""


def test_learned_rules_are_loaded_and_an_empty_file_list_means_no_rules(write_settings_file):
    rules = load_learned_rules(
        write_settings_file(
            "learned_rules.yaml",
            """
            rules:
              - description: winter tyres
                category: Car
                one_off: true
            """,
        )
    )

    assert rules[0].description == "winter tyres"
    assert rules[0].category_name == "Car"
    assert rules[0].is_one_off
    assert load_learned_rules(write_settings_file("empty.yaml", "rules: []\n")) == ()


def test_special_periods_are_loaded_with_their_dates(write_settings_file):
    periods = load_special_periods(
        write_settings_file(
            "special_periods.yaml",
            """
            periods:
              - name: Seaside
                from: 2026-07-10
                to: 2026-07-17
                everything_goes_to: Holidays
                days_without_notes: spend_by_balances
            """,
        )
    )

    assert periods[0].first_day == date(2026, 7, 10)
    assert periods[0].last_day == date(2026, 7, 17)
    assert periods[0].category_name == "Holidays"
    assert periods[0].spending_is_worked_out_from_balances
    assert periods[0].contains(date(2026, 7, 17))
    assert not periods[0].contains(date(2026, 7, 18))


def test_a_period_that_ends_before_it_starts_is_reported(write_settings_file):
    periods_file = write_settings_file(
        "special_periods.yaml",
        """
        periods:
          - name: Seaside
            from: 2026-07-17
            to: 2026-07-10
            everything_goes_to: Holidays
        """,
    )

    with pytest.raises(ConfigurationError) as problem:
        load_special_periods(periods_file)

    assert problem.value.message_key == "configuration.period_ends_before_it_starts"


def test_a_date_written_as_text_is_reported(write_settings_file):
    periods_file = write_settings_file(
        "special_periods.yaml",
        """
        periods:
          - name: Seaside
            from: 10 July
            to: 2026-07-17
            everything_goes_to: Holidays
        """,
    )

    with pytest.raises(ConfigurationError) as problem:
        load_special_periods(periods_file)

    assert problem.value.message_key == "configuration.value_must_be_date"
    assert problem.value.details["place"] == "periods[1].from"


def test_a_rule_that_names_an_unknown_category_is_reported_when_everything_is_loaded(tmp_path):
    data_folder = create_data_folder(tmp_path, "en")
    data_folder.keyword_rules_file.write_text(
        "rules:\n  - when_description_contains: [Lidl]\n    category: Groceriez\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError) as problem:
        load_configuration(data_folder)

    assert problem.value.message_key == "configuration.rule_uses_unknown_category"
    assert problem.value.details["place"] == "rules[1]"
    assert problem.value.details["category"] == "Groceriez"
