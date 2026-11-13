"""Looks for words inside a description, ignoring letter case."""

import re
from collections.abc import Iterable


def contains_keyword(text: str, keyword: str) -> bool:
    """True when a word of the text starts with the keyword.

    "lunch" is found in "lunches" and in "team lunch", but "bar" is not
    found in "rhubarb": the keyword must be at the start of a word.
    """
    return re.search(rf"(?<!\w){re.escape(keyword)}", text, re.IGNORECASE) is not None


def contains_any_keyword(text: str, keywords: Iterable[str]) -> bool:
    return any(contains_keyword(text, keyword) for keyword in keywords)


def remove_keywords(text: str, keywords: Iterable[str]) -> str:
    for keyword in sorted(keywords, key=len, reverse=True):
        text = re.sub(rf"(?<!\w){re.escape(keyword)}\w*", " ", text, flags=re.IGNORECASE)
    return text


def is_the_same_text(first_text: str, second_text: str) -> bool:
    """Compare two descriptions, ignoring letter case and extra spaces."""
    return _normalise(first_text) == _normalise(second_text)


def _normalise(text: str) -> str:
    return " ".join(text.casefold().split())
