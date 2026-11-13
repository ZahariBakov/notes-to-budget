from notes_to_budget.classification.text_matching import (
    contains_any_keyword,
    contains_keyword,
    is_the_same_text,
    remove_keywords,
)


def test_keyword_is_found_at_the_start_of_a_word():
    assert contains_keyword("team lunch", "lunch")
    assert contains_keyword("lunches for two", "lunch")
    assert contains_keyword("обяда в офиса", "обяд")


def test_keyword_is_not_found_in_the_middle_of_a_word():
    assert not contains_keyword("rhubarb pie", "bar")
    assert not contains_keyword("поток", "ток")


def test_letter_case_does_not_matter_also_for_cyrillic():
    assert contains_keyword("ЛИДЛ", "лидл")
    assert contains_keyword("lidl", "Lidl")


def test_a_keyword_may_be_several_words():
    assert contains_keyword("taken from savings today", "from savings")


def test_any_of_several_keywords_is_enough():
    assert contains_any_keyword("bread and water", ["milk", "water"])
    assert not contains_any_keyword("bread and water", ["milk", "cheese"])
    assert not contains_any_keyword("bread", [])


def test_keywords_are_removed_together_with_their_word_endings():
    assert remove_keywords("saved for later", ["save"]).split() == ["for", "later"]


def test_descriptions_are_compared_without_case_and_extra_spaces():
    assert is_the_same_text("Gym  Membership", " gym membership ")
    assert not is_the_same_text("gym", "gym membership")
