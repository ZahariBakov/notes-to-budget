"""A line of the notes that needs the person's attention."""

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ParsingProblem:
    """What was wrong with one line, ready to be explained in any language."""

    line_number: int
    line_text: str
    message_key: str
    details: Mapping[str, object] = field(default_factory=dict)


class LineNotUnderstood(Exception):
    """Raised while reading one line; becomes a ``ParsingProblem`` for that line."""

    def __init__(self, message_key: str, **details: object) -> None:
        super().__init__(message_key)
        self.message_key = message_key
        self.details = details
