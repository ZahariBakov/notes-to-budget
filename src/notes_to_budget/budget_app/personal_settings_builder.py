"""Writes a person's categories and accounts as a script file for the phone app.

The app reads this file once, when it prepares the spreadsheet, and copies
the settings into the "Settings" sheet. From then on the sheet is what
counts, so the person can change categories there.
"""

import json
from typing import Any

from notes_to_budget.configuration.configuration import Configuration
from notes_to_budget.domain.transaction_type import TransactionType

PERSONAL_SETTINGS_FILE_NAME = "personal_settings.js"

_FILE_HEADER = """\
// Your own categories and accounts, written by "notes-to-budget app-settings".
// The app copies them into the Settings sheet when it prepares the spreadsheet.
// Keep this file to yourself: it is not part of the shared code.
"""


def build_personal_settings(configuration: Configuration) -> dict[str, Any]:
    categories = configuration.categories
    listed_categories = [
        _category(category.name, category.group_name, TransactionType.EXPENSE)
        for category in categories.expense_categories()
    ]
    listed_categories.extend(
        _category(name, "", TransactionType.INCOME) for name in categories.income_category_names
    )
    listed_categories.append(
        _category(categories.savings_category_name, "", TransactionType.SAVING)
    )
    listed_categories.append(
        _category(categories.investments_category_name, "", TransactionType.INVESTMENT)
    )
    return {
        "language": configuration.settings.language,
        "currencySymbol": configuration.settings.currency_symbol,
        "categories": listed_categories,
        "accounts": [
            {
                "code": account.code,
                "name": account.name,
                "reconciled": account.is_reconciled,
                "creditCard": account.is_credit_card,
            }
            for account in configuration.accounts.accounts
        ],
    }


def build_personal_settings_file(configuration: Configuration) -> str:
    settings_as_text = json.dumps(
        build_personal_settings(configuration), ensure_ascii=False, indent=2
    )
    return f"{_FILE_HEADER}\nconst PERSONAL_SETTINGS = {settings_as_text};\n"


def _category(name: str, group: str, kind: TransactionType) -> dict[str, str]:
    """Income, savings and investments get their group name from the app's language."""
    return {"name": name, "group": group, "kind": str(kind)}
