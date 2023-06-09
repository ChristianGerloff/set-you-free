import datetime
import logging
from typing import Optional
from urllib.parse import urlencode

from lxml import html

import findpapers.utils.common_utils as common_util
import findpapers.utils.query_utils as query_util
from findpapers.models.paper import Paper
from findpapers.models.publication import Publication
from findpapers.models.search import Search
from findpapers.utils.requests_utils import DefaultSession

DATABASE_LABEL = "ACM"
BASE_URL = "https://dl.acm.org"
MAX_ENTRIES_PER_PAGE = 100


def _get_search_url(search: Search, start_record: Optional[int] = 0) -> str:
    pass


def _get_result(search: Search, start_record: Optional[int] = 0) -> dict:  # pragma: no cover
    pass


def _get_paper_page(url: str) -> html.HtmlElement:  # pragma: no cover
    pass


def _get_paper_metadata(doi: str) -> dict:  # pragma: no cover
    pass


def _get_paper(paper_page: html.HtmlElement, paper_doi: str, paper_url: str) -> Paper:
    pass


def run(search: Search, pbar=None) -> None:
    pass
