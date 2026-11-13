"""Describes a person's form: their categories, accounts and the labels to show.

The description is plain data. It is written into the Google script, and
later it tells the importer how to read the answers back.
"""

from typing import Any

from notes_to_budget.configuration.configuration import Configuration
from notes_to_budget.domain.account import Account
from notes_to_budget.domain.transaction_type import TransactionType
from notes_to_budget.localization.translator import Translator

SEPARATOR_BETWEEN_ACCOUNT_CODE_AND_NAME = " – "

FORM_LABEL_NAMES = (
    "formTitle",
    "formDescription",
    "spreadsheetTitle",
    "saved",
    "amount",
    "amountHelp",
    "amountMustBeNumber",
    "category",
    "account",
    "description",
    "toAccount",
    "toAccountHelp",
    "oneOff",
    "oneOffYes",
    "date",
    "dateHelp",
    "monthSheet",
    "answersSheet",
    "balancesSheet",
    "group",
    "plan",
    "planHelp",
    "actual",
    "remaining",
    "income",
    "expenses",
    "savedAndInvested",
    "left",
    "startOfMonth",
    "expected",
    "actualNow",
    "difference",
    "balancesHelp",
    "linkToForm",
    "linkToSpreadsheet",
)


def describe_account_in_the_form(account: Account) -> str:
    """How an account is shown in the form, for example ``C – Cash``."""
    return f"{account.code}{SEPARATOR_BETWEEN_ACCOUNT_CODE_AND_NAME}{account.name}"


def build_form_setup(configuration: Configuration, translator: Translator) -> dict[str, Any]:
    return {
        "currencySymbol": configuration.settings.currency_symbol,
        "categories": _list_categories(configuration, translator),
        "accounts": [
            {
                "code": account.code,
                "label": describe_account_in_the_form(account),
                "reconciled": account.is_reconciled,
            }
            for account in configuration.accounts.accounts
        ],
        "labels": {
            label_name: translator.translate(f"form.{label_name}")
            for label_name in FORM_LABEL_NAMES
        },
    }


def _list_categories(configuration: Configuration, translator: Translator) -> list[dict[str, Any]]:
    """Every choice of the "category" question, in the order shown.

    Expenses come first because they are chosen most often. The last
    choice is not a category at all: it marks a transfer between accounts.
    """
    categories = configuration.categories
    listed = [
        _category(category.name, category.group_name, TransactionType.EXPENSE)
        for category in categories.expense_categories()
    ]
    income_group = translator.translate("form.income")
    listed.extend(
        _category(income_category_name, income_group, TransactionType.INCOME)
        for income_category_name in categories.income_category_names
    )
    saved_group = translator.translate("form.savedAndInvested")
    listed.append(_category(categories.savings_category_name, saved_group, TransactionType.SAVING))
    listed.append(
        _category(categories.investments_category_name, saved_group, TransactionType.INVESTMENT)
    )
    listed.append(
        _category(translator.translate("form.transferChoice"), "", TransactionType.TRANSFER)
    )
    return listed


def _category(name: str, group: str, kind: TransactionType) -> dict[str, Any]:
    return {"name": name, "group": group, "kind": str(kind)}
