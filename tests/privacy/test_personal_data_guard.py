from notes_to_budget.privacy.personal_data_guard import (
    find_files_that_look_personal,
    looks_like_personal_data,
)


def test_workbooks_ledgers_and_notes_look_personal():
    assert looks_like_personal_data("Budget 2026.xlsx")
    assert looks_like_personal_data("ledger/2026/2026-10.csv")
    assert looks_like_personal_data("Записки/2026/Октомври-2026.txt")


def test_extension_is_checked_without_regard_to_letter_case():
    assert looks_like_personal_data("BUDGET.XLSX")


def test_source_code_and_documentation_do_not_look_personal():
    assert not looks_like_personal_data("src/notes_to_budget/command_line/main.py")
    assert not looks_like_personal_data("README.bg.md")
    assert not looks_like_personal_data("pyproject.toml")


def test_invented_sample_data_is_allowed_in_examples_and_fixtures():
    assert not looks_like_personal_data("examples/bg/notes/2026/Януари-2026.txt")
    assert not looks_like_personal_data("tests/fixtures/one_month_ledger.csv")


def test_a_folder_that_only_starts_like_examples_is_not_allowed():
    assert looks_like_personal_data("examples-of-mine/notes.txt")


def test_windows_style_paths_are_understood():
    assert not looks_like_personal_data("examples\\en\\notes\\2026\\January-2026.txt")
    assert looks_like_personal_data("data\\notes.txt")


def test_only_the_personal_files_are_reported_in_the_given_order():
    staged_files = ["README.md", "my-budget.xlsx", "src/app.py", "notes.txt"]

    assert find_files_that_look_personal(staged_files) == ["my-budget.xlsx", "notes.txt"]
