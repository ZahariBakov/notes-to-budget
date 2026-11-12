"""Keeps printing from failing on consoles that cannot show every letter."""

import sys


def make_console_output_safe() -> None:
    """Show a replacement mark instead of crashing on an unsupported character.

    Some Windows consoles cannot display every Cyrillic or currency
    character; a message with one odd character is better than no message.
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
