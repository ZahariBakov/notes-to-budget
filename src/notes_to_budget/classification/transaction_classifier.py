"""Turns the entries read from the notes into transactions for the ledger."""

from collections.abc import Sequence

from notes_to_budget.classification.classification_result import (
    ClassificationResult,
    EntryToClassify,
)
from notes_to_budget.classification.classification_rule import ClassificationRule
from notes_to_budget.domain.transaction import Transaction
from notes_to_budget.domain.transaction_type import TransactionType
from notes_to_budget.localization.translator import Translator
from notes_to_budget.notes_parsing.parsed_notes import ParsedNotes

NO_RULE_DECIDED = "no_rule"
SEPARATOR_BETWEEN_REVIEW_REASONS = "; "


def classify_parsed_notes(
    parsed_notes: ParsedNotes, rules: Sequence[ClassificationRule], translator: Translator
) -> list[Transaction]:
    """Classify every entry, in the order of the file.

    Nothing is guessed silently: an entry no rule could decide, an entry
    without an account and an entry the person marked as uncertain are
    all flagged for review, with the reason written in the note.
    """
    transactions = []
    for parsed_day in parsed_notes.days:
        for parsed_entry in parsed_day.entries:
            entry = EntryToClassify(day=parsed_day.day, entry=parsed_entry)
            transactions.append(_classify_entry(entry, rules, translator, parsed_notes.file_name))
    return transactions


def _classify_entry(
    entry: EntryToClassify,
    rules: Sequence[ClassificationRule],
    translator: Translator,
    file_name: str,
) -> Transaction:
    result, decided_by = _ask_the_rules(entry, rules)
    from_account_code = result.from_account_code or entry.entry.account_code or ""

    review_reason_keys = []
    if decided_by == NO_RULE_DECIDED:
        review_reason_keys.append("review.no_rule_decided")
    if result.review_reason_key:
        review_reason_keys.append(result.review_reason_key)
    if not from_account_code:
        review_reason_keys.append("review.account_missing")
    if entry.entry.is_uncertain:
        review_reason_keys.append("review.marked_uncertain")

    return Transaction(
        day=entry.day,
        amount=result.amount,
        description=entry.description,
        transaction_type=result.transaction_type,
        from_account_code=from_account_code,
        to_account_code=result.to_account_code,
        category_name=result.category_name,
        is_one_off=result.is_one_off,
        needs_review=bool(review_reason_keys),
        note=SEPARATOR_BETWEEN_REVIEW_REASONS.join(
            translator.translate(reason_key) for reason_key in review_reason_keys
        ),
        decided_by=decided_by,
        source=f"{file_name}:{entry.entry.line_number}",
    )


def _ask_the_rules(
    entry: EntryToClassify, rules: Sequence[ClassificationRule]
) -> tuple[ClassificationResult, str]:
    for rule in rules:
        result = rule.classify(entry)
        if result is not None:
            return result, rule.name
    return _undecided(entry), NO_RULE_DECIDED


def _undecided(entry: EntryToClassify) -> ClassificationResult:
    """Keep the entry, without a category, as income or expense by its sign."""
    if entry.is_money_in:
        return ClassificationResult(
            transaction_type=TransactionType.INCOME, amount=entry.entry.amount
        )
    return ClassificationResult(transaction_type=TransactionType.EXPENSE, amount=entry.entry.amount)
