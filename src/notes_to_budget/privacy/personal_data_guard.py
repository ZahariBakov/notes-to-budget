"""Refuses commits that contain files which look like personal data.

Notes, ledgers and workbooks belong in the user's own data folder, never in
this public repository. Invented sample data is allowed in a few folders.

This file deliberately imports nothing from the rest of the project, so the
git hook can run it directly, even before the project is installed.
"""

import subprocess
import sys
from pathlib import PurePosixPath

PERSONAL_DATA_FILE_EXTENSIONS = frozenset({".xlsx", ".xlsm", ".xls", ".ods", ".csv", ".txt"})

FOLDERS_WHERE_SAMPLE_DATA_IS_ALLOWED = (
    PurePosixPath("examples"),
    PurePosixPath("tests/fixtures"),
)


def looks_like_personal_data(file_path: str) -> bool:
    """Tell whether a file in the repository could be someone's real data."""
    path = PurePosixPath(file_path.replace("\\", "/"))
    if path.suffix.lower() not in PERSONAL_DATA_FILE_EXTENSIONS:
        return False
    return not _is_inside_a_sample_data_folder(path)


def find_files_that_look_personal(file_paths: list[str]) -> list[str]:
    """Return the files that must not be committed, in the order given."""
    return [file_path for file_path in file_paths if looks_like_personal_data(file_path)]


def list_files_staged_for_commit() -> list[str]:
    """Ask git which files are about to be committed."""
    git_output = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"],
        capture_output=True,
        check=True,
    ).stdout
    file_names = git_output.decode("utf-8").split("\0")
    return [file_name for file_name in file_names if file_name]


def main() -> int:
    """Check the staged files; return 1 (which stops the commit) if any look personal."""
    personal_files = find_files_that_look_personal(list_files_staged_for_commit())
    if not personal_files:
        return 0

    print("Commit stopped: these files look like personal data.", file=sys.stderr)
    print("Комитът е спрян: тези файлове приличат на лични данни.", file=sys.stderr)
    for file_path in personal_files:
        print(f"  {file_path}", file=sys.stderr)
    print(
        "Keep your own notes, ledgers and workbooks outside this repository. "
        "Invented samples belong in examples/ or tests/fixtures/.",
        file=sys.stderr,
    )
    return 1


def _is_inside_a_sample_data_folder(path: PurePosixPath) -> bool:
    return any(path.is_relative_to(folder) for folder in FOLDERS_WHERE_SAMPLE_DATA_IS_ALLOWED)


if __name__ == "__main__":
    sys.exit(main())
