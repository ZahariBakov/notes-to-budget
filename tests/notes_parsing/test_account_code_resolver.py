from notes_to_budget.notes_parsing.account_code_resolver import AccountCodeResolver


def test_account_is_recognised_by_its_code(accounts):
    resolver = AccountCodeResolver(accounts)

    assert resolver.resolve("C") == "C"
    assert resolver.resolve("CC") == "CC"


def test_account_is_recognised_by_another_way_of_writing_it(accounts):
    resolver = AccountCodeResolver(accounts)

    assert resolver.resolve("Revolut") == "R"
    assert resolver.resolve("credit card") == "CC"


def test_a_frequent_typo_listed_in_the_settings_is_recognised(accounts):
    assert AccountCodeResolver(accounts).resolve("E") == "R"


def test_letter_case_and_spaces_around_do_not_matter(accounts):
    resolver = AccountCodeResolver(accounts)

    assert resolver.resolve(" r ") == "R"
    assert resolver.resolve("CASH") == "C"


def test_text_that_is_not_an_account_is_not_recognised(accounts):
    resolver = AccountCodeResolver(accounts)

    assert resolver.resolve("lunch") is None
    assert resolver.resolve("") is None
