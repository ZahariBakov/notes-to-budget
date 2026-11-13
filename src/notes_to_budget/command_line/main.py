"""Entry point of the ``notes-to-budget`` command.

Each command lives in its own file in this folder and is registered here.
"""

import argparse
import os
import sys
from collections.abc import Sequence

from notes_to_budget import __version__
from notes_to_budget.command_line.check_command import add_check_command
from notes_to_budget.command_line.console_output import make_console_output_safe
from notes_to_budget.command_line.init_command import add_init_command
from notes_to_budget.command_line.message_language import choose_message_language
from notes_to_budget.command_line.preview_command import add_preview_command
from notes_to_budget.command_line.read_notes_command import add_read_notes_command
from notes_to_budget.localization.translator import Translator
from notes_to_budget.user_facing_error import UserFacingError

PROGRAM_NAME = "notes-to-budget"
EXIT_CODE_SUCCESS = 0
EXIT_CODE_PROBLEM = 1


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
    commands = parser.add_subparsers(title="commands", metavar="<command>")
    add_init_command(commands)
    add_check_command(commands)
    add_read_notes_command(commands)
    add_preview_command(commands)
    return parser


def main(command_line_arguments: Sequence[str] | None = None) -> int:
    """Run the program and return the exit code (0 means success)."""
    make_console_output_safe()
    parser = build_argument_parser()
    arguments = parser.parse_args(command_line_arguments)

    if not hasattr(arguments, "run_command"):
        parser.print_help()
        return EXIT_CODE_SUCCESS

    try:
        return arguments.run_command(arguments)
    except UserFacingError as problem:
        translator = Translator(choose_message_language(arguments, os.environ))
        print(translator.translate(problem.message_key, **problem.details), file=sys.stderr)
        return EXIT_CODE_PROBLEM
