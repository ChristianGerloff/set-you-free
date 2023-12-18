import re
from datetime import date
from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator

from set_you_free.backend.findpapers.data.available_databases import AVAILABLE_DATABASES
from set_you_free.backend.findpapers.exceptions import (
    InvalidSourceError,
    PaperPublicationDateMissingError,
    PaperTitleMissingError,
    UnsupportedDatabaseError,
)
from set_you_free.backend.findpapers.models.publication import Publication


class Paper(BaseModel):
    title: str = Field(..., examples=["Fake title"], description="Title of the paper.")
    abstract: str = Field(
        ...,
        examples=["Fake abstract"],
        description="Abstract of the paper.",
    )
    authors: list[str] = Field(
        ...,
        examples=["Fake author 1", "Fake author 2"],
        description="Authors of the paper.",
    )
    publication: Publication
    publication_date: date = Field(
        ...,
        examples=["2020-01-01"],
        description="Publication date of the paper.",
    )
    urls: set[str] = Field(
        ...,
        examples=["https://en.wikipedia.org/wiki/Friends", "https://www.google.com"],
        description="URLs of the paper.",
    )
    doi: Optional[str] = Field(
        None,
        examples=["10.1016/j.jneumeth.2020.01.001"],
        description="DOI of the paper.",
    )
    citations: Optional[int] = Field(
        None,
        examples=[10],
        description="Number of citations of the paper.",
    )
    keywords: Optional[set[str]] = Field(
        None,
        examples=["Term A, Term B"],
        description="The keywords of the paper.",
    )
    comments: Optional[str] = Field(
        None,
        examples=["some comments"],
        description="The comments on the paper.",
    )
    number_of_pages: Optional[int] = Field(
        None,
        examples=[5],
        description="The number of pages of the paper.",
    )
    pages: Optional[str] = Field(
        None,
        examples=["1-5"],
        description="The pages of the paper.",
    )
    databases: Optional[set[str]] = Field(
        None,
        examples=["IEEE", "ACM"],
        description="The databases where the paper is available.",
    )
    reviewed: Optional[bool] = Field(
        False,
        description="Whether the paper is reviewed or not.",
    )
    criteria: Optional[list] = Field(
        None,
        examples=["some criteria"],
        description="The criteria used to review the paper.",
    )
    selected: Optional[bool] = Field(
        None,
        examples=[True],
        description="Whether the paper is selected or not.",
    )
    categories: Optional[bool] = Field(
        None,
        examples=[{"Facet A": ["Category A", "Category B"]}],
        description="The categories of the paper.",
    )
    references: Optional[list] = Field(
        [],
        examples=["Ref 1"],
        description="The references of the paper.",
    )
    cites: Optional[list] = Field(
        [],
        examples=["Citation 1"],
        description="The cites of the paper.",
    )
    source: str = Field(
        default="primary",
        examples=["primary"],
        description="Source of the paper.",
    )

    def __hash__(self) -> int:
        return self.title.__hash__()

    @field_validator("title")
    @classmethod
    def check_title(cls, value: str) -> str:
        if not value:
            raise PaperTitleMissingError
        return value

    @field_validator("publication_date")
    @classmethod
    def check_publication_date(cls, value: date) -> date:
        if not value:
            raise PaperPublicationDateMissingError
        return value

    @field_validator("keywords")
    @classmethod
    def check_keywords(cls, value: Union[set[str], None]) -> set[str]:
        return value if value is not None else set()

    @field_validator("databases")
    @classmethod
    def check_databases(cls, value: Union[set[str], None]) -> set[str]:
        return value if value is not None else set()

    @field_validator("source")
    @classmethod
    def check_source(cls, value: str) -> str:
        sources = ["primary", "references", "cites"]
        if value not in sources:
            raise InvalidSourceError(sources)
        return value

    def review(self, selected: bool, criteria: list = []) -> None:
        self.reviewed = True
        self.criteria = criteria
        self.selected = selected

    def add_database(self, database_name: str) -> None:
        if database_name not in AVAILABLE_DATABASES:
            raise UnsupportedDatabaseError(database_name)
        self.databases.add(database_name)

    def add_url(self, url: str) -> None:
        self.urls.add(url)

    def enrich(self, paper: "Paper") -> None:
        self.publication_date = paper.publication_date if self.publication_date is None else self.publication_date
        self.doi = paper.doi if self.doi is None else self.doi
        self.abstract = (
            paper.abstract
            if self.abstract is None or (paper.abstract is not None and len(paper.abstract) > len(self.abstract))
            else self.abstract
        )
        self.authors = (
            paper.authors
            if self.authors is None or (paper.authors is not None and len(paper.authors) > len(self.authors))
            else self.authors
        )
        self.citations = (
            paper.citations
            if self.citations is None or (paper.citations is not None and paper.citations > self.citations)
            else self.citations
        )
        self.keywords = (
            paper.keywords
            if self.keywords is None or (paper.keywords is not None and len(paper.keywords) > len(self.keywords))
            else self.keywords
        )
        self.comments = (
            paper.comments
            if self.comments is None or (paper.comments is not None and len(paper.comments) > len(self.comments))
            else self.comments
        )
        self.number_of_pages = (
            paper.number_of_pages
            if self.number_of_pages is None
            or (paper.number_of_pages is not None and paper.number_of_pages > self.number_of_pages)
            else self.number_of_pages
        )
        self.pages = (
            paper.pages
            if self.pages is None or (paper.pages is not None and len(paper.pages) > len(self.pages))
            else self.pages
        )

        for url in paper.urls:
            self.add_url(url)

        for database in paper.databases:
            self.add_database(database)

        if self.publication is None:
            self.publication = paper.publication
        elif paper.publication is not None:
            self.publication.enrich(paper.publication)

    def get_citation_key(self) -> str:
        author_key = self.authors[0].lower().replace(" ", "").replace(",", "") if len(self.authors) > 0 else "unknown"
        year_key = self.publication_date.year if self.publication_date is not None else "XXXX"
        title_key = self.title.split(" ")[0].lower()
        citation_key = re.sub(r"[^\w\d]", "", f"{author_key}{year_key}{title_key}")
        return citation_key

    # TODO: what does this do?
    def has_category_match(self, categories: dict) -> bool:
        if categories is not None and self.categories is not None:
            for facet, facet_categories in categories.items():
                for facet_category in facet_categories:
                    if facet_category in self.categories.get(facet, []):
                        return True

        return False

    @classmethod
    def from_dict(cls, paper_dict: dict) -> "Paper":
        return cls(**paper_dict)
