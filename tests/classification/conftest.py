"""A small set of settings shared by the classification tests."""

from collections.abc import Callable
from dataclasses import replace

import pytest

from notes_to_budget.classification.rule_set_builder import build_classification_rules
from notes_to_budget.classification.transaction_classifier import classify_parsed_notes
from notes_to_budget.configuration.classification_rules import KeywordRule, PersonRule
from notes_to_budget.configuration.configuration import Configuration
from notes_to_budget.configuration.notes_format import NotesFormat
from notes_to_budget.configuration.settings import Settings
from notes_to_budget.domain.account import Account
from notes_to_budget.domain.account_catalog import AccountCatalog
from notes_to_budget.domain.category import Category, CategoryGroup
from notes_to_budget.domain.category_catalog import CategoryCatalog
from notes_to_budget.domain.month import Month
from notes_to_budget.domain.transaction import Transaction
from notes_to_budget.localization.translator import Translator
from notes_to_budget.notes_parsing.notes_file_reader import NumberedLine
from notes_to_budget.notes_parsing.notes_parser import parse_notes

EXPENSE_CATEGORY_NAMES = (
    "Groceries",
    "Food at work",
    "Eating out",
    "Cafes",
    "Alcohol",
    "Transport",
    "Children",
    "Gifts",
    "Holidays",
    "Subscriptions",
    "Other",
    "Lost",
)


@pytest.fixture
def configuration() -> Configuration:
    return Configuration(
        settings=Settings(
            language="en",
            currency_symbol="€",
            notes_folder_name="notes",
            ledger_folder_name="ledger",
            review_folder_name="review",
            workbook_file_name_pattern="Budget {year}.xlsx",
        ),
        categories=CategoryCatalog(
            expense_groups=(
                CategoryGroup(
                    name="Everything",
                    categories=tuple(
                        Category(name=name, group_name="Everything")
                        for name in EXPENSE_CATEGORY_NAMES
                    ),
                ),
            ),
            income_category_names=("Salary", "Rent", "Additional"),
            savings_category_name="Savings",
            investments_category_name="Investments",
            fallback_category_name="Other",
            lost_money_category_name="Lost",
        ),
        accounts=AccountCatalog(
            accounts=(
                Account("C", "Cash", True, 1, ("cash",)),
                Account("R", "Online wallet", True, 2, ("Revolut", "wallet")),
                Account("B", "Bank card", True, 3, ("card",)),
                Account("CC", "Credit card", False, None, ("credit card", "credit")),
            )
        ),
        notes_format=NotesFormat(
            balances_are_written_in_the_morning=True,
            newest_day_first=True,
            uncertain_marker="?",
            transfer_phrases=("from {from} to {to}", "to {to}"),
            savings_taken_out_phrases=("from savings",),
            savings_put_in_phrases=("saved",),
            investment_phrases=("invested",),
        ),
        keyword_rules=(
            KeywordRule(keywords=("Lidl", "bread", "water"), category_name="Groceries"),
            KeywordRule(
                keywords=("lunch",),
                category_name="Food at work",
                weekend_category_name="Eating out",
            ),
            KeywordRule(keywords=("dinner", "burger"), category_name="Eating out"),
            KeywordRule(
                keywords=("beer", "vodka"), category_name="Alcohol", excluded_keywords=("and",)
            ),
            KeywordRule(keywords=("gift", "birthday"), category_name="Gifts"),
            KeywordRule(keywords=("charging", "parking"), category_name="Transport"),
            KeywordRule(keywords=("from Anna",), category_name="Additional"),
        ),
        person_rules=(
            PersonRule(
                names=("Mimi",),
                category_name="Children",
                excluded_keywords=("gift", "burger"),
            ),
            PersonRule(names=("John",), category_name=""),
        ),
    )


@pytest.fixture
def classify(configuration) -> Callable[..., list[Transaction]]:
    """Read and classify notes written inside a test (a file for March 2026).

    Settings can be changed for one test: ``classify(text, learned_rules=(...))``.
    """

    def classify_notes(notes_text: str, **changed_settings) -> list[Transaction]:
        used_configuration = replace(configuration, **changed_settings)
        lines = [
            NumberedLine(number=line_number, text=line_text)
            for line_number, line_text in enumerate(notes_text.splitlines(), start=1)
            if line_text.strip()
        ]
        parsed_notes = parse_notes(
            lines,
            file_name="March.txt",
            month_of_the_file=Month(2026, 3),
            accounts=used_configuration.accounts,
            notes_format=used_configuration.notes_format,
            currency_symbol="€",
        )
        assert parsed_notes.problems == ()
        return classify_parsed_notes(
            parsed_notes, build_classification_rules(used_configuration), Translator("en")
        )

    return classify_notes


@pytest.fixture
def classify_one(classify) -> Callable[..., Transaction]:
    """Classify a single entry written on Monday 2 March 2026 (or another day)."""

    def classify_entry(entry_line: str, day: str = "02", **changed_settings) -> Transaction:
        transactions = classify(f"{day} - 1 / 2 / 3\n {entry_line}", **changed_settings)
        assert len(transactions) == 1
        return transactions[0]

    return classify_entry
