import logging
from datetime import date

import requests

from findpapers.models.paper import Paper
from findpapers.models.publication import Publication
from findpapers.models.search import Search

OPENCITATIONS_API = "https://opencitations.net/index/api/v1/metadata/"
DATABASE_LABEL = "OC"  # short for opencitations
SPLIT_AUTHOR = "; "


def _get_paper_entry(doi: str) -> dict:
    """Use the DOI and extract the metadata of the paper from Opencitations API.

    Args:
        doi (str): DOI of the paper.

    Returns:
        dict: Paper entry from the Opencitations API.
    """
    return requests.get(url=OPENCITATIONS_API + doi).json()[0]


def _get_publication(paper_entry: dict) -> Publication:
    """Generate publication instance from a paper entry.

    Args:
        paper_entry (dict): Paper entry retrieved from Opencitations API.

    Returns:
        Publication: A Publication instance.
    """
    publication_title = paper_entry.get("source_title")

    if not publication_title:
        publication_title = DATABASE_LABEL

    # publication_category = 'Preprint' if publication_title is None else None
    publication_category = None

    return Publication(title=publication_title, category=publication_category)


def _get_paper(paper_entry: dict, publication: Publication) -> Paper:
    """Create paper instance from paper entry.

    Args:
        paper_entry (dict): A paper entry retrieved from Opencitations API.
        publication (Publication): Publication instance associated with the paper.

    Returns:
        Paper: A Paper instance.
    """
    paper_title = paper_entry.get("title")
    paper_abstract = None
    paper_authors = paper_entry.get("author").split(SPLIT_AUTHOR)
    paper_publication_year = int(paper_entry.get("year"))
    paper_publication_date = date(year=paper_publication_year, month=1, day=1)
    paper_urls = [paper_entry.get("oa_link")]
    paper_doi = paper_entry.get("doi")
    paper_pages = paper_entry.get("page")
    paper_citations_count = paper_entry.get("citation_count")

    paper_citations = []
    paper_references = []

    # add cross references as a list of clean DOIs
    if len(paper_entry.get("citation")) > 0:
        paper_citations = paper_entry.get("citation").replace(" ", "").split(";")
    if len(paper_entry.get("reference")) > 0:
        paper_references = paper_entry.get("reference").replace(" ", "").split(";")

    # note: check if ok i think these are counts
    return Paper(
        title=paper_title,
        abstract=paper_abstract,
        authors=paper_authors,
        publication=publication,
        publication_date=paper_publication_date,
        urls=paper_urls,
        doi=paper_doi,
        citations=paper_citations_count,
        pages=paper_pages,
        references=paper_references,
        cites=paper_citations,
    )


def _add_papers(search: Search, source: str) -> None:
    """Add paper to the search.

    Args:
        search (Search): A Search instance.
        source (str): Source of paper.
    """
    # get references/citations
    source_dois = [d for _, p in search.paper_by_doi.items() for d in getattr(p, source)]

    # gather paper metadata
    if source_dois:
        logging.info(f"Opencitations: {len(source_dois)} papers found")
        for idx, doi in enumerate(source_dois):
            paper_entry = _get_paper_entry(doi=doi)
            publication = _get_publication(paper_entry=paper_entry)
            paper = _get_paper(paper_entry=paper_entry, publication=publication)

            if paper:
                logging.info(f"({idx}/{len(source_dois)}) Fetching paper: {doi}")
                paper.source = source
                paper.add_database(database_name=DATABASE_LABEL)
                search.add_paper(paper=paper)


def run(search: Search, references: bool = True, citations: bool = True) -> None:
    """Fetch paper from Opencitations API and add the collected papers to the search instance.

    Args:
        search (Search): A Search instance.
        references (bool, optional): If references should be used. Defaults to True.
        citations (bool, optional): If citations should be used. Defaults to True.
    """
    try:
        if references:
            _add_papers(search=search, source="references")
        if citations:
            _add_papers(search=search, source="cites")
    except Exception as e:
        logging.debug(e, exc_info=True)
