"""Writes the Google script that creates a person's form and spreadsheet."""

import json
from importlib import resources

from notes_to_budget.configuration.configuration import Configuration
from notes_to_budget.google_form.form_setup import build_form_setup
from notes_to_budget.localization.translator import Translator

SCRIPT_TEMPLATE_FILE_NAME = "create_budget_form.template.gs"
FINISHED_SCRIPT_FILE_NAME = "create_budget_form.gs"
SETUP_PLACEHOLDER = "/*SETUP_PLACEHOLDER*/ null"


def build_form_script(configuration: Configuration, translator: Translator) -> str:
    """Put the person's categories, accounts and labels into the script template."""
    template = (
        resources.files("notes_to_budget.google_form")
        .joinpath(SCRIPT_TEMPLATE_FILE_NAME)
        .read_text(encoding="utf-8")
    )
    setup = build_form_setup(configuration, translator)
    setup_as_script_text = json.dumps(setup, ensure_ascii=False, indent=2)
    return template.replace(SETUP_PLACEHOLDER, setup_as_script_text)
