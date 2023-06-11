import copy
import datetime

import pytest

import findpapers.searchers.arxiv_searcher as arxiv_searcher
from findpapers.models.publication import Publication
from findpapers.models.search import Search

paper_entry = {
    "title": "title fake",
    "published": "2020-02-27T13:35:26Z",
    "arxiv:journal_ref": {"#text": "fake publication name"},
    "category": [{"@term": "astro-ph"}],  # can be a single value
    "arxiv:doi": {"#text": "fake-doi"},
    "summary": "a long abstract",
    "link": [  # can be a single value
        {"@href": "http://fake-url-A"},
        {"@href": "http://fake-url-B"},
    ],
    "author": [  # can be a single value
        {"name": "author A"},
        {"name": "author B"},
    ],
    "arxiv:comment": {"#text": "fake comment"},
}


def test_get_publication() -> None:
    publication = arxiv_searcher._get_publication(paper_entry)

    assert publication.title == paper_entry.get("arxiv:journal_ref").get("#text")
    assert publication.isbn is None
    assert publication.issn is None
    assert publication.publisher is None
    assert publication.category == "Preprint"
    assert len(publication.subject_areas) == 1
    assert "Astrophysics" in publication.subject_areas

    alternative_paper_entry = copy.deepcopy(paper_entry)
    alternative_paper_entry["category"] = paper_entry.get("category")[0]

    publication = arxiv_searcher._get_publication(alternative_paper_entry)
    assert len(publication.subject_areas) == 1
    assert "Astrophysics" in publication.subject_areas


def test_get_paper(publication: Publication) -> None:
    publication_date = datetime.date(2020, 2, 27)
    paper = arxiv_searcher._get_paper(paper_entry, publication_date, publication)

    assert paper.publication == publication
    assert paper.title == paper_entry.get("title")
    assert paper.publication_date == publication_date
    assert paper.doi == paper_entry.get("arxiv:doi").get("#text")
    assert paper.citations is None
    assert paper.abstract == paper_entry.get("summary")
    assert len(paper.authors) == 2
    assert "author A" in paper.authors
    assert "author B" in paper.authors
    assert not paper.keywords
    assert len(paper.urls) == 2
    assert "http://fake-url-A" in paper.urls
    assert "http://fake-url-B" in paper.urls

    alternative_paper_entry = copy.deepcopy(paper_entry)
    alternative_paper_entry["link"] = paper_entry.get("link")[0]
    alternative_paper_entry["author"] = paper_entry.get("author")[0]

    paper = arxiv_searcher._get_paper(alternative_paper_entry, publication_date, publication)
    assert len(paper.urls) == 1
    assert "http://fake-url-A" in paper.urls
    assert len(paper.authors) == 1
    assert "author A" in paper.authors


@pytest.mark.skip(reason="search.paper_by_doi is empty. This has to be corrected.")
def test_run(search: Search) -> None:
    search.limit = 14
    search.limit_per_database = None
    arxiv_searcher.run(search)
    # assert len(search.papers) == 14
