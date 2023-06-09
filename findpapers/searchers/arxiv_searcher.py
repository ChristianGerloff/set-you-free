import datetime
import logging
import math
import re
import time
from typing import Optional

import requests
import xmltodict
from lxml import html

import findpapers.utils.common_utils as common_util
import findpapers.utils.query_utils as query_util
from findpapers.models.paper import Paper
from findpapers.models.publication import Publication
from findpapers.models.search import Search
from findpapers.utils.requests_utils import DefaultSession

from findpapers.data.subject_area_by_key import SUBJECT_AREA_BY_KEY

DATABASE_LABEL = "arXiv"
BASE_URL = "http://export.arxiv.org"
MAX_ENTRIES_PER_PAGE = 200


def _get_search_url(search: Search, start_record: Optional[int] = 0) -> str:
    pass


# pragma: no cover
def _get_api_result(search: Search, start_record: Optional[int] = 0) -> dict:
    pass


def _get_publication(paper_entry: dict) -> Publication:
    pass


def _get_paper(paper_entry: dict, paper_publication_date: datetime.date, publication: Publication) -> Paper:
    pass


def run(search: Search, pbar=None) -> None:
    pass
