import datetime
import logging
import math
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

DATABASE_LABEL = "IEEE"
BASE_URL = "http://ieeexploreapi.ieee.org"
MAX_ENTRIES_PER_PAGE = 200


def _get_search_url(search: Search, api_token: str, start_record: Optional[int] = 1) -> str:
    pass


def _get_api_result(search: Search, api_token: str, start_record: Optional[int] = 1) -> dict:  # pragma: no cover
    pass


def _get_publication(paper_entry: dict) -> Publication:
    pass


def _get_paper(paper_entry: dict, publication: Publication) -> Paper:
    pass


def run(search: Search, api_token: str, pbar=None) -> None:
    pass
