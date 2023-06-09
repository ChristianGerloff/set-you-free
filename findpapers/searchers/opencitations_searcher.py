import logging
import requests

from datetime import date
from findpapers.models.paper import Paper
from findpapers.models.publication import Publication
from findpapers.models.search import Search

# from findpapers.tools.references_tool import References

OPENCITATIONS_API = "https://opencitations.net/index/api/v1/metadata/"
DATABASE_LABEL = "OC"  # short for opencitations
SPLIT_AUTHOR = "; "


def _get_paper_entry(doi: str) -> dict:
    pass


def _get_publication(paper_entry: dict) -> Publication:
    pass


def _get_paper(paper_entry: dict, publication: Publication) -> Paper:
    pass


def _add_papers(search: Search, source: str) -> None:
    pass


def run(search: Search, references: bool = True, citations: bool = True) -> None:
    pass
