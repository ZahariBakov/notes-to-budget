from decimal import Decimal

from notes_to_budget.domain.transaction_type import TransactionType


def test_money_in_named_like_an_income_category_is_income(classify_one):
    salary = classify_one("+ 2000 - salary - B")

    assert salary.transaction_type is TransactionType.INCOME
    assert salary.amount == Decimal("2000")
    assert salary.category_name == "Salary"
    assert salary.decided_by == "income_rule"


def test_a_keyword_rule_may_send_money_in_to_an_income_category(classify_one):
    gift_of_money = classify_one("+ 40 - from Anna - C")

    assert gift_of_money.transaction_type is TransactionType.INCOME
    assert gift_of_money.category_name == "Additional"


def test_money_back_for_an_expense_lowers_that_category(classify_one):
    refund = classify_one("+ 5 - from John for lunch - R")

    assert refund.transaction_type is TransactionType.EXPENSE
    assert refund.amount == Decimal("-5")
    assert refund.category_name == "Food at work"
    assert refund.decided_by == "refund_rule"
    assert not refund.needs_review


def test_money_in_that_no_rule_understands_is_flagged_as_income_without_a_category(classify_one):
    unknown = classify_one("+ 17 - from Sam - R")

    assert unknown.transaction_type is TransactionType.INCOME
    assert unknown.category_name == ""
    assert unknown.needs_review
    assert unknown.decided_by == "no_rule"


def test_the_word_salary_in_an_expense_does_not_make_it_income(classify_one):
    assert classify_one("- 5 - salary party beer - C").transaction_type is TransactionType.EXPENSE


def test_a_keyword_chooses_the_category(classify_one):
    groceries = classify_one("- 35 - Lidl - R")

    assert groceries.transaction_type is TransactionType.EXPENSE
    assert groceries.amount == Decimal("35")
    assert groceries.category_name == "Groceries"
    assert groceries.from_account_code == "R"
    assert groceries.decided_by == "keyword_rule"
    assert not groceries.needs_review


def test_the_first_matching_keyword_rule_wins(classify_one):
    assert classify_one("- 7 - water and beer - R").category_name == "Groceries"


def test_an_excluded_word_makes_a_keyword_rule_step_aside(classify_one):
    alone = classify_one("- 4 - beer - C")
    with_something_else = classify_one("- 7 - beer and crisps - C")

    assert alone.category_name == "Alcohol"
    assert with_something_else.category_name == ""
    assert with_something_else.needs_review


def test_lunch_is_food_at_work_on_a_working_day_and_eating_out_at_the_weekend(classify_one):
    on_monday = classify_one("- 9 - lunch - R", day="02")
    on_saturday = classify_one("- 9 - lunch - R", day="07")
    on_sunday = classify_one("- 9 - lunch - R", day="08")

    assert on_monday.category_name == "Food at work"
    assert on_saturday.category_name == "Eating out"
    assert on_sunday.category_name == "Eating out"


def test_a_persons_name_decides_before_the_keywords(classify_one):
    for_a_child = classify_one("- 6 - lunch Mimi - C")

    assert for_a_child.category_name == "Children"
    assert for_a_child.decided_by == "people_rule"


def test_a_person_rule_steps_aside_for_its_excluded_words(classify_one):
    assert classify_one("- 129 - gift Mimi - R").category_name == "Gifts"
    assert classify_one("- 23 - burgers with Mimi - R").category_name == "Eating out"


def test_a_person_without_a_category_is_only_a_label(classify_one):
    labelled = classify_one("- 9 - parking John - R")

    assert labelled.category_name == "Transport"
    assert labelled.description == "parking John"


def test_an_expense_no_rule_understands_is_kept_without_a_category_and_flagged(classify_one):
    unknown = classify_one("- 13 - Gonzo - R")

    assert unknown.transaction_type is TransactionType.EXPENSE
    assert unknown.amount == Decimal("13")
    assert unknown.category_name == ""
    assert unknown.needs_review
    assert unknown.note == "no rule could choose a category"
    assert unknown.decided_by == "no_rule"
