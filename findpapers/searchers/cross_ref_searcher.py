import logging
from datetime import date

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from findpapers.models.paper import Paper
from findpapers.models.publication import Publication
from findpapers.models.search import Search

CROSSREF_API = "https://api.crossref.org/works/"
DATABASE_LABEL = "CR"  # short for opencitations
SPLIT_AUTHOR = "; "


class DateConverter(object):
    def __init__(self, date_parts: list) -> None:
        self.date_parts = date_parts
        date_functions = {3: "_ymd_date", 2: "_ym_date", 1: "_y_date"}

        date_getter = date_functions.get(len(date_parts))
        converter = getattr(self, date_getter)
        converter()
        self.date = date(year=self.year, month=self.month, day=self.day)

    def _ymd_date(self) -> None:
        self.year = int(self.date_parts[0])
        self.month = int(self.date_parts[1])
        self.day = int(self.date_parts[2])

    def _ym_date(self) -> None:
        self.year = int(self.date_parts[0])
        self.month = int(self.date_parts[1])
        self.day = 1

    def _y_date(self) -> None:
        self.year = int(self.date_parts[0])
        self.month = 1
        self.day = 1


def _get_paper_entry(doi: str) -> dict:
    pass


def _get_publication(paper_entry: dict) -> Publication:
    pass


def _get_paper(paper_entry: dict, publication: Publication) -> Paper:
    pass


def _add_papers(search: Search, source: str) -> None:
    pass
