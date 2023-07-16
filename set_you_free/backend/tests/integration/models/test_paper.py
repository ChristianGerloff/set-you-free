from datetime import date

import pytest

from set_you_free.backend.findpapers.models.paper import Paper
from set_you_free.backend.tests.integration.factories.publication_factory import (
    Publication,
    PublicationFactory,
)
from set_you_free.backend.tests.integration.utils.paper_utils import create_paper_event


class TestPaper:
    def test_paper_title_is_not_none(self, paper: Paper) -> None:
        assert paper.title is not None

    def test_paper_title_is_none(self, paper: Paper) -> None:
        paper.title = None
        with pytest.raises(ValueError) as exc_info:
            paper.check_title(paper.title)
        assert str(exc_info.value) == "Paper's title is missing."

    def test_publication_date_is_none(self, paper: Paper) -> None:
        paper.publication_date = None
        with pytest.raises(ValueError) as exc_info:
            paper.check_publication_date(paper.publication_date)
        assert str(exc_info.value) == "Paper's publication_date is missing."

    def test_incorrect_source(self, paper: Paper) -> None:
        paper.source = "qwerty"
        sources = ["primary", "references", "cites"]
        with pytest.raises(ValueError) as exc_info:
            paper.check_source(paper.source)
        assert str(exc_info.value) == f"Source of the paper is invalid. Valid sources are {sources}."

    def test_to_dict_data_type(self, paper: Paper) -> None:
        assert isinstance(paper.dict(), dict)

    def test_incorrect_database(self, paper: Paper) -> None:
        database_name = "test"
        with pytest.raises(ValueError) as exc_info:
            paper.add_database(database_name=database_name)
        assert str(exc_info.value) == f"Database {database_name} is not supported."

    def test_from_dict_data_type(
        self,
    ) -> None:
        # TODO: add categories once its function usage is cleared
        paper_dict = {
            "title": "Fake title",
            "abstract": "a long abstract",
            "authors": ["Dr Paul", "Dr John", "Dr George", "Dr Ringo"],
            "publication_date": date(1969, 1, 30),
            "urls": {"http://www.example.com:80/1:1:1"},
            "doi": "fake-doi",
            "citations": 25,
            "keywords": {"term A", "term B"},
            "comments": "some comments",
            "number_of_pages": 4,
            "pages": "1-4",
            "databases": {"arXiv", "ACM", "IEEE", "PubMed", "Scopus"},
            "publication": PublicationFactory().build(),
        }
        paper = Paper.from_dict(paper_dict)
        assert isinstance(paper, Paper)
        assert paper.title == "Fake title"
        assert paper.abstract == "a long abstract"
        assert paper.authors == ["Dr Paul", "Dr John", "Dr George", "Dr Ringo"]
        assert paper.publication_date == date(1969, 1, 30)
        assert isinstance(paper.urls, set)
        assert list(paper.urls)[0] == "http://www.example.com:80/1:1:1"
        assert paper.doi == "fake-doi"
        assert paper.citations == 25
        assert isinstance(paper.keywords, set)
        assert paper.keywords == {"term A", "term B"}
        assert paper.comments == "some comments"
        assert paper.number_of_pages == 4
        assert paper.pages == "1-4"
        assert isinstance(paper.databases, set)
        assert paper.databases == {"arXiv", "ACM", "IEEE", "PubMed", "Scopus"}
        assert isinstance(paper.publication, Publication)

    def test_paper(self, paper: Paper) -> None:
        assert len(paper.authors) == 5
        assert len(paper.databases) == 3

        paper.databases = set()
        paper.add_database("Scopus")
        paper.add_database("Scopus")
        assert len(paper.databases) == 1

        paper.add_database("ACM")
        assert len(paper.databases) == 2

        paper.add_url(list(paper.urls)[0])
        assert len(paper.urls) == 1
        paper.add_url("another://url")
        assert len(paper.urls) == 2

        paper.publication_date = None
        paper.abstract = None
        paper.authors = None
        paper.keywords = None
        paper.publication = None
        paper.doi = None
        paper.citations = 0
        paper.comments = None
        paper.number_of_pages = None
        paper.pages = None
        paper.databases = set()

        another_paper: Paper = create_paper_event()
        another_paper.citations = 10
        another_paper.doi = "DOI-X"
        another_paper.keywords = {"key-A", "key-B", "key-C"}
        another_paper.comments = "some more comments"
        another_paper.add_database("arXiv")

        paper.enrich(another_paper)
        assert paper.authors == another_paper.authors
        assert paper.publication_date == another_paper.publication_date
        assert paper.doi == another_paper.doi
        assert paper.citations == another_paper.citations
        assert paper.keywords == another_paper.keywords
        assert paper.publication == another_paper.publication
        assert paper.number_of_pages == another_paper.number_of_pages
        assert paper.pages == another_paper.pages
        assert "arXiv" in paper.databases
        assert len(paper.databases) == 4
        assert paper.comments == another_paper.comments
