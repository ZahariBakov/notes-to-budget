"""Notices days that are repeated or out of order in the notes.

Such days usually mean a typo in the date or a day that belongs to
another month, so the person should look at them.
"""

from collections.abc import Sequence

from notes_to_budget.notes_parsing.parsed_notes import ParsedDay
from notes_to_budget.notes_parsing.parsing_problem import ParsingProblem


def find_days_that_are_repeated_or_out_of_order(
    days: Sequence[ParsedDay], line_text_by_number: dict[int, str], *, newest_day_first: bool
) -> list[ParsingProblem]:
    problems = []
    days_seen_so_far = set()
    previous_day = None

    for parsed_day in days:
        line_text = line_text_by_number[parsed_day.line_number]
        if parsed_day.day in days_seen_so_far:
            problems.append(
                ParsingProblem(
                    line_number=parsed_day.line_number,
                    line_text=line_text,
                    message_key="notes.problem.day_repeated",
                    details={"day": parsed_day.day.isoformat()},
                )
            )
        elif previous_day is not None and _breaks_the_order(
            previous_day.day, parsed_day.day, newest_day_first
        ):
            problems.append(
                ParsingProblem(
                    line_number=parsed_day.line_number,
                    line_text=line_text,
                    message_key=_out_of_order_message_key(newest_day_first),
                    details={"day": parsed_day.day.isoformat()},
                )
            )
        days_seen_so_far.add(parsed_day.day)
        previous_day = parsed_day
    return problems


def _breaks_the_order(previous_day, this_day, newest_day_first: bool) -> bool:
    if newest_day_first:
        return this_day > previous_day
    return this_day < previous_day


def _out_of_order_message_key(newest_day_first: bool) -> str:
    if newest_day_first:
        return "notes.problem.day_out_of_order_newest_first"
    return "notes.problem.day_out_of_order_oldest_first"
