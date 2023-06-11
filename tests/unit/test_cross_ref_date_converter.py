from datetime import date

import pytest

from findpapers.searchers.cross_ref_searcher import DateConverter


@pytest.mark.parametrize(
    ("date_parts", "expected_output"),
    [
        ([2002], date(year=2002, month=1, day=1)),
        ([2020, 3], date(year=2020, month=3, day=1)),
        ([1949, 10, 12], date(year=1949, month=10, day=12)),
    ],
)
def test_correct_date_converter(date_parts: list, expected_output: date) -> None:
    assert DateConverter(date_parts).convert_date() == expected_output


@pytest.mark.parametrize(
    ("date_parts"),
    [
        ([]),
        ([1949, 10, 12, 15]),
    ],
)
def test_incorrect_date_converter(date_parts: list) -> None:
    with pytest.raises(ValueError):
        assert DateConverter(date_parts).convert_date()
