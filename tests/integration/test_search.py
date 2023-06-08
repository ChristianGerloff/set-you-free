import copy
from datetime import date, datetime

import pytest

from findpapers.models.paper import Paper
from findpapers.models.search import Search
from tests.integration.utils.paper_utils import create_paper_event


class TestSearch:
    def test_that_search_query_is_not_none(self, search: Search) -> None:
        assert search.query

    def test_that_search_query_is_none(self, search: Search) -> None:
        search.query = None
        with pytest.raises(ValueError) as exc_info:
            search.check_query(search.query)
        assert str(exc_info.value) == "Search query is missing."

    def test_set_query(self, search: Search) -> None:
        new_query = "New query"
        assert search.query != new_query

        search.set_query(new_query)
        assert search.query == new_query

    def test_to_dict_data_type(self, search: Search) -> None:
        assert isinstance(search.dict(), dict)

    def test_incorrect_database(self, search: Search) -> None:
        database_name = "test"
        with pytest.raises(ValueError) as exc_info:
            search.add_database(database_name=database_name)
        assert str(exc_info.value) == f"Database {database_name} is not supported."

    def test_get_paper_key(self, search: Search) -> None:
        paper_title = "FAKE-TITLE"
        paper_publication_date = date(1996, 9, 8)
        paper_doi = "FAKE-DOI"

        assert (
            search.get_paper_key(
                paper_title=paper_title,
                paper_publication_date=paper_publication_date,
                paper_doi=paper_doi,
            )
            == f"DOI-{paper_doi}"
        )
        assert (
            search.get_paper_key(paper_title=paper_title, paper_publication_date=paper_publication_date)
            == f"{paper_title.lower()}|1996"
        )
        assert search.get_paper_key(paper_title=paper_title, paper_publication_date=None) == f"{paper_title.lower()}|"

    def test_get_publication_key(self, search: Search) -> None:
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
            search.get_publication_key(publication_title=publication_title, publication_issn=publication_issn)
            == f"ISSN-{publication_issn.lower()}"
        )
        assert (
            search.get_publication_key(publication_title=publication_title, publication_isbn=publication_isbn)
            == f"ISBN-{publication_isbn.lower()}"
        )
        assert search.get_publication_key(publication_title=publication_title) == f"TITLE-{publication_title.lower()}"

    def test_from_dict_data_type(
        self,
    ) -> None:
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

    def test_search(self, paper: Paper, search: Search) -> None:
        paper.doi = None

        assert not search.papers  # can be either 0 or none

        # made these as None because of the following condition in search.add_paper
        # if (self.since is None or paper.publication_date >= self.since) and (
        #         self.until is None or paper.publication_date <= self.until
        #     )
        search.since = None
        search.until = None

        search.add_paper(paper)
        assert len(search.papers) == 1
        search.add_paper(paper)
        assert len(search.papers) == 1

        another_paper: Paper = create_paper_event()

        # added the title & abstract so that the paper & another_paper instance aren't equal
        another_paper.title = "awesome paper title 2"
        another_paper.abstract = "a long abstract"
        another_paper.add_database("arXiv")

        search.add_paper(another_paper)
        assert len(search.papers) == 2

        assert paper == search.get_paper(paper.title, paper.publication_date, paper.doi)
        assert paper.publication == search.get_publication(
            paper.publication.title,
            paper.publication.issn,
            paper.publication.isbn,
        )

        search.remove_paper(another_paper)
        assert len(search.papers) == 1
        assert paper in search.papers

        search.limit_per_database = 1
        with pytest.raises(OverflowError) as exc_info:
            search.add_paper(another_paper)
        assert str(exc_info.value) == "When the papers limit is provided, you cannot exceed it."

        search.limit_per_database = 2
        search.add_paper(another_paper)
        assert len(search.papers) == 2

        another_paper_2: Paper = copy.deepcopy(paper)
        another_paper_2.title = "awesome paper title 3"
        another_paper_2.abstract = "a long abstract"
        another_paper_2.databases = set()

        with pytest.raises(ValueError) as exc_info:
            search.add_paper(another_paper_2)
        assert str(exc_info.value) == ("Paper cannot be added to search without at least one defined database.")

        another_paper_2.add_database("arXiv")

        with pytest.raises(OverflowError):
            search.add_paper(another_paper_2)

        # TODO: check why this isn't working
        # search.merge_duplications()
        # assert len(search.papers) == 1
