"""All accounts of one person."""

from dataclasses import dataclass

from notes_to_budget.domain.account import Account


@dataclass(frozen=True)
class AccountCatalog:
    accounts: tuple[Account, ...]

    def find_by_code(self, account_code: str) -> Account | None:
        for account in self.accounts:
            if account.code == account_code:
                return account
        return None

    def reconciled_accounts_in_balance_order(self) -> tuple[Account, ...]:
        """The accounts that appear in the balances line, first to last."""
        reconciled_accounts = [account for account in self.accounts if account.is_reconciled]
        return tuple(sorted(reconciled_accounts, key=lambda account: account.balance_position))
