import datetime
import logging
from typing import Optional

import xmltodict

import set_you_free.backend.findpapers.utils.common_utils as common_util
import set_you_free.backend.findpapers.utils.query_utils as query_util
from set_you_free.backend.findpapers.models.paper import Paper
from set_you_free.backend.findpapers.models.publication import Publication
from set_you_free.backend.findpapers.models.search import Search
from set_you_free.backend.findpapers.utils.requests_utils import DefaultSession

DATABASE_LABEL = "PubMed"
BASE_URL = "https://eutils.ncbi.nlm.nih.gov"
MAX_ENTRIES_PER_PAGE = 50


def _get_search_url(search: Search, start_record: Optional[int] = 0) -> str:
    pass


def _get_api_result(search: Search, start_record: Optional[int] = 0) -> dict:
    pass


def _get_paper_entry(pubmed_id: str) -> dict:  # pragma: no cover
    pass


def _get_publication(paper_entry: dict) -> Publication:
    pass


def _get_text_recursively(text_entry) -> str:
    pass


def _get_paper(paper_entry: dict, publication: Publication) -> Paper:
    pass


def run(search: Search, pbar=None) -> None:
    pass
