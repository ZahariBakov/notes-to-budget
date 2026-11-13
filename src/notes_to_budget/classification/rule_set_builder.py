"""Puts the rules in the order they are tried.

The first rule that decides wins, so the order is the policy:

1. the person's own earlier answer for exactly this description;
2. transfers, savings and investments, which are not expenses;
3. money coming in: income, or else a refund of some expense;
4. holidays, when everything spent goes to one category;
5. people, then keywords.
"""

from notes_to_budget.classification.classification_rule import ClassificationRule
from notes_to_budget.classification.income_and_refund_rules import IncomeRule, RefundRule
from notes_to_budget.classification.investment_rule import InvestmentRule
from notes_to_budget.classification.keyword_rule import KeywordCategoryRule
from notes_to_budget.classification.learned_rule import LearnedAnswerRule
from notes_to_budget.classification.people_rule import PeopleRule
from notes_to_budget.classification.savings_rule import SavingsRule
from notes_to_budget.classification.special_period_rule import SpecialPeriodRule
from notes_to_budget.classification.transfer_rule import TransferRule
from notes_to_budget.configuration.configuration import Configuration
from notes_to_budget.notes_parsing.account_code_resolver import AccountCodeResolver


def build_classification_rules(configuration: Configuration) -> list[ClassificationRule]:
    accounts = AccountCodeResolver(configuration.accounts)
    categories = configuration.categories
    notes_format = configuration.notes_format
    people_rule = PeopleRule(configuration.person_rules)
    keyword_rule = KeywordCategoryRule(configuration.keyword_rules)
    category_finders = (people_rule, keyword_rule)

    return [
        LearnedAnswerRule(configuration.learned_rules, categories),
        TransferRule(notes_format.transfer_phrases, accounts),
        SavingsRule(
            notes_format.savings_taken_out_phrases,
            notes_format.savings_put_in_phrases,
            categories.savings_category_name,
            accounts,
        ),
        InvestmentRule(notes_format.investment_phrases, categories.investments_category_name),
        IncomeRule(categories, category_finders),
        RefundRule(categories, category_finders),
        SpecialPeriodRule(configuration.special_periods, category_finders),
        people_rule,
        keyword_rule,
    ]
