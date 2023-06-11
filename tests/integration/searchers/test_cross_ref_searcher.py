from datetime import date

import pytest

import findpapers.searchers.cross_ref_searcher as cross_ref_searcher
from findpapers.models.paper import Paper
from findpapers.models.publication import Publication
from findpapers.models.search import Search


@pytest.mark.usefixtures("doi")
def test_get_paper_entry(doi: str) -> None:
    paper_entry = cross_ref_searcher._get_paper_entry(doi)
    assert isinstance(paper_entry, dict)
    assert paper_entry["DOI"] == doi
    assert "title" in paper_entry
    assert "abstract" not in paper_entry
    assert "author" in paper_entry
    assert "URL" in paper_entry
    assert "published" in paper_entry
    assert "page" not in paper_entry
    assert "reference" in paper_entry
    assert "container-title" in paper_entry
    assert "ISSN" in paper_entry
    assert "type" in paper_entry


@pytest.mark.parametrize(("doi"), ["10.1016/j.powtec.2016.04.009", "10.1002/cfg.144"])
def test_get_publication(doi: str) -> None:
    paper_entry = cross_ref_searcher._get_paper_entry(doi)
    publication = cross_ref_searcher._get_publication(paper_entry)
    categories = {
        "journal-article": "Journal",
        "book-chapter": "Book",
        "book": "Book",
        "proceedings-article": "Other",
        "dataset": "Other",
        "posted-contend": "Other",
        "other": "Other",
    }
    assert isinstance(publication, Publication)
    assert publication.title == paper_entry["container-title"][0]
    assert publication.issn == paper_entry["ISSN"][0]
    assert publication.publisher == paper_entry["publisher"]
    assert publication.category == categories.get(paper_entry.get("type"), "Other")


@pytest.mark.parametrize(("doi"), ["10.1080/10260220290013453"])
def test_get_paper(doi: str) -> None:
    paper_entry = cross_ref_searcher._get_paper_entry(doi)
    publication = cross_ref_searcher._get_publication(paper_entry)
    paper = cross_ref_searcher._get_paper(paper_entry, publication)

    assert isinstance(paper, Paper)
    assert paper.title == paper_entry["title"][0]
    for tag in ["<jats:sec>", "</jats:sec>", "<jats:title>", "</jats:title>", "<jats:p>", "</jats:p>"]:
        assert tag not in paper.abstract
    assert paper.authors == ["Antoniou, I.", "Ivanov, V. V.", "Kisel, I. V."]
    assert paper.publication_date
    assert isinstance(paper.publication_date, date)


@pytest.mark.skip(reason="search.paper_by_doi is empty. This has to be corrected.")
def test_run(search: Search) -> None:
    search.limit = 14
    search.limit_per_database = None
    cross_ref_searcher.run(search)
    # assert len(search.papers) == 14
