"""Recognises an account from the way it is written in the notes."""

import re

from notes_to_budget.domain.account_catalog import AccountCatalog


class AccountCodeResolver:
    """Knows every code and every other way of writing each account.

    Letter case is ignored, so ``r`` and ``R`` mean the same account.
    """

    def __init__(self, accounts: AccountCatalog) -> None:
        self._account_code_by_way_of_writing: dict[str, str] = {}
        self._account_names: list[str] = []
        for account in accounts.accounts:
            for way_of_writing in (account.code, *account.also_written_as):
                self._account_code_by_way_of_writing[way_of_writing.casefold()] = account.code
            self._account_names.extend(account.also_written_as)

    def resolve(self, written_account: str) -> str | None:
        """Return the account code, or None when the text is not an account."""
        return self._account_code_by_way_of_writing.get(written_account.strip().casefold())

    def all_ways_of_writing(self) -> list[str]:
        """Every code and name, longest first, so "credit card" wins over "card"."""
        return sorted(self._account_code_by_way_of_writing, key=len, reverse=True)

    def find_account_named_in(self, text: str) -> str | None:
        """Find an account mentioned by name inside a sentence, such as "to cash".

        Only names are looked for, not the short codes: a one-letter code
        would be found by accident inside ordinary words.
        """
        for account_name in sorted(self._account_names, key=len, reverse=True):
            if re.search(rf"(?<!\w){re.escape(account_name)}(?!\w)", text, re.IGNORECASE):
                return self.resolve(account_name)
        return None

    def remove_account_names_from(self, text: str) -> str:
        for account_name in sorted(self._account_names, key=len, reverse=True):
            text = re.sub(
                rf"(?<!\w){re.escape(account_name)}(?!\w)", " ", text, flags=re.IGNORECASE
            )
        return text
