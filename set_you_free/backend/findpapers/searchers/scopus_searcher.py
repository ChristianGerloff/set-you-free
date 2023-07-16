import datetime
import logging
import re
from typing import Optional

import requests
from lxml import html

import set_you_free.backend.findpapers.utils.common_utils as common_util
import set_you_free.backend.findpapers.utils.query_utils as query_util
from set_you_free.backend.findpapers.models.paper import Paper
from set_you_free.backend.findpapers.models.publication import Publication
from set_you_free.backend.findpapers.models.search import Search
from set_you_free.backend.findpapers.utils.requests_utils import DefaultSession

DATABASE_LABEL = "Scopus"
BASE_URL = "https://api.elsevier.com"


def _get_query(search: Search) -> str:
    pass


def _get_publication_entry(publication_issn: str, api_token: str) -> dict:  # pragma: no cover
    pass


def _get_publication(paper_entry: dict, api_token: str) -> Publication:
    pass


def _get_paper_page(url: str) -> object:  # pragma: no cover
    pass


def _get_paper(paper_entry: dict, publication: Publication) -> Paper:
    pass


def _get_search_results(search: Search, api_token: str, url: Optional[str] = None) -> dict:  # pragma: no cover
    pass


def enrich_publication_data(search: Search, api_token: str) -> None:
    pass


def run(search: Search, api_token: str, pbar=None, url: Optional[str] = None, papers_count: Optional[int] = 0) -> None:
    pass
