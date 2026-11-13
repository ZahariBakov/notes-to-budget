"""Recognises an account from the way it is written in the notes."""

from notes_to_budget.domain.account_catalog import AccountCatalog


class AccountCodeResolver:
    """Knows every code and every other way of writing each account.

    Letter case is ignored, so ``r`` and ``R`` mean the same account.
    """

    def __init__(self, accounts: AccountCatalog) -> None:
        self._account_code_by_way_of_writing: dict[str, str] = {}
        for account in accounts.accounts:
            for way_of_writing in (account.code, *account.also_written_as):
                self._account_code_by_way_of_writing[way_of_writing.casefold()] = account.code

    def resolve(self, written_account: str) -> str | None:
        """Return the account code, or None when the text is not an account."""
        return self._account_code_by_way_of_writing.get(written_account.strip().casefold())
