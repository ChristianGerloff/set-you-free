import pytest

from set_you_free.backend.findpapers.utils.common_utils import get_numeric_month_by_string


@pytest.mark.parametrize(("month", "expected_output"), [("January", "01"), ("March", "03"), ("October", "10")])
def test_get_numeric_month_by_string_when_full_form_of_string_is_provided(month: str, expected_output: str) -> None:
    assert get_numeric_month_by_string(string=month) == expected_output


@pytest.mark.parametrize(("month", "expected_output"), [("Feb", "02"), ("May", "05"), ("Nov", "11")])
def test_get_numeric_month_by_string_when_short_form_of_string_is_provided(month: str, expected_output: str) -> None:
    assert get_numeric_month_by_string(string=month) == expected_output


@pytest.mark.parametrize(("month", "expected_output"), [("06", "06"), ("08", "08"), ("11", "11")])
def test_get_numeric_month_by_string_when_month_is_provided_as_number(month: str, expected_output: str) -> None:
    assert get_numeric_month_by_string(string=month) == expected_output


@pytest.mark.parametrize("string", ["15", "fdgdf", None])
def test_get_numeric_month_by_string_when_string_is_not_valid(string: str) -> None:
    assert get_numeric_month_by_string(string=string) == "01"
