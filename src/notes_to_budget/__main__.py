"""Allows running the program with ``python -m notes_to_budget``."""

import sys

from notes_to_budget.command_line.main import main

if __name__ == "__main__":
    sys.exit(main())
