"""
Tests search class.
"""
from datetime import datetime
from pathlib import Path
from src.search import Search
import pytest


@pytest.mark.parametrize('start_date,'
                         'end_date,'
                         'search_string',
                         [(datetime.fromisoformat('2015-01-01'),
                           datetime.today().date(),
                           '[hyperscanning] AND [fNIRS]')])
def test_default_search(start_date: datetime,
                        end_date: datetime,
                        search_string: str):
    """Tests the initaliazaton and simple search."""
    filename = Path(__file__).resolve().parent / 'data' / 'test.json'
    basic_search = Search(start_date, end_date)
    basic_search.search(search_string, filename)
    pass
