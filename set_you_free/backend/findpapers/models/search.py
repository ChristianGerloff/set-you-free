import itertools
from datetime import date, datetime
from difflib import SequenceMatcher
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from set_you_free.backend.findpapers.data.available_databases import AVAILABLE_DATABASES
from set_you_free.backend.findpapers.exceptions import (
    DatabaseNotSelectedError,
    MissingSearchQueryError,
    UnsupportedDatabaseError,
)
from set_you_free.backend.findpapers.models.paper import Paper
from set_you_free.backend.findpapers.models.publication import Publication


class Search(BaseModel):
    query: str = Field(
        ...,
        examples=["BRAIN"],
        description="The query used to fetch the papers.",
    )
    since: Optional[date] = Field(
        None,
        examples=["2020-01-01"],
        description="The lower bound (inclusive) date of search.",
    )
    until: Optional[date] = Field(
        None,
        examples=["2020-01-01"],
        description="The upper bound (inclusive) date of search.",
    )
    limit: Optional[int] = Field(
        None,
        examples=[100],
        description="The max number of papers that can be returned in the search, when the limit is not provided the search will retrieve all the papers that it can.",
    )
    limit_per_database: Optional[int] = Field(
        None,
        examples=[5],
        description="The max number of papers that can be returned in the search for each database, when the limit is not provided the search will retrieve all the papers that it can.",
    )
    processed_at: Optional[datetime] = Field(
        None,
        examples=["2020-01-01"],
        description="The date and time when the search was processed.",
    )
    # TODO: in findpapers, this is a list of strings. Is list correct?
    # In the paper model, we have it as set, because of which in the add_database
    # method, .add isn't valid as it is valid only for set and not for list
    databases: Optional[set[str]] = Field(
        None,
        examples=["pubmed", "ACM"],
        description="The list of databases that the search will be limited to. If not provided all databases will be used.",
    )
    publication_types: Optional[list[str]] = Field(
        None,
        examples=["journal", "book"],
        description="The list of publication types that the search will be limited to. If not provided all publication types will be used.",
    )
    collected_papers: Optional[set] = Field(
        None,
        examples=["https://doi.org/10.1016/j.jbiome.2019.01.002"],
        description="A list of papers already collected.",
    )

    papers: set = set()
    paper_by_key: dict = {}
    publication_by_key: dict = {}
    paper_by_doi: dict = {}
    papers_by_database: dict = {}

    def __hash__(self) -> int:
        return self.query.__hash__()

    @field_validator("query", mode="before")
    @classmethod
    def check_query(cls, value: str) -> str:
        if not value:
            raise MissingSearchQueryError
        return value

    @field_validator("since", "until")
    @classmethod
    def validate_date(cls, value):
        return value.date() if value and isinstance(value, datetime) else value

    @field_validator("processed_at")
    @classmethod
    def assign_processed_at(cls, value) -> datetime | Any:
        return value if value else datetime.utcnow()

    @field_validator("collected_papers")
    @classmethod
    def validate_collected_papers(cls, value) -> set | None:
        if value:
            for paper in value:
                try:
                    cls.add_paper(paper)
                except Exception:
                    pass
            return None
        else:
            return set()

    def set_query(self, query: str) -> None:
        self.query = query

    def add_database(self, database_name: str) -> None:
        if database_name not in AVAILABLE_DATABASES:
            raise UnsupportedDatabaseError(database_name)
        self.databases.add(database_name)

    def get_paper_key(
        self,
        paper_title: str,
        paper_publication_date: date,
        paper_doi: Optional[str] = None,
    ) -> str:
        return (
            f"DOI-{paper_doi}"
            if paper_doi
            else f"{paper_title.lower()}|{paper_publication_date.year if paper_publication_date else ''}"
        )

    def get_publication_key(
        self,
        publication_title: str,
        publication_issn: Optional[str] = None,
        publication_isbn: Optional[str] = None,
    ) -> str:
        if publication_issn:
            return f"ISSN-{publication_issn.lower()}"
        elif publication_isbn:
            return f"ISBN-{publication_isbn.lower()}"
        else:
            return f"TITLE-{publication_title.lower()}"

    def add_paper(self, paper: Paper) -> None:
        if not paper.databases:
            raise DatabaseNotSelectedError

        databases_lowered = {db.lower() for db in self.databases}

        for database in paper.databases:
            if self.databases and database.lower() not in databases_lowered:
                raise ValueError(f"Database {database} isn't in databases list.")
            if self.reached_its_limit(database):
                raise OverflowError(
                    "When the papers limit is provided, you cannot exceed it.",
                )
            if database not in self.papers_by_database:
                self.papers_by_database[database] = set()

        if paper.publication:
            publication_key = self.get_publication_key(
                publication_title=paper.publication.title,
                publication_issn=paper.publication.issn,
                publication_isbn=paper.publication.isbn,
            )
            already_collected_publication = self.publication_by_key.get(publication_key)

            if already_collected_publication:
                already_collected_publication.enrich(paper.publication)
                paper.publication = already_collected_publication
            else:
                self.publication_by_key[publication_key] = paper.publication

        paper_key = self.get_paper_key(
            paper_title=paper.title,
            paper_publication_date=paper.publication_date,
            paper_doi=paper.doi,
        )
        already_collected_paper = self.paper_by_key.get(paper_key)

        if (self.since is None or paper.publication_date >= self.since) and (
            self.until is None or paper.publication_date <= self.until
        ):
            if not already_collected_paper:
                self.papers.add(paper)
                self.paper_by_key[paper_key] = paper

                if paper.doi:
                    self.paper_by_doi[paper.doi] = paper

                for database in paper.databases:
                    if database not in self.papers_by_database:
                        self.papers_by_database[database] = set()
                    self.papers_by_database[database].add(paper)
            else:
                self.papers_by_database[database].add(already_collected_paper)
                already_collected_paper.enrich(paper)

    def get_paper(
        self,
        paper_title: str,
        paper_publication_date: str,
        paper_doi: Optional[str] = None,
    ) -> Paper:
        paper_key = self.get_paper_key(paper_title, paper_publication_date, paper_doi)
        return self.paper_by_key.get(paper_key, None)

    def get_publication(
        self,
        title: str,
        issn: Optional[str] = None,
        isbn: Optional[str] = None,
    ) -> Publication:
        publication_key = self.get_publication_key(title, issn, isbn)
        return self.publication_by_key.get(publication_key, None)

    def remove_paper(self, paper: Paper) -> None:
        paper_key = self.get_paper_key(paper.title, paper.publication_date, paper.doi)

        if paper_key in self.paper_by_key:
            del self.paper_by_key[paper_key]

        for database in paper.databases:
            self.papers_by_database.get(database, set()).discard(paper)

        self.papers.discard(paper)

    def merge_duplications(self, similarity_threshold: float = 0.95) -> None:
        paper_key_pairs = list(itertools.combinations(self.paper_by_key.keys(), 2))

        for _, pair in enumerate(paper_key_pairs):
            paper_1 = self.paper_by_key.get(pair[0])
            paper_2 = self.paper_by_key.get(pair[1])

            # check if de-duplication can be performed
            if not (paper_1 and paper_2 and not paper_1.title and not paper_2.title):
                continue

            elif (paper_1.doi != paper_2.doi or not paper_1.doi) and (
                paper_1.abstract
                and paper_2.abstract
                and paper_1.abstract not in ["", "[No abstract available]"]
                and paper_2.abstract not in ["", "[No abstract available]"]
            ):
                max_title_length = max(len(paper_1.title), len(paper_2.title))
                diff_title_length = abs(len(paper_1.title) - len(paper_2.title))
                max_abstract_length = max(len(paper_1.abstract), len(paper_2.abstract))
                diff_abstract_length = abs(
                    len(paper_1.abstract) - len(paper_2.abstract),
                )

                # Adj: larger length differences decreasing the threshold
                adjusted_title_threshold = max(
                    similarity_threshold * (1 - 0.5 * diff_title_length / max_title_length),
                    similarity_threshold * 0.75,
                )
                adjusted_abstract_threshold = max(
                    similarity_threshold * (1 - 0.5 * diff_abstract_length / max_abstract_length),
                    similarity_threshold * 0.75,
                )

                # calculating the distance between the titles
                titles_similarity = SequenceMatcher(
                    None,
                    paper_1.title.lower(),
                    paper_2.title.lower(),
                ).ratio()
                abstracts_similarity = SequenceMatcher(
                    None,
                    paper_1.abstract.lower(),
                    paper_2.abstract.lower(),
                ).ratio()

                if (titles_similarity > adjusted_title_threshold) or (
                    abstracts_similarity > adjusted_abstract_threshold
                ):
                    # using the information of paper_2 to enrich paper_1
                    paper_1.enrich(paper_2)

                    # removing the paper_2 instance
                    self.remove_paper(paper_2)
            elif (
                (paper_1.publication_date and paper_2.publication_date)
                and (paper_1.publication_date.year == paper_2.publication_date.year)
                and (paper_1.doi and paper_1.doi == paper_2.doi)
            ):
                max_title_length = max(len(paper_1.title), len(paper_2.title))
                diff_title_length = abs(len(paper_1.title) - len(paper_2.title))

                # Adj: larger length differences decreasing the threshold
                adjusted_title_threshold = max(
                    similarity_threshold * (1 - 0.5 * diff_title_length / max_title_length),
                    similarity_threshold * 0.75,
                )

                # calculating the similarity
                titles_similarity = SequenceMatcher(
                    None,
                    paper_1.title.lower(),
                    paper_2.title.lower(),
                ).ratio()

                if titles_similarity > adjusted_title_threshold:
                    # using the information of paper_2 to enrich paper_1
                    paper_1.enrich(paper_2)

                    # removing the paper_2 instance
                    self.remove_paper(paper_2)

    def reached_its_limit(self, database: str) -> bool:
        n_dbs = len(self.papers_by_database.get(database)) if bool(self.papers_by_database.get(database)) else 0
        reached_general_limit = self.limit is not None and len(self.papers) >= self.limit
        reached_database_limit = (
            self.limit_per_database is not None
            and database in self.papers_by_database
            and n_dbs >= self.limit_per_database
        )
        return reached_general_limit or reached_database_limit

    @classmethod
    def from_dict(cls, search_dict: dict) -> "Search":
        return cls(**search_dict)
