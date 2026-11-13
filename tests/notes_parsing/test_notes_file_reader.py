import pytest

from notes_to_budget.notes_parsing.notes_file_reader import (
    NotesFileError,
    NumberedLine,
    read_notes_lines,
)


def test_blank_lines_are_skipped_but_line_numbers_match_the_file(tmp_path):
    notes_file = tmp_path / "notes-sample"
    notes_file.write_text("02 - 1 / 2 / 3\n\n - 8 - обяд - Р\n   \n", encoding="utf-8")

    assert read_notes_lines(notes_file) == [
        NumberedLine(number=1, text="02 - 1 / 2 / 3"),
        NumberedLine(number=3, text=" - 8 - обяд - Р"),
    ]


def test_a_file_saved_by_windows_notepad_is_read(tmp_path):
    notes_file = tmp_path / "notes-sample"
    notes_file.write_text("02 - 1 / 2 / 3\n", encoding="utf-8-sig")

    assert read_notes_lines(notes_file)[0].text == "02 - 1 / 2 / 3"


def test_a_missing_notes_file_is_reported(tmp_path):
    with pytest.raises(NotesFileError) as problem:
        read_notes_lines(tmp_path / "nowhere")

    assert problem.value.message_key == "notes.file_missing"


def test_a_file_in_another_encoding_is_reported(tmp_path):
    notes_file = tmp_path / "notes-sample"
    notes_file.write_bytes(" - 8 - обяд - Р".encode("cp1251"))

    with pytest.raises(NotesFileError) as problem:
        read_notes_lines(notes_file)

    assert problem.value.message_key == "notes.file_not_utf8"
