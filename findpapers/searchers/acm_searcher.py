import datetime
import logging
import os
from random import choice
from typing import Optional
from urllib.parse import urlencode

import requests
from lxml import html
from stqdm import stqdm

# import findpapers.utils.common_utils as common_util
from findpapers.data.user_agents import USER_AGENTS
from findpapers.models.paper import Paper
from findpapers.models.publication import Publication
from findpapers.models.search import Search
from findpapers.utils.query_utils import replace_search_term_enclosures

# from findpapers.utils.requests_utils import DefaultSession

DATABASE_LABEL = "ACM"
BASE_URL = "https://dl.acm.org"
MAX_ENTRIES_PER_PAGE = 100


def _get_search_url(search: Search, start_record: Optional[int] = 0) -> str:
    """Return the URL to retrieve data from ACM database. See https://dl.acm.org/search/advanced for query tips.

    Args:
        search (Search): A search instance.
        start_record (Optional[int], optional): Sequence number of first record to fetch. Defaults to 0.

    Returns:
        str: URL to be used to retrieve data from ACM database.
    """
    # when a wildcard is present, the search term cannot be enclosed in quotes
    transformed_query = replace_search_term_enclosures(
        query=search.query,
        open_replacement="",
        close_replacement="",
        only_on_wildcards=True,
    )

    # some additional query transformations
    transformed_query = transformed_query.replace(" AND NOT ", " NOT ")
    transformed_query = replace_search_term_enclosures(
        query=transformed_query,
        open_replacement='"',
        close_replacement='"',
    )

    query = f"Abstract:({transformed_query}) OR Keyword:({transformed_query}) OR Title:({transformed_query})"
    url_parameters = {
        "fillQuickSearch": "false",
        "expand": "all",
        "AllField": query,
        "pageSize": MAX_ENTRIES_PER_PAGE,
        "startPage": start_record,
        "sortBy": "Ppub",
    }

    if search.since:
        url_parameters.update({"AfterMonth": search.since.month, "AfterYear": search.since.year})

    if search.until:
        url_parameters.update({"BeforeMonth": search.until.month, "BeforeYear": search.until.year})

    return f"{BASE_URL}/action/doSearch?{urlencode(url_parameters)}"


def _requests_get(url: str) -> html.HtmlElement:
    """Make a GET request to the specified ACM database URL and return the parsed HTML content.

    Args:
        url (str): ACM database URL.

    Returns:
        html.HtmlElement: Result from ACM database.
    """
    # TODO: Is this proxy block required?
    proxy = os.getenv("FINDPAPERS_PROXY")
    if proxy:
        proxies = {"http": proxy, "https": proxy}

    response = requests.get(url, headers={"User-Agent": choice(USER_AGENTS)}, proxies=proxies)
    return html.fromstring(response.content)


# TODO: does this return a dict or html.HtmlElement?
def _get_result(search: Search, start_record: Optional[int] = 0) -> html.HtmlElement:
    """Return results from ACM database using the provided search parameters.

    Args:
        search (Search): A search instance.
        start_record (Optional[int], optional): Sequence number of first record to fetch. Defaults to 0.

    Returns:
        html.HtmlElement: Result from ACM database.
    """
    url: str = _get_search_url(search, start_record)
    # TODO: Can the try_success be replaced with requests?
    # response = common_util.try_success(lambda: DefaultSession().get(url), 2)
    return _requests_get(url=url)


def _get_paper_page(url: str) -> html.HtmlElement:
    """Get a paper page element from a provided URL.

    Args:
        url (str): Paper URL.

    Returns:
        html.HtmlElement: A HTML element representing the paper given by the provided URL.
    """
    return _requests_get(url=url)


def _get_paper_metadata(doi: str) -> dict:
    """Get a paper metadata from a provided DOI.

    Args:
        doi (str): Paper DOI.

    Returns:
        dict: The ACM paper metadata, or None if there's no metadata available.
    """
    form = {"dois": doi, "targetFile": "custom-bibtex", "format": "bibTex"}

    # # TODO: Can the try_success be replaced with requests like below?
    # response = common_util.try_success(
    #     lambda: DefaultSession().post(f"{BASE_URL}/action/exportCiteProcCitation", data=form).json(), 2
    # )

    response = requests.post(f"{BASE_URL}/action/exportCiteProcCitation", data=form).json()
    return response.get("items", [{}])[0].get(doi, {})


