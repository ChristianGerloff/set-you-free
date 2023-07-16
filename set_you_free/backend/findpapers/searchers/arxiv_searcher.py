import logging
import re
import time
from datetime import datetime
from typing import Generator, Optional

import arxiv
from stqdm import stqdm

from set_you_free.backend.findpapers.data.subject_area_by_key import SUBJECT_AREA_BY_KEY
from set_you_free.backend.findpapers.models.paper import Paper
from set_you_free.backend.findpapers.models.publication import Publication
from set_you_free.backend.findpapers.models.search import Search

DATABASE_LABEL = "arXiv"
# BASE_URL = "http://export.arxiv.org"
MAX_ENTRIES_PER_PAGE = 200


def _arxiv_search(search: Search, start_record: Optional[int] = 0) -> Generator[arxiv.Result, None, None]:
    """Search the arXiv database using the provided search parameters.

    Args:
        search (Search): A search instance.
        start_record (Optional[int], optional): Index at which record should be searched from. Defaults to 0.

    Returns:
        Generator[arxiv.Result, None, None]: Search results.
    """
    # TODO: do we need to transform the query like it has been done in findpapers repo?
    arxiv_search = arxiv.Search(
        query=search.query,
        max_results=MAX_ENTRIES_PER_PAGE,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )
    return arxiv_search.results(offset=start_record)


def _get_publication(paper_entry: dict) -> Publication:
    """Build a publication instance using paper entry provided.

    Args:
        paper_entry (dict): A paper entry retrieved from arXiv.

    Returns:
        Publication: A Publication instance.
    """
    if "arxiv:journal_ref" in paper_entry:
        # overwrite with published title
        publication_title = paper_entry.get("arxiv:journal_ref").get("#text")

        if not publication_title:
            return None

    else:
        publication_title = DATABASE_LABEL  # unpublished preprints

    subject_areas = set()
    categories = paper_entry.get("category")
    if categories:
        if isinstance(categories, list):
            for category in categories:
                subject_area = SUBJECT_AREA_BY_KEY.get(category.get("@term"), None)
                if subject_area:
                    subject_areas.add(subject_area)
        else:
            subject_area = SUBJECT_AREA_BY_KEY.get(categories.get("@term"), None)
            if subject_area:
                subject_areas.add(subject_area)

    return Publication(title=publication_title, category="Preprint", subject_areas=subject_areas)


def _get_paper(paper_entry: dict, paper_publication_date: datetime.date, publication: Publication) -> Paper:
    """Build a paper instance using a paper entry provided.

    Args:
        paper_entry (dict): Paper entry retrieved from arXiv.
        paper_publication_date (datetime.date): Paper publication date.
        publication (Publication): A publication instance that will be associated with the paper.

    Returns:
        Paper: Paper instance.
    """
    paper_title = paper_entry.get("title")

    if not paper_title:
        return None

    paper_title = paper_title.replace("\n", "")
    paper_title = re.sub(pattern=" +", repl=" ", string=paper_title)

    paper_doi = paper_entry.get("arxiv:doi").get("#text") if "arxiv:doi" in paper_entry else None
    paper_abstract = paper_entry.get("summary")
    paper_urls = set()
    paper_authors = []

    links = paper_entry.get("link")
    if links:
        if isinstance(links, list):
            for link in links:
                paper_urls.add(link.get("@href"))
        else:
            paper_urls.add(links.get("@href"))

    authors = paper_entry.get("author")
    if authors:
        if isinstance(authors, list):
            for author in authors:
                paper_authors.append(author.get("name"))
        else:
            paper_authors.append(authors.get("name"))

    paper_comments = paper_entry.get("arxiv:comment", {}).get("#text", None)

    return Paper(
        title=paper_title,
        abstract=paper_abstract,
        authors=paper_authors,
        publication=publication,
        publication_date=paper_publication_date,
        urls=paper_urls,
        doi=paper_doi,
        comments=paper_comments,
    )


def run(search: Search, pbar: stqdm = None) -> None:
    """Fetch papers from arXiv database using the provided search parameters. After fetching the data from arXiv, the collected papers are added to the provided search instance.

    Args:
        search (Search): A search instance.
        pbar (stqdm, optional): stqdm instance for progress bar. Defaults to None.
    """
    papers_count = 0
    entries = _arxiv_search(search)

    total_papers = len(list(entries))
    logging.info(f"arXiv: {total_papers} papers to fetch")

    while papers_count < total_papers and not search.reached_its_limit(DATABASE_LABEL):
        for paper_entry in entries:
            if papers_count >= total_papers or search.reached_its_limit(DATABASE_LABEL):
                break

            papers_count += 1
            try:
                paper_title = paper_entry.title
                logging.info(f"({papers_count}/{total_papers}) Fetching arXiv paper: {paper_title}")

                published_date = datetime.strptime(str(paper_entry.published), "%Y-%m-%d %H:%M:%S%z").date()

                # nowadays we don't have a date filter on arXiv API, so we need to do it by ourselves'
                if search.since and published_date < search.since:
                    logging.info('Skipping paper due to "since" date constraint')
                    continue
                elif search.until and published_date > search.until:
                    logging.info('Skipping paper due to "until" date constraint')
                    continue

                publication = _get_publication(paper_entry=paper_entry)
                paper = _get_paper(
                    paper_entry=paper_entry,
                    paper_publication_date=published_date,
                    publication=publication,
                )

                if paper:
                    paper.add_database(DATABASE_LABEL)
                    search.add_paper(paper)

            except Exception as e:  # pragma: no cover
                logging.debug(e, exc_info=True)

            try:
                if pbar:
                    pbar.update(1)
            except Exception as e:  # pragma: no cover
                logging.debug(e, exc_info=True)

        if papers_count < total_papers and not search.reached_its_limit(DATABASE_LABEL):
            time.sleep(1)  # sleep for 1 second to avoid server blocking
            entries = _arxiv_search(search=search, start_record=papers_count)
