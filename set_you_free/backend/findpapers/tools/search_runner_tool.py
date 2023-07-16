import copy
import datetime
import logging
import os
import re
from typing import List, Optional
from urllib.parse import urlparse

import requests
from lxml import html

import set_you_free.backend.findpapers.searchers.acm_searcher as acm_searcher
import set_you_free.backend.findpapers.searchers.arxiv_searcher as arxiv_searcher
import set_you_free.backend.findpapers.searchers.biorxiv_searcher as biorxiv_searcher
import set_you_free.backend.findpapers.searchers.cross_ref_searcher as cross_ref_searcher
import set_you_free.backend.findpapers.searchers.ieee_searcher as ieee_searcher
import set_you_free.backend.findpapers.searchers.medrxiv_searcher as medrxiv_searcher
import set_you_free.backend.findpapers.searchers.opencitations_searcher as opencitations_searcher
import set_you_free.backend.findpapers.searchers.pubmed_searcher as pubmed_searcher
import set_you_free.backend.findpapers.searchers.scopus_searcher as scopus_searcher
import set_you_free.backend.findpapers.tools.cross_references_tool as cr
import set_you_free.backend.findpapers.utils.common_utils as common_util
import set_you_free.backend.findpapers.utils.persistence_utils as persistence_util
import set_you_free.backend.findpapers.utils.publication_utils as publication_util
from set_you_free.backend.findpapers.models.paper import Paper
from set_you_free.backend.findpapers.models.publication import Publication
from set_you_free.backend.findpapers.models.search import Search
from set_you_free.backend.findpapers.utils.requests_utils import DefaultSession


def _get_paper_metadata_by_url(url: str):
    pass


def _force_single_metadata_value_by_key(metadata_entry: dict, metadata_key: str) -> None:
    pass


def _enrich(search: Search, scopus_api_token: Optional[str] = None) -> None:
    pass


def _filter(search: Search) -> None:
    pass


def _flag_potentially_predatory_publications(search: Search) -> None:
    pass


def _database_safe_run(function: callable, search: Search, database_label: str) -> None:
    pass


def _sanitize_query(query: str) -> str:
    pass


def _is_query_ok(query: str) -> bool:
    pass


def _add_refs_cites(search: Search) -> None:
    pass


def search(
    outputpath: str,
    query: Optional[str] = None,
    since: Optional[datetime.date] = None,
    until: Optional[datetime.date] = None,
    limit: Optional[int] = None,
    limit_per_database: Optional[int] = None,
    databases: Optional[List[str]] = None,
    publication_types: Optional[List[str]] = None,
    scopus_api_token: Optional[str] = None,
    ieee_api_token: Optional[str] = None,
    proxy: Optional[str] = None,
    similarity_threshold: Optional[float] = 0.95,
    rxiv_query: Optional[str] = None,
    cross_reference_search: Optional[bool] = False,
    enrich: Optional[bool] = False,
    only_title_abstract: Optional[bool] = False,
    verbose: Optional[bool] = False,
    pbar=None,
) -> dict:
    pass
