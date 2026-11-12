"""An expense category and the group it belongs to."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    name: str
    group_name: str
    includes: str = ""
    """A short reminder of what belongs in the category."""


@dataclass(frozen=True)
class CategoryGroup:
    name: str
    categories: tuple[Category, ...]
