"""All categories of one person, with the ones that have a special meaning."""

from dataclasses import dataclass

from notes_to_budget.domain.category import Category, CategoryGroup
from notes_to_budget.domain.transaction_type import TransactionType


@dataclass(frozen=True)
class CategoryCatalog:
    expense_groups: tuple[CategoryGroup, ...]
    income_category_names: tuple[str, ...]
    savings_category_name: str
    investments_category_name: str
    fallback_category_name: str
    """The expense category for things that truly fit nowhere else."""
    lost_money_category_name: str
    """The expense category for money that is gone without a record."""

    def expense_categories(self) -> tuple[Category, ...]:
        return tuple(category for group in self.expense_groups for category in group.categories)

    def expense_category_names(self) -> tuple[str, ...]:
        return tuple(category.name for category in self.expense_categories())

    def all_category_names(self) -> tuple[str, ...]:
        return (
            *self.expense_category_names(),
            *self.income_category_names,
            self.savings_category_name,
            self.investments_category_name,
        )

    def is_known_category(self, category_name: str) -> bool:
        return category_name in self.all_category_names()

    def transaction_type_of(self, category_name: str) -> TransactionType | None:
        """What kind of money movement a category stands for."""
        if category_name in self.expense_category_names():
            return TransactionType.EXPENSE
        if category_name in self.income_category_names:
            return TransactionType.INCOME
        if category_name == self.savings_category_name:
            return TransactionType.SAVING
        if category_name == self.investments_category_name:
            return TransactionType.INVESTMENT
        return None
