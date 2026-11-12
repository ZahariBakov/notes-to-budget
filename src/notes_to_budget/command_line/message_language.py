"""Decides in which language to talk to the person."""

import argparse
from collections.abc import Mapping

from notes_to_budget.configuration.configuration_error import ConfigurationError
from notes_to_budget.configuration.data_folder import find_data_folder
from notes_to_budget.configuration.settings_loader import load_settings
from notes_to_budget.localization.translator import FALLBACK_LANGUAGE


def choose_message_language(arguments: argparse.Namespace, environment: Mapping[str, str]) -> str:
    """Prefer the language asked for on the command line, then the one in the settings.

    When neither can be found (for example the settings are broken, which
    may be the very thing we need to report), fall back to English.
    """
    language_from_command_line = getattr(arguments, "language", None)
    if language_from_command_line:
        return language_from_command_line

    try:
        data_folder = find_data_folder(getattr(arguments, "data_folder", None), environment)
        return load_settings(data_folder.settings_file).language
    except ConfigurationError:
        return FALLBACK_LANGUAGE
