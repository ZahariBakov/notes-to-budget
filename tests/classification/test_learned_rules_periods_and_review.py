from dataclasses import replace
from datetime import date
from decimal import Decimal

from notes_to_budget.configuration.classification_rules import LearnedRule, SpecialPeriod
from notes_to_budget.domain.transaction_type import TransactionType

SEASIDE = SpecialPeriod(
    name="Seaside",
    first_day=date(2026, 3, 5),
    last_day=date(2026, 3, 7),
    category_name="Holidays",
)


def test_an_earlier_answer_for_exactly_this_description_decides(classify_one):
    learned = classify_one("- 13 - Gonzo - R", learned_rules=(LearnedRule("gonzo", "Eating out"),))

    assert learned.category_name == "Eating out"
    assert learned.decided_by == "learned_rule"
    assert not learned.needs_review


def test_an_earlier_answer_wins_over_every_other_rule(classify_one):
    learned = classify_one("- 9 - lunch - R", learned_rules=(LearnedRule("lunch", "Other"),))

    assert learned.category_name == "Other"


def test_an_earlier_answer_applies_only_to_the_exact_description(classify_one):
    other_entry = classify_one(
        "- 9 - lunch with the team - R", learned_rules=(LearnedRule("lunch", "Other"),)
    )

    assert other_entry.category_name == "Food at work"


def test_an_earlier_answer_can_mark_the_entry_as_one_off(classify_one):
    learned = classify_one(
        "- 541 - winter tyres - R",
        learned_rules=(LearnedRule("winter tyres", "Transport", is_one_off=True),),
    )

    assert learned.is_one_off


def test_an_earlier_answer_with_an_income_category_makes_it_income(classify_one):
    learned = classify_one("+ 2700.46 - B", learned_rules=(LearnedRule("bonus", "Additional"),))
    named = classify_one("+ 500 - bonus - B", learned_rules=(LearnedRule("bonus", "Additional"),))

    assert learned.needs_review
    assert named.transaction_type is TransactionType.INCOME
    assert named.amount == Decimal("500")


def test_an_earlier_answer_for_money_back_gives_a_negative_expense(classify_one):
    refund = classify_one(
        "+ 17 - from Sam for vodka - R",
        learned_rules=(LearnedRule("from Sam for vodka", "Alcohol"),),
    )

    assert refund.transaction_type is TransactionType.EXPENSE
    assert refund.amount == Decimal("-17")


def test_everything_spent_during_a_holiday_goes_to_the_holiday_category(classify):
    transactions = classify(
        """
        06 - 1 / 2 / 3
         - 50 - dinner - C
         - 12 - beach umbrella - C
        04 - 1 / 2 / 3
         - 40 - dinner - C
        """,
        special_periods=(SEASIDE,),
    )

    assert [transaction.category_name for transaction in transactions] == [
        "Holidays",
        "Holidays",
        "Eating out",
    ]
    assert transactions[0].decided_by == "special_period_rule"


def test_transfers_savings_and_income_keep_their_meaning_during_a_holiday(classify):
    transactions = classify(
        """
        06 - 1 / 2 / 3
         - 200 - from card to cash
         - 100 - saved - C
         + 2000 - salary - B
        """,
        special_periods=(SEASIDE,),
    )

    assert [transaction.transaction_type for transaction in transactions] == [
        TransactionType.TRANSFER,
        TransactionType.SAVING,
        TransactionType.INCOME,
    ]


def test_an_earlier_answer_keeps_a_subscription_out_of_the_holiday(classify):
    transactions = classify(
        "06 - 1 / 2 / 3\n - 10 - car internet - R",
        special_periods=(SEASIDE,),
        learned_rules=(LearnedRule("car internet", "Subscriptions"),),
    )

    assert transactions[0].category_name == "Subscriptions"


def test_a_holiday_leaves_alone_the_categories_it_is_told_to(classify):
    transactions = classify(
        """
        06 - 1 / 2 / 3
         - 20 - charging - R
         - 50 - dinner - C
        """,
        special_periods=(replace(SEASIDE, categories_that_stay=("Transport",)),),
    )

    assert [transaction.category_name for transaction in transactions] == ["Transport", "Holidays"]
    assert transactions[0].decided_by == "keyword_rule"


def test_an_entry_without_an_account_is_flagged(classify_one):
    expense = classify_one("- 16 - beer")

    assert expense.category_name == "Alcohol"
    assert expense.from_account_code == ""
    assert expense.needs_review
    assert expense.note == "the account is not written"


def test_an_entry_marked_as_uncertain_is_flagged_even_when_a_rule_decided(classify_one):
    expense = classify_one("- 17 - lunch - C -?")

    assert expense.category_name == "Food at work"
    assert expense.needs_review
    assert expense.note == "you marked this entry as uncertain"


def test_several_reasons_for_review_are_all_written_in_the_note(classify_one):
    expense = classify_one("- 13 - Gonzo ?")

    assert expense.note == (
        "no rule could choose a category; the account is not written; "
        "you marked this entry as uncertain"
    )


def test_every_transaction_remembers_its_day_description_and_line_in_the_notes(classify):
    transactions = classify(
        """
        02 - 1 / 2 / 3
         - 35 - Lidl - R
        """
    )

    assert transactions[0].day == date(2026, 3, 2)
    assert transactions[0].description == "Lidl"
    assert transactions[0].source == "March.txt:3"
