"""How much money each account held on the morning of one day."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class DailyBalance:
    """Balances written at the start of a day, before that day's entries."""

    day: date
    amount_by_account_code: Mapping[str, Decimal]

    def amount_for(self, account_code: str) -> Decimal | None:
        return self.amount_by_account_code.get(account_code)
