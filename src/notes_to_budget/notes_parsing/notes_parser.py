"""Reads a whole notes file: decides what each line is and collects the result."""

from collections.abc import Sequence
from dataclasses import dataclass, field, replace

from notes_to_budget.configuration.notes_format import NotesFormat
from notes_to_budget.domain.account_catalog import AccountCatalog
from notes_to_budget.domain.daily_balance import DailyBalance
from notes_to_budget.domain.month import Month
from notes_to_budget.notes_parsing.account_code_resolver import AccountCodeResolver
from notes_to_budget.notes_parsing.day_header_parser import (
    DayHeader,
    looks_like_day_header,
    parse_day_header,
)
from notes_to_budget.notes_parsing.day_order_checker import (
    find_days_that_are_repeated_or_out_of_order,
)
from notes_to_budget.notes_parsing.entry_line_parser import (
    looks_like_entry_line,
    parse_entry_line,
)
from notes_to_budget.notes_parsing.notes_file_reader import NumberedLine
from notes_to_budget.notes_parsing.parsed_notes import ParsedDay, ParsedEntry, ParsedNotes
from notes_to_budget.notes_parsing.parsing_problem import LineNotUnderstood, ParsingProblem
from notes_to_budget.notes_parsing.text_cleaning import remove_currency_symbol_after_numbers


@dataclass
class _DayBeingRead:
    header: DayHeader
    line_number: int
    entries: list[ParsedEntry] = field(default_factory=list)


def parse_notes(
    lines: Sequence[NumberedLine],
    *,
    file_name: str,
    month_of_the_file: Month | None,
    accounts: AccountCatalog,
    notes_format: NotesFormat,
    currency_symbol: str = "",
) -> ParsedNotes:
    """Turn the lines of a notes file into days with entries.

    A line that cannot be understood is never dropped silently: it is
    returned as a problem with its line number and the reason.
    """
    account_code_resolver = AccountCodeResolver(accounts)
    accounts_in_balance_order = accounts.reconciled_accounts_in_balance_order()
    days_being_read: list[_DayBeingRead] = []
    problems: list[ParsingProblem] = []
    current_day: _DayBeingRead | None = None

    def report_problem(line: NumberedLine, message_key: str, **details: object) -> None:
        problems.append(
            ParsingProblem(
                line_number=line.number,
                line_text=line.text.strip(),
                message_key=message_key,
                details=details,
            )
        )

    for line in lines:
        line_text = remove_currency_symbol_after_numbers(line.text, currency_symbol)
        try:
            if looks_like_day_header(line_text):
                # Forget the previous day first: if this header cannot be read,
                # the entries below it must not land in the wrong day.
                current_day = None
                header = parse_day_header(
                    line_text, month_of_the_file, len(accounts_in_balance_order)
                )
                current_day = _DayBeingRead(header=header, line_number=line.number)
                days_being_read.append(current_day)
                if header.balances_were_not_understood:
                    report_problem(
                        line,
                        "notes.problem.balances_not_understood",
                        expected=len(accounts_in_balance_order),
                    )
                if month_of_the_file is not None and not month_of_the_file.contains(header.day):
                    report_problem(
                        line,
                        "notes.problem.day_in_another_month",
                        day=header.day.isoformat(),
                        month=str(month_of_the_file),
                    )
            elif looks_like_entry_line(line_text):
                if current_day is None:
                    raise LineNotUnderstood("notes.problem.entry_without_day")
                entry = parse_entry_line(
                    line_text, line.number, account_code_resolver, notes_format.uncertain_marker
                )
                current_day.entries.append(replace(entry, original_text=line.text.strip()))
            else:
                raise LineNotUnderstood("notes.problem.line_not_understood")
        except LineNotUnderstood as line_problem:
            report_problem(line, line_problem.message_key, **line_problem.details)

    days = tuple(
        _finish_day(day_being_read, accounts_in_balance_order) for day_being_read in days_being_read
    )
    problems.extend(
        find_days_that_are_repeated_or_out_of_order(
            days,
            {line.number: line.text.strip() for line in lines},
            newest_day_first=notes_format.newest_day_first,
        )
    )
    return ParsedNotes(
        file_name=file_name,
        days=days,
        problems=tuple(sorted(problems, key=lambda problem: problem.line_number)),
    )


def _finish_day(day_being_read: _DayBeingRead, accounts_in_balance_order) -> ParsedDay:
    header = day_being_read.header
    balance = None
    if header.balance_amounts is not None:
        balance = DailyBalance(
            day=header.day,
            amount_by_account_code={
                account.code: amount
                for account, amount in zip(
                    accounts_in_balance_order, header.balance_amounts, strict=True
                )
            },
        )
    return ParsedDay(
        day=header.day,
        line_number=day_being_read.line_number,
        balance=balance,
        entries=tuple(day_being_read.entries),
    )
