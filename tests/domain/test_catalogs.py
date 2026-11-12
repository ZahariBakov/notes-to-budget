from notes_to_budget.domain.account import Account
from notes_to_budget.domain.account_catalog import AccountCatalog
from notes_to_budget.domain.category import Category, CategoryGroup
from notes_to_budget.domain.category_catalog import CategoryCatalog

EVERYDAY = CategoryGroup(
    name="Everyday",
    categories=(
        Category(name="Groceries", group_name="Everyday"),
        Category(name="Eating out", group_name="Everyday"),
    ),
)
OTHER = CategoryGroup(
    name="Other",
    categories=(
        Category(name="Other", group_name="Other"),
        Category(name="Lost", group_name="Other"),
    ),
)
CATEGORIES = CategoryCatalog(
    expense_groups=(EVERYDAY, OTHER),
    income_category_names=("Salary", "Rent"),
    savings_category_name="Savings",
    investments_category_name="Investments",
    fallback_category_name="Other",
    lost_money_category_name="Lost",
)


def test_expense_categories_are_listed_group_by_group():
    assert CATEGORIES.expense_category_names() == ("Groceries", "Eating out", "Other", "Lost")


def test_all_category_names_include_income_savings_and_investments():
    assert CATEGORIES.all_category_names() == (
        "Groceries",
        "Eating out",
        "Other",
        "Lost",
        "Salary",
        "Rent",
        "Savings",
        "Investments",
    )


def test_catalog_tells_whether_a_category_is_known():
    assert CATEGORIES.is_known_category("Salary")
    assert not CATEGORIES.is_known_category("Groceriez")


CASH = Account(code="C", name="Cash", is_reconciled=True, balance_position=1)
WALLET = Account(code="R", name="Online wallet", is_reconciled=True, balance_position=2)
CREDIT_CARD = Account(code="CC", name="Credit card", is_reconciled=False)


def test_account_is_found_by_its_code():
    accounts = AccountCatalog(accounts=(CASH, WALLET, CREDIT_CARD))

    assert accounts.find_by_code("R") is WALLET
    assert accounts.find_by_code("X") is None


def test_reconciled_accounts_follow_the_order_of_the_balances_line():
    accounts = AccountCatalog(accounts=(CREDIT_CARD, WALLET, CASH))

    assert accounts.reconciled_accounts_in_balance_order() == (CASH, WALLET)
