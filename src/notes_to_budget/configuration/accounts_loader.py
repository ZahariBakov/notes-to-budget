"""Reads ``accounts.yaml``."""

from collections import Counter
from pathlib import Path
from typing import Any

from notes_to_budget.configuration.configuration_error import ConfigurationError
from notes_to_budget.configuration.yaml_file_reader import read_yaml_mapping
from notes_to_budget.configuration.yaml_values import (
    read_optional_text_list,
    read_optional_whole_number,
    read_optional_yes_or_no,
    read_required_list,
    read_required_text,
    require_named_values,
)
from notes_to_budget.domain.account import Account
from notes_to_budget.domain.account_catalog import AccountCatalog


def load_account_catalog(accounts_file: Path) -> AccountCatalog:
    values = read_yaml_mapping(accounts_file)
    listed_accounts = read_required_list(values, "accounts", accounts_file)

    catalog = AccountCatalog(
        accounts=tuple(
            _read_account(listed_account, f"accounts[{position}]", accounts_file)
            for position, listed_account in enumerate(listed_accounts, start=1)
        )
    )
    _check_there_is_at_least_one_account(catalog, accounts_file)
    _check_every_way_of_writing_means_one_account(catalog, accounts_file)
    _check_balance_positions(catalog, accounts_file)
    return catalog


def _read_account(listed_account: Any, place: str, accounts_file: Path) -> Account:
    account_values = require_named_values(listed_account, accounts_file, place)
    return Account(
        code=read_required_text(account_values, "code", accounts_file, place),
        name=read_required_text(account_values, "name", accounts_file, place),
        is_reconciled=read_optional_yes_or_no(
            account_values, "reconciled", accounts_file, place, default=False
        ),
        balance_position=read_optional_whole_number(
            account_values, "balance_position", accounts_file, place
        ),
        also_written_as=read_optional_text_list(
            account_values, "also_written_as", accounts_file, place
        ),
        is_credit_card=read_optional_yes_or_no(
            account_values, "credit_card", accounts_file, place, default=False
        ),
    )


def _check_there_is_at_least_one_account(catalog: AccountCatalog, accounts_file: Path) -> None:
    if not catalog.accounts:
        raise ConfigurationError("configuration.no_accounts", file=accounts_file)


def _check_every_way_of_writing_means_one_account(
    catalog: AccountCatalog, accounts_file: Path
) -> None:
    """A code or alias used for two accounts would make the notes ambiguous."""
    ways_of_writing = [
        way_of_writing.casefold()
        for account in catalog.accounts
        for way_of_writing in (account.code, *account.also_written_as)
    ]
    times_used = Counter(ways_of_writing)
    used_twice = [way_of_writing for way_of_writing, times in times_used.items() if times > 1]
    if used_twice:
        raise ConfigurationError(
            "configuration.account_written_the_same_way_twice",
            file=accounts_file,
            written=used_twice[0],
        )


def _check_balance_positions(catalog: AccountCatalog, accounts_file: Path) -> None:
    """Reconciled accounts must fill positions 1, 2, 3... of the balances line."""
    for account in catalog.accounts:
        if account.is_reconciled and account.balance_position is None:
            raise ConfigurationError(
                "configuration.reconciled_account_needs_balance_position",
                file=accounts_file,
                account=account.code,
            )
        if not account.is_reconciled and account.balance_position is not None:
            raise ConfigurationError(
                "configuration.balance_position_needs_reconciled_account",
                file=accounts_file,
                account=account.code,
            )

    positions = sorted(
        account.balance_position for account in catalog.accounts if account.is_reconciled
    )
    expected_positions = list(range(1, len(positions) + 1))
    if positions != expected_positions:
        raise ConfigurationError(
            "configuration.balance_positions_must_count_from_one",
            file=accounts_file,
            positions=", ".join(str(position) for position in positions),
        )