def _get_paper(paper_page: html.HtmlElement, paper_doi: str, paper_url: str) -> Paper:
    """Build a paper instance using the paper entry provided.

    Args:
        paper_page (html.HtmlElement): A paper page retrieved from ACM.
        paper_doi (str): Paper DOI.
        paper_url (str): ACM paper URL.

    Returns:
        Paper: A Paper instance.
    """
    paper_metadata = _get_paper_metadata(paper_doi)

    if not paper_metadata:
        return None

    simple_abstract = paper_page.xpath('//*[contains(@class, "abstractSection")]/p')
    full_abstract = paper_page.xpath(
        '//*[contains(@class, "abstractSection abstractInFull")]/'
        '*[contains(@class, "abstractSection abstractInFull")]/section/p',
    )

    paper_abstract = simple_abstract[0].text if simple_abstract else full_abstract[0].text if full_abstract else None

    cite_paper = paper_page.xpath('//*[contains(@class, "article-metric citation")]//span')
    cite_miscs = paper_page.xpath('//*[@class="bibliometrics__count"]/span')

    paper_citations = int(cite_paper[0].text) if cite_paper else int(cite_miscs[0].text) if cite_miscs else None

    paper_title = paper_metadata.get("title")

    if paper_title:
        publication = Publication(
            title=paper_metadata.get("container-title"),
            isbn=paper_metadata.get("ISBN"),
            issn=paper_metadata.get("ISSN"),
            publisher=paper_metadata.get("publisher"),
            category=paper_metadata.get("type"),
        )
    else:
        publication = None

    paper_authors = [f"{a.get('family')}, {a.get('given')}" for a in paper_metadata.get("author", [])]

    if issued := paper_metadata.get("issued"):
        date_parts = issued["date-parts"][0]
        if len(date_parts) == 1:  # only year
            paper_publication_date = datetime.date(date_parts[0], 1, 1)
        else:
            paper_publication_date = datetime.date(date_parts[0], date_parts[1], date_parts[2])
    else:
        paper_publication_date = None

    if not paper_publication_date:
        return None

    paper_keywords = (
        set([x.strip() for x in paper_metadata["keyword"].split(",")]) if paper_metadata.get("keyword") else set()
    )

    paper_pages = paper_metadata.get("page")
    if paper_pages:
        paper_pages = paper_pages.replace("\u2013", "-")

    paper_number_of_pages = int(paper_metadata.get("number-of-pages") or None)

    if not paper_doi:
        paper_doi = paper_metadata.get("DOI")

    return Paper(
        title=paper_title,
        abstract=paper_abstract,
        authors=paper_authors,
        publication=publication,
        publication_date=paper_publication_date,
        urls={paper_url},
        doi=paper_doi,
        citations=paper_citations,
        keywords=paper_keywords,
        comments=None,
        number_of_pages=paper_number_of_pages,
        pages=paper_pages,
    )


def run(search: Search, pbar: stqdm = None) -> None:
    """Fetch papers from ACM database using the provided search parameters. After fetching the data from ACM, the collected papers are added to the provided search instance.

    Args:
        search (Search): A search instance.
        pbar (stqdm, optional): stqdm instance for progress bar. Defaults to None.
    """
    result = _get_result(search=search)

    try:
        total_papers = int(result.xpath('//*[@class="hitsLength"]')[0].text.strip())
    except Exception:  # pragma: no cover
        total_papers = 0

    logging.info(f"ACM: {total_papers} papers to fetch")

    papers_count = 0
    page_index = 0
    while papers_count < total_papers and not search.reached_its_limit(database=DATABASE_LABEL):
        pub_urls = [BASE_URL + x.attrib["href"] for x in result.xpath('//*[@class="hlFld-Title"]/a')]
        misc_urls = [BASE_URL + x.attrib["href"] for x in result.xpath('//*[@class="hlFld-ContentGroupTitle"]/a')]
        papers_urls = pub_urls + misc_urls

        if not papers_urls:
            break

        for paper_url in papers_urls:
            if papers_count >= total_papers or search.reached_its_limit(database=DATABASE_LABEL):
                break

            try:
                papers_count += 1
                paper_page = _get_paper_page(url=paper_url)

                if paper_url in pub_urls:
                    paper_title = paper_page.xpath('//*[@class="citation__title"]')[0].text
                else:
                    paper_title = paper_page.xpath('//*[@class="article__tocHeading"]')[3].text

                logging.info(f"({papers_count}/{total_papers}) Fetching ACM paper: {paper_title}")

                paper_doi = None
                if "/abs/" in paper_url:
                    paper_doi = paper_url.split("/abs/")[1]
                elif "/book/" in paper_url:
                    paper_doi = paper_url.split("/book/")[1]
                else:
                    paper_doi = paper_url.split("/doi/")[1]

                paper = _get_paper(paper_page=paper_page, paper_doi=paper_doi, paper_url=paper_url)

                if not paper:
                    continue

                paper.add_database(database_name=DATABASE_LABEL)
                search.add_paper(paper=paper)

            except Exception as e:  # pragma: no cover
                logging.debug(e, exc_info=True)

            try:
                if pbar:
                    pbar.update(1)
            except Exception as e:  # pragma: no cover
                logging.debug(e, exc_info=True)

        if papers_count < total_papers and not search.reached_its_limit(database=DATABASE_LABEL):
            page_index += 1
            result = _get_result(search=search, start_record=page_index)
