from string import Formatter
from typing import Any

import pytest

from notes_to_budget.localization.translator import (
    SUPPORTED_LANGUAGES,
    Translator,
    load_messages,
)


def test_message_is_translated_and_filled_in():
    english = Translator("en").translate("init.created", folder="C:/budget")
    bulgarian = Translator("bg").translate("init.created", folder="C:/budget")

    assert english == "Created your data folder: C:/budget"
    assert bulgarian == "Папката с твоите данни е създадена: C:/budget"


def test_an_unknown_message_key_is_shown_as_it_is():
    assert Translator("bg").translate("no.such.message") == "no.such.message"


def test_an_unsupported_language_is_refused():
    with pytest.raises(ValueError):
        Translator("fr")


def test_curly_braces_meant_literally_survive_translation():
    message = Translator("en").translate(
        "configuration.workbook_file_name_needs_year", file="settings.yaml"
    )

    assert "{year}" in message


def all_messages_by_key(messages: dict[str, Any], prefix: str = "") -> dict[str, str]:
    """Flatten nested messages into ``section.name -> text``."""
    messages_by_key = {}
    for key, value in messages.items():
        full_key = f"{prefix}{key}"
        if isinstance(value, dict):
            messages_by_key.update(all_messages_by_key(value, prefix=f"{full_key}."))
        else:
            messages_by_key[full_key] = value
    return messages_by_key


def placeholders_of(message: str) -> set[str]:
    return {name for _, name, _, _ in Formatter().parse(message) if name}


@pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
def test_every_language_has_the_same_messages_with_the_same_placeholders(language):
    english_messages = all_messages_by_key(load_messages("en"))
    translated_messages = all_messages_by_key(load_messages(language))

    assert translated_messages.keys() == english_messages.keys()
    for message_key, english_message in english_messages.items():
        assert placeholders_of(translated_messages[message_key]) == placeholders_of(
            english_message
        ), message_key
