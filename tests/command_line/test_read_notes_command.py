from pathlib import Path

import pytest

from notes_to_budget.command_line.main import main

EXAMPLES_FOLDER = Path(__file__).parents[2] / "examples"
BULGARIAN_EXAMPLE = EXAMPLES_FOLDER / "bg" / "notes" / "Март-2026.txt"
ENGLISH_EXAMPLE = EXAMPLES_FOLDER / "en" / "notes" / "March-2026.txt"


@pytest.fixture
def new_data_folder(tmp_path, capsys):
    """Create a data folder with starter settings in the asked language."""

    def create(language: str) -> Path:
        main(["init", str(tmp_path), "--language", language])
        capsys.readouterr()
        return tmp_path

    return create


def test_the_bulgarian_example_is_read_without_problems(new_data_folder, capsys):
    data_folder = new_data_folder("bg")

    exit_code = main(
        [
            "read-notes",
            str(BULGARIAN_EXAMPLE),
            "--month",
            "2026-03",
            "--data-folder",
            str(data_folder),
        ]
    )

    printed = capsys.readouterr().out
    assert exit_code == 0
    assert "Прочетох Март-2026.txt: 6 дни, 17 записа." in printed
    assert "Всички редове са разбрани." in printed


def test_the_english_example_needs_no_month_because_it_has_full_dates(new_data_folder, capsys):
    data_folder = new_data_folder("en")

    exit_code = main(["read-notes", str(ENGLISH_EXAMPLE), "--data-folder", str(data_folder)])

    printed = capsys.readouterr().out
    assert exit_code == 0
    assert "Read March-2026.txt: 6 days, 17 entries." in printed
    assert "Every line was understood." in printed


def test_entries_are_listed_when_asked(new_data_folder, capsys):
    data_folder = new_data_folder("en")

    main(["read-notes", str(ENGLISH_EXAMPLE), "--show-entries", "--data-folder", str(data_folder)])

    printed = capsys.readouterr().out
    assert "  2026-03-02  +2000  salary  [B]" in printed
    assert "  2026-03-02  -300  from card to cash  [no account]" in printed
    assert "  2026-03-01  -3  coffee  [C]" in printed


def test_a_file_name_alone_is_looked_for_in_the_notes_folder(new_data_folder, capsys):
    data_folder = new_data_folder("bg")
    (data_folder / "Записки" / "Март-2026.txt").write_bytes(BULGARIAN_EXAMPLE.read_bytes())

    exit_code = main(
        ["read-notes", "Март-2026.txt", "--month", "2026-03", "--data-folder", str(data_folder)]
    )

    assert exit_code == 0
    assert "6 дни" in capsys.readouterr().out


def test_problem_lines_are_shown_with_their_number_reason_and_text(new_data_folder, capsys):
    data_folder = new_data_folder("bg")
    notes_file = data_folder / "Записки" / "broken-notes"
    notes_file.write_text("02 - 47 / 153 / 1500\n - обяд - Р\nкупих нещо\n", encoding="utf-8")

    exit_code = main(
        ["read-notes", str(notes_file), "--month", "2026-03", "--data-folder", str(data_folder)]
    )

    printed = capsys.readouterr().out
    assert exit_code == 0
    assert "2 реда искат твоето внимание:" in printed
    assert "ред 2: Не намерих сумата." in printed
    assert "      - обяд - Р" in printed
    assert "ред 3: Не разбрах този ред." in printed


def test_day_numbers_without_a_month_explain_how_to_fix_it(new_data_folder, capsys):
    data_folder = new_data_folder("bg")

    main(["read-notes", str(BULGARIAN_EXAMPLE), "--data-folder", str(data_folder)])

    assert "добави --month" in capsys.readouterr().out


def test_a_missing_notes_file_is_an_error_in_the_persons_language(new_data_folder, capsys):
    data_folder = new_data_folder("bg")

    exit_code = main(["read-notes", "няма-такъв-файл", "--data-folder", str(data_folder)])

    printed = capsys.readouterr()
    assert exit_code == 1
    assert "не съществува" in printed.err


def test_a_month_written_the_wrong_way_is_explained(new_data_folder, capsys):
    data_folder = new_data_folder("en")

    exit_code = main(
        ["read-notes", str(ENGLISH_EXAMPLE), "--month", "March", "--data-folder", str(data_folder)]
    )

    printed = capsys.readouterr()
    assert exit_code == 1
    assert "2026-11" in printed.err
