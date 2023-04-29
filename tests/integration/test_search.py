import pytest

from datetime import date, datetime
from findpapers.models.paper import Paper
from findpapers.models.search import Search


def test_search_query_is_not_none(search: Search):
    assert search.query


def test_search_query_is_none(search: Search):
    search.query = None
    with pytest.raises(ValueError) as exc_info:
        search.check_query(search.query)
    assert str(exc_info.value) == "Search query is missing."


def test_set_query(search: Search):
    new_query = "New query"
    search.set_query(new_query)
    assert search.query == new_query


def test_to_dict_data_type(search: Search):
    assert isinstance(search.dict(), dict)


def test_incorrect_database(search: Search):
    database_name = "test"
    with pytest.raises(ValueError) as exc_info:
        search.add_database(database_name=database_name)
    assert str(exc_info.value) == f"Database {database_name} is not supported."


def test_get_paper_key(search: Search):
    paper_title = "FAKE-TITLE"
    publication_date = date(1996, 9, 8)
    paper_doi = "FAKE-DOI"

    assert (
        search.get_paper_key(
            paper_title=paper_title,
            publication_date=publication_date,
            paper_doi=paper_doi,
        )
        == f"DOI-{paper_doi}"
    )
    assert (
        search.get_paper_key(paper_title=paper_title, publication_date=publication_date)
        == f"{paper_title.lower()}|1996"
    )
    assert (
        search.get_paper_key(paper_title=paper_title, publication_date=None)
        == f"{paper_title.lower()}|"
    )


def test_get_publication_key(search: Search):
    publication_title = "FAKE-TITLE"
    publication_issn = "FAKE-ISSN"
    publication_isbn = "FAKE-ISBN"

    assert (
        search.get_publication_key(
            publication_title=publication_title,
            publication_issn=publication_issn,
            publication_isbn=publication_isbn,
        )
        == f"ISSN-{publication_issn.lower()}"
    )
    assert (
        search.get_publication_key(
            publication_title=publication_title, publication_issn=publication_issn
        )
        == f"ISSN-{publication_issn.lower()}"
    )
    assert (
        search.get_publication_key(
            publication_title=publication_title, publication_isbn=publication_isbn
        )
        == f"ISBN-{publication_isbn.lower()}"
    )
    assert (
        search.get_publication_key(publication_title=publication_title)
        == f"TITLE-{publication_title.lower()}"
    )


# TODO: these have to be corrected once the add_paper method is correctly implemented
# def test_get_paper(paper: Paper, search: Search):
#     search.add_paper(paper)
#     assert paper == search.get_paper(
#         paper_title=paper.title,
#         publication_date=paper.publication_date,
#         paper_doi=paper.doi,
#     )


# def test_get_publication(paper: Paper, search: Search):
#     search.add_paper(paper)
#     assert paper.publication == search.get_publication(
#         title=paper.publication.title,
#         issn=paper.publication.issn,
#         isbn=paper.publication.isbn,
#     )


def test_from_dict_data_type():
    search_dict = {
        "query": "Random query",
        "since": date(1996, 9, 8),
        "until": date(1976, 12, 18),
        "limit": 5901,
        "limit_per_database": 1787,
        "processed_at": datetime(2023, 4, 29, 18, 32, 33, 553128),
        "databases": None,
        "publication_types": ["yjfOpAUyziWVnFkQGmIu"],
        "papers": set(),
        "paper_by_key": {},
        "publication_by_key": {},
        "paper_by_doi": {},
        "papers_by_database": {},
    }
    search = Search.from_dict(search_dict)
    assert isinstance(search, Search)
    assert search.query == "Random query"
    assert search.since == date(1996, 9, 8)
    assert search.until == date(1976, 12, 18)
    assert search.limit == 5901
    assert search.limit_per_database == 1787
    assert search.processed_at == datetime(2023, 4, 29, 18, 32, 33, 553128)
    assert not search.databases
    assert isinstance(search.publication_types, list)
    assert search.publication_types == ["yjfOpAUyziWVnFkQGmIu"]
    assert isinstance(search.papers, set)
    assert isinstance(search.paper_by_key, dict)
    assert not search.paper_by_key
    assert isinstance(search.publication_by_key, dict)
    assert not search.publication_by_key
    assert isinstance(search.paper_by_doi, dict)
    assert not search.paper_by_doi
    assert isinstance(search.papers_by_database, dict)
    assert not search.papers_by_database


def test_search(paper: Paper, search: Search):
    paper.doi = None
    assert not search.papers  # can be either 0 or none
