"""Reads a notes file from disk, line by line."""

from dataclasses import dataclass
from pathlib import Path

from notes_to_budget.user_facing_error import UserFacingError

# "utf-8-sig" also accepts files saved by Windows Notepad.
NOTES_FILE_ENCODING = "utf-8-sig"


@dataclass(frozen=True)
class NumberedLine:
    number: int
    """The line number in the file, counted from 1, as an editor shows it."""
    text: str


class NotesFileError(UserFacingError):
    """The notes file cannot be read at all."""


def read_notes_lines(notes_file: Path) -> list[NumberedLine]:
    """Return the lines that have something written on them."""
    if not notes_file.is_file():
        raise NotesFileError("notes.file_missing", file=notes_file)
    try:
        file_text = notes_file.read_text(encoding=NOTES_FILE_ENCODING)
    except UnicodeDecodeError:
        raise NotesFileError("notes.file_not_utf8", file=notes_file) from None

    return [
        NumberedLine(number=line_number, text=line_text)
        for line_number, line_text in enumerate(file_text.splitlines(), start=1)
        if line_text.strip()
    ]
