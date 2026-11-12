"""Finds the text of a message in the person's language."""

from functools import cache
from importlib import resources
from typing import Any

import yaml

SUPPORTED_LANGUAGES = ("bg", "en")
FALLBACK_LANGUAGE = "en"


class Translator:
    """Turns a message key such as ``init.created`` into a sentence.

    A message missing in the chosen language is shown in English; a key
    that exists nowhere is shown as it is, so nothing fails silently.
    """

    def __init__(self, language: str) -> None:
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Language '{language}' is not one of {SUPPORTED_LANGUAGES}.")
        self.language = language

    def translate(self, message_key: str, **values: object) -> str:
        message = find_message(self.language, message_key)
        if message is None:
            message = find_message(FALLBACK_LANGUAGE, message_key)
        if message is None:
            return message_key
        return message.format(**values)


def find_message(language: str, message_key: str) -> str | None:
    """Look up ``section.name`` in the messages of one language."""
    current_level: Any = load_messages(language)
    for key_part in message_key.split("."):
        if not isinstance(current_level, dict) or key_part not in current_level:
            return None
        current_level = current_level[key_part]
    return current_level if isinstance(current_level, str) else None


@cache
def load_messages(language: str) -> dict[str, Any]:
    messages_file = resources.files("notes_to_budget.localization").joinpath(
        "locales", f"{language}.yaml"
    )
    return yaml.safe_load(messages_file.read_text(encoding="utf-8"))
