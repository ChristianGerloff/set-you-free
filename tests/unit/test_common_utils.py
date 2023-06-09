from findpapers.utils.common_utils import get_numeric_month_by_string


def test_get_numeric_month_by_string_when_ful_form_of_string_is_provided() -> None:
    assert get_numeric_month_by_string(string="January") == "01"


def test_get_numeric_month_by_string_when_short_form_of_string_is_provided() -> None:
    assert get_numeric_month_by_string(string="Mar") == "03"


def test_get_numeric_month_by_string_when_number_is_provided_as_string() -> None:
    assert get_numeric_month_by_string(string="12") == "12"


def test_get_numeric_month_by_string_when_string_is_not_valid() -> None:
    assert get_numeric_month_by_string(string="15") == "01"
    assert get_numeric_month_by_string(string="fdgdf") == "01"


def test_get_numeric_month_by_string_when_string_is_not_provided() -> None:
    assert get_numeric_month_by_string(string=None) == "01"
