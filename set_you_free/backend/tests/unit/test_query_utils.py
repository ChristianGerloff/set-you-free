from set_you_free.backend.findpapers.utils.query_utils import replace_search_term_enclosures


def test_basic_replacement_of_search_term_enclosures() -> None:
    query = "Hello [World], this is [query] utils."
    open_replacement = "("
    close_replacement = ")"
    expected_result = "Hello (World), this is (query) utils."
    assert replace_search_term_enclosures(query, open_replacement, close_replacement) == expected_result


def test_replacement_of_search_term_enclosures_on_wildcards() -> None:
    query = "This [replacement?] function [works*]."
    open_replacement = "<"
    close_replacement = ">"
    expected_result = "This <replacement?> function <works*>."
    assert (
        replace_search_term_enclosures(query, open_replacement, close_replacement, only_on_wildcards=True)
        == expected_result
    )


def test_no_replacement_of_search_term_enclosures_on_wildcard_terms() -> None:
    query = "foo,bar?[blah*]"
    open_replacement = ""
    close_replacement = ""
    expected_result = "foo,bar?blah*"
    assert replace_search_term_enclosures(query, open_replacement, close_replacement) == expected_result
