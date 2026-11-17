import pytest

from notes_to_budget.configuration.accounts_loader import load_account_catalog
from notes_to_budget.configuration.configuration_error import ConfigurationError

VALID_ACCOUNTS = """
    accounts:
      - code: C
        name: Cash
        reconciled: true
        balance_position: 1
        also_written_as: [cash]
      - code: R
        name: Online wallet
        reconciled: true
        balance_position: 2
        also_written_as: [Revolut, E]
      - code: CC
        name: Credit card
"""


def load_changed_accounts(write_settings_file, old_text, new_text):
    assert old_text in VALID_ACCOUNTS
    changed_file = write_settings_file("accounts.yaml", VALID_ACCOUNTS.replace(old_text, new_text))
    return load_account_catalog(changed_file)


def test_valid_accounts_are_loaded(write_settings_file):
    catalog = load_account_catalog(write_settings_file("accounts.yaml", VALID_ACCOUNTS))
    wallet = catalog.find_by_code("R")

    assert [account.code for account in catalog.accounts] == ["C", "R", "CC"]
    assert wallet.name == "Online wallet"
    assert wallet.is_reconciled
    assert wallet.balance_position == 2
    assert wallet.also_written_as == ("Revolut", "E")


def test_an_account_is_not_reconciled_unless_the_settings_say_so(write_settings_file):
    catalog = load_account_catalog(write_settings_file("accounts.yaml", VALID_ACCOUNTS))
    credit_card = catalog.find_by_code("CC")

    assert not credit_card.is_reconciled
    assert credit_card.balance_position is None


def test_an_account_is_a_credit_card_only_when_the_settings_say_so(write_settings_file):
    catalog = load_changed_accounts(
        write_settings_file, "name: Credit card", "name: Credit card\n        credit_card: true"
    )

    assert catalog.find_by_code("CC").is_credit_card
    assert not catalog.find_by_code("C").is_credit_card


def test_the_same_code_for_two_accounts_is_reported(write_settings_file):
    with pytest.raises(ConfigurationError) as problem:
        load_changed_accounts(write_settings_file, "code: CC", "code: C")

    assert problem.value.message_key == "configuration.account_written_the_same_way_twice"


def test_an_alias_that_is_another_accounts_code_is_reported(write_settings_file):
    with pytest.raises(ConfigurationError) as problem:
        load_changed_accounts(write_settings_file, "[Revolut, E]", "[Revolut, c]")

    assert problem.value.message_key == "configuration.account_written_the_same_way_twice"
    assert problem.value.details["written"] == "c"


def test_a_reconciled_account_without_a_balance_position_is_reported(write_settings_file):
    with pytest.raises(ConfigurationError) as problem:
        load_changed_accounts(write_settings_file, "        balance_position: 2\n", "")

    assert problem.value.message_key == "configuration.reconciled_account_needs_balance_position"
    assert problem.value.details["account"] == "R"


def test_balance_positions_with_a_gap_are_reported(write_settings_file):
    with pytest.raises(ConfigurationError) as problem:
        load_changed_accounts(write_settings_file, "balance_position: 2", "balance_position: 3")

    assert problem.value.message_key == "configuration.balance_positions_must_count_from_one"
    assert problem.value.details["positions"] == "1, 3"


def test_a_balance_position_on_an_account_that_is_not_reconciled_is_reported(write_settings_file):
    with pytest.raises(ConfigurationError) as problem:
        load_changed_accounts(
            write_settings_file,
            "name: Credit card",
            "name: Credit card\n        balance_position: 3",
        )

    assert problem.value.message_key == "configuration.balance_position_needs_reconciled_account"


def test_reconciled_must_be_true_or_false(write_settings_file):
    with pytest.raises(ConfigurationError) as problem:
        load_changed_accounts(write_settings_file, "reconciled: true", "reconciled: sometimes")

    assert problem.value.message_key == "configuration.value_must_be_yes_or_no"
    assert problem.value.details["place"] == "accounts[1].reconciled"


def test_an_empty_list_of_accounts_is_reported(write_settings_file):
    accounts_file = write_settings_file("accounts.yaml", "accounts: []\n")

    with pytest.raises(ConfigurationError) as problem:
        load_account_catalog(accounts_file)

    assert problem.value.message_key == "configuration.no_accounts"
