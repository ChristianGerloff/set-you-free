import logging
from datetime import date

from crossref.restful import Works

from findpapers.models.paper import Paper
from findpapers.models.publication import Publication
from findpapers.models.search import Search

# CROSSREF_API = "https://api.crossref.org/works/"
DATABASE_LABEL = "CR"  # short for opencitations
SPLIT_AUTHOR = "; "


class DateConverter(object):
    def __init__(self, date_parts: list) -> None:
        self.date_parts = date_parts
        date_functions = {3: "_ymd_date", 2: "_ym_date", 1: "_y_date"}

        date_getter = date_functions.get(len(date_parts))
        converter = getattr(self, date_getter)
        converter()
        self.date = date(year=self.year, month=self.month, day=self.day)

    def _ymd_date(self) -> None:
        self.year = int(self.date_parts[0])
        self.month = int(self.date_parts[1])
        self.day = int(self.date_parts[2])

    def _ym_date(self) -> None:
        self.year = int(self.date_parts[0])
        self.month = int(self.date_parts[1])
        self.day = 1

    def _y_date(self) -> None:
        self.year = int(self.date_parts[0])
        self.month = 1
        self.day = 1


def _get_paper_entry(doi: str) -> dict:
    """Use the DOI and extract the metadata of the paper from Crossref API.

    Args:
        doi (str): DOI of the paper.

    Returns:
        dict: Paper entry from the Crossref API.
    """
    return Works().doi(doi=doi)


def _get_publication(paper_entry: dict) -> Publication:
    """Generate publication instance from a paper entry.

    Args:
        paper_entry (dict): Paper entry retrieved from Crossref API.

    Returns:
        Publication: A publication instance.
    """
    publication_title = (
        DATABASE_LABEL if not paper_entry.get("container-title") else paper_entry.get("container-title")[0]
    )

    publication_issn = paper_entry.get("ISSN")[0] if paper_entry.get("ISSN") else None

    categories = {
        "journal-article": "Journal",
        "book-chapter": "Book",
        "book": "Book",
        "proceedings-article": "Other",
        "dataset": "Other",
        "posted-contend": "Other",
        "other": "Other",
    }
    publication_category = categories.get(paper_entry.get("type"), "Other")

    return Publication(
        title=publication_title,
        issn=publication_issn,
        publisher=paper_entry.get("publisher"),
        category=publication_category,
    )


def _get_paper(paper_entry: dict, publication: Publication) -> Paper:
    """Create a paper instance from paper entry.

    Args:
        paper_entry (dict): A paper entry retrieved from Opencitations API.
        publication (Publication): Publication instance associated with the paper.

    Returns:
        Paper: A paper instance.
    """
    title = paper_entry.get("title")

    # add only papers with titles
    if not title:
        return None

    paper_title = title[0]

    paper_abstract = paper_entry.get("abstract")

    # exclude cross-refs without abstracts
    if not paper_abstract:
        return None

    remove_abstract = ["<jats:sec>", "</jats:sec>", "<jats:title>", "</jats:title>", "<jats:p>", "</jats:p>"]
    for abstract in remove_abstract:
        paper_abstract = paper_abstract.replace(abstract, "")

    paper_authors = [f"{a.get('family')}, {a.get('given')}" for a in paper_entry.get("author", [])]

    # esnure publication date
    published = paper_entry.get("published")
    if not published:
        return None

    date_parts = paper_entry.get("published").get("date-parts")
    paper_date = DateConverter(date_parts[0]).date
    paper_urls = set()
    paper_urls.add(paper_entry.get("URL"))
    paper_doi = paper_entry.get("DOI")
    paper_pages = paper_entry.get("page")
    references = paper_entry.get("reference")
    paper_references = [d.get("DOI") for d in (references if references else [])]

    # note: check if ok i think these are counts
    return Paper(
        paper_title,
        paper_abstract,
        paper_authors,
        publication,
        paper_date,
        paper_urls,
        paper_doi,
        pages=paper_pages,
        references=paper_references,
    )


def _add_papers(search: Search, source: str) -> None:
    """Add paper to the search.

    Args:
        search (Search): A Search instance.
        source (str): Source of paper.
    """
    # get references/citations
    source_dois = [d for _, p in search.paper_by_doi.items() for d in getattr(p, source)]
    # avoid duplicates
    source_dois = list(set(source_dois))

    # gather paper metadata
    if source_dois:
        logging.info(f"Cross-References {len(source_dois)} papers found")
        for idx, doi in enumerate(source_dois):
            paper_entry = _get_paper_entry(doi=doi)
            if not paper_entry:
                continue  # doi was not found
            publication = _get_publication(paper_entry=paper_entry)
            paper = _get_paper(paper_entry=paper_entry, publication=publication)

            if paper:
                logging.info(f"({idx}/{len(source_dois)}) Fetching paper: {doi}")
                paper.source = source
                paper.add_database(database_name=DATABASE_LABEL)
                search.add_paper(paper=paper)


def run(search: Search, references: bool = True, citations: bool = True) -> None:
    """Fetch paper from Crossref API and add the collected papers to the search instance.

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