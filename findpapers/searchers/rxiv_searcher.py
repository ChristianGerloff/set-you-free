import datetime
import logging
from typing import List

from lxml import html

import findpapers.utils.common_utils as common_util
import findpapers.utils.query_utils as query_util
from findpapers.models.paper import Paper
from findpapers.models.publication import Publication
from findpapers.models.search import Search
from findpapers.utils.requests_utils import DefaultSession

BASE_URL = "https://www.medrxiv.org"
API_BASE_URL = "https://api.biorxiv.org"


def _get_search_urls(search: Search, database: str) -> List[str]:
    pass


def _get_result(url: str) -> html.HtmlElement:  # pragma: no cover
    pass


def _get_result_page_data(result_page: html.HtmlElement) -> dict:
    pass


def _get_paper_metadata(doi: str, database: str) -> dict:  # pragma: no cover
    pass


def _get_data(url: str) -> List[dict]:
    pass


def _get_publication(paper_entry: dict, database: str) -> Publication:
    pass


def _get_paper(paper_metadata: dict, database: str) -> Paper:
    pass


def run(search: Search, database: str, pbar=None) -> None:
    pass
