"""Entry point of the ``notes-to-budget`` command.

Each sub-command (init, import, review, reconcile, build) will live in its
own file in this folder and be registered here.
"""

import argparse
from collections.abc import Sequence

from notes_to_budget import __version__

PROGRAM_NAME = "notes-to-budget"


def build_argument_parser() -> argparse.ArgumentParser:
    """Describe every command and option the program understands."""
    parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        description="Turn daily expense notes into a monthly budget workbook.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{PROGRAM_NAME} {__version__}",
    )
    return parser


def main(command_line_arguments: Sequence[str] | None = None) -> int:
    """Run the program and return the exit code (0 means success)."""
    parser = build_argument_parser()
    parser.parse_args(command_line_arguments)
    parser.print_help()
    return 0
