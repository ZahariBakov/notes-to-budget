from pathlib import Path

import pytest

from notes_to_budget.command_line.main import main

EXAMPLES_FOLDER = Path(__file__).parents[2] / "examples"
BULGARIAN_EXAMPLE = EXAMPLES_FOLDER / "bg" / "notes" / "Март-2026.txt"
ENGLISH_EXAMPLE = EXAMPLES_FOLDER / "en" / "notes" / "March-2026.txt"


@pytest.fixture
def new_data_folder(tmp_path, capsys):
    def create(language: str) -> Path:
        main(["init", str(tmp_path), "--language", language])
        capsys.readouterr()
        return tmp_path

    return create


def test_the_english_example_is_classified_completely_by_the_starter_rules(new_data_folder, capsys):
    data_folder = new_data_folder("en")

    exit_code = main(["preview", str(ENGLISH_EXAMPLE), "--data-folder", str(data_folder)])

    printed = capsys.readouterr().out
    assert exit_code == 0
    assert "March-2026.txt: 17 entries, 0 need your review." in printed
    assert "salary  ->  Salary  [income_rule]" in printed
    assert "from card to cash  ->  B → C  [transfer_rule]" in printed
    assert "saved  ->  Savings  [savings_rule]" in printed
    assert "from John for lunch  ->  Food at work  [refund_rule]" in printed
    assert "birthday gift  ->  Celebrations and gifts  [keyword_rule]" in printed


def test_the_bulgarian_example_is_classified_completely_by_the_starter_rules(
    new_data_folder, capsys
):
    data_folder = new_data_folder("bg")

    exit_code = main(
        ["preview", str(BULGARIAN_EXAMPLE), "--month", "2026-03", "--data-folder", str(data_folder)]
    )

    printed = capsys.readouterr().out
    assert exit_code == 0
    assert "Март-2026.txt: 17 записа, 0 искат твоята проверка." in printed
    assert "заплата  ->  Заплата  [income_rule]" in printed
    assert "от карта в брой  ->  К → Б  [transfer_rule]" in printed
    assert "от Иван за обяд  ->  Хранене в работа  [refund_rule]" in printed
    assert "прехвърляне" in printed


def test_lunch_on_a_sunday_in_the_example_counts_as_eating_out(new_data_folder, capsys):
    data_folder = new_data_folder("en")

    main(["preview", str(ENGLISH_EXAMPLE), "--data-folder", str(data_folder)])

    printed_lines = capsys.readouterr().out.splitlines()
    sunday_lunch = next(line for line in printed_lines if "2026-03-01" in line and "lunch" in line)
    thursday_lunch = next(
        line for line in printed_lines if "2026-03-05" in line and "lunch" in line
    )
    assert "Eating out" in sunday_lunch
    assert "Food at work" in thursday_lunch


def test_only_entries_that_need_review_are_listed_when_asked(new_data_folder, capsys):
    data_folder = new_data_folder("en")
    notes_file = data_folder / "notes" / "short-notes"
    notes_file.write_text(
        "02.03.26 - 1 / 2 / 3\n - 35 - Lidl - R\n - 13 - Gonzo - R\n", encoding="utf-8"
    )

    main(["preview", str(notes_file), "--only-review", "--data-folder", str(data_folder)])

    printed = capsys.readouterr().out
    assert "Gonzo  ->  (no category)  [no_rule]" in printed
    assert "? no rule could choose a category" in printed
    assert "Lidl" not in printed
    assert "2 entries, 1 need your review." in printed


def test_lines_that_could_not_be_read_are_mentioned(new_data_folder, capsys):
    data_folder = new_data_folder("en")
    notes_file = data_folder / "notes" / "short-notes"
    notes_file.write_text("02.03.26 - 1 / 2 / 3\n - Lidl - R\n", encoding="utf-8")

    main(["preview", str(notes_file), "--data-folder", str(data_folder)])

    assert "1 lines could not be read" in capsys.readouterr().out
