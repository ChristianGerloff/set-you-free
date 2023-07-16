from decimal import Decimal

import pytest

from set_you_free.backend.findpapers.models.publication import Publication
from set_you_free.backend.tests.integration.utils.publication_utils import create_publication_event


class TestPublication:
    def test_publication_title_is_not_none(self, publication: Publication) -> None:
        assert publication.title is not None

    def test_publication_isbn_is_none(self, publication: Publication) -> None:
        publication.title = None
        with pytest.raises(ValueError) as exc_info:
            Publication.check_title(publication.title)
        assert str(exc_info.value) == "Publication's title is missing."

    def test_publication_issn_has_length_eight(self, publication: Publication) -> None:
        assert len(publication.issn) == 8

    def test_error_is_raised_when_issn_does_not_have_length_eight(self, publication: Publication) -> None:
        publication.issn = "1234567890"
        with pytest.raises(ValueError) as exc_info:
            Publication.check_issn(publication.issn)
        assert str(exc_info.value) == "Publication's ISSN must be only 8 characters long."

    def test_category(self, publication: Publication) -> None:
        assert publication.category in [
            "Journal",
            "Book",
            "Thesis",
            "Conference Proceedings",
            "Preprint",
        ]

    def test_to_dict_data_type(self, publication: Publication) -> None:
        assert isinstance(publication.dict(), dict)

    def test_from_dict_data_type(
        self,
    ) -> None:
        publication_dict = {
            "title": "Fake title",
            "isbn": "1234567890",
            "issn": "12345678",
            "publisher": "Fake publisher",
            "category": "journal",
            "cite_score": Decimal(1.0),
            "sjr": Decimal(2.0),
            "snip": Decimal(3.0),
            "subject_areas": {"Fake subject area 1", "Fake subject area 2"},
            "is_potentially_predatory": True,
        }
        publication = Publication.from_dict(publication_dict)
        assert isinstance(publication, Publication)
        assert publication.title == "Fake title"
        assert publication.isbn == "1234567890"
        assert publication.issn == "12345678"
        assert publication.publisher == "Fake publisher"
        assert publication.category == "Journal"
        assert publication.cite_score == Decimal("1.0")
        assert publication.sjr == Decimal("2.0")
        assert publication.snip == Decimal("3.0")
        assert publication.subject_areas == {"Fake subject area 1", "Fake subject area 2"}
        assert publication.is_potentially_predatory is True

    def test_publication(self, publication: Publication) -> None:
        publication.issn = None
        publication.isbn = None
        publication.cite_score = None
        publication.sjr = None
        publication.snip = None
        publication.publisher = None
        publication.category = None
        publication.subject_areas = set()

        another_publication: Publication = create_publication_event()
        another_publication.title = "Another publication"
        another_publication.cite_score = Decimal(1.0)
        another_publication.sjr = Decimal(2.0)
        another_publication.snip = Decimal(3.0)
        another_publication.subject_areas = {"area A"}

        publication.enrich(another_publication)

        assert publication.cite_score == another_publication.cite_score
        assert publication.sjr == another_publication.sjr
        assert publication.snip == another_publication.snip
        assert publication.issn == another_publication.issn
        assert publication.isbn == another_publication.isbn
        assert publication.publisher == another_publication.publisher
        assert publication.category == another_publication.category
        assert "area A" in publication.subject_areas
