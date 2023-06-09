import copy
import datetime
import logging
import os
import re
from typing import List, Optional
from urllib.parse import urlparse

import requests
from lxml import html

import findpapers.searchers.acm_searcher as acm_searcher
import findpapers.searchers.arxiv_searcher as arxiv_searcher
import findpapers.searchers.biorxiv_searcher as biorxiv_searcher
import findpapers.searchers.cross_ref_searcher as cross_ref_searcher
import findpapers.searchers.ieee_searcher as ieee_searcher
import findpapers.searchers.medrxiv_searcher as medrxiv_searcher
import findpapers.searchers.opencitations_searcher as opencitations_searcher
import findpapers.searchers.pubmed_searcher as pubmed_searcher
import findpapers.searchers.scopus_searcher as scopus_searcher
import findpapers.tools.cross_references_tool as cr
import findpapers.utils.common_utils as common_util
import findpapers.utils.persistence_utils as persistence_util
import findpapers.utils.publication_utils as publication_util
from findpapers.models.paper import Paper
from findpapers.models.publication import Publication
from findpapers.models.search import Search
from findpapers.utils.requests_utils import DefaultSession


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
