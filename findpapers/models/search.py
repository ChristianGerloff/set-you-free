from datetime import datetime, date

from typing import List, Optional
from pydantic import BaseModel, Field, validator
from findpapers.models.paper import Paper
from findpapers.models.publication import Publication
from findpapers.data.available_databases import AVAILABLE_DATABASES


class Search(BaseModel):
    query: str = Field(
        ..., examples=["BRAIN"], description="The query used to fetch the papers."
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
    publication_types: Optional[List[str]] = Field(
        None,
        examples=["journal", "book"],
        description="The list of publication types that the search will be limited to. If not provided all publication types will be used.",
    )
    papers: Optional[set] = Field(
        None,
        examples=["https://doi.org/10.1016/j.jbiome.2019.01.002"],
        description="A list of papers already collected.",
    )
    paper_by_key: dict = {}
    publication_by_key: dict = {}
    paper_by_doi: dict = {}
    papers_by_database: dict = {}

    @validator("query", pre=True)
    def check_query(cls, value: str) -> str:
        if not value:
            raise (ValueError("Search query is missing."))
        return value

    @validator("since", "until")
    def validate_date(cls, value):
        if value and isinstance(value, datetime):
            value = value.date()
        return value

    @validator("processed_at")
    def assign_processed_at(cls, value):
        if not value:
            return datetime.utcnow()
        return value

    @validator("papers")
    def set_papers(cls, value):
        if value:
            for paper in value:
                try:
                    cls.add_paper(paper)
                except Exception:
                    pass
        else:
            return set()

    def set_query(self, query: str) -> None:
        self.query = query

    def add_database(self, database_name: str) -> None:
        if database_name not in AVAILABLE_DATABASES:
            raise ValueError(f"Database {database_name} is not supported.")
        self.databases.add(database_name)

    def get_paper_key(
        self, paper_title: str, publication_date: date, paper_doi: Optional[str] = None
    ) -> str:
        return (
            f"DOI-{paper_doi}"
            if paper_doi
            else f"{paper_title.lower()}|{publication_date.year if publication_date else ''}"
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

    # TODO: check this. Currently the code is copied directly from findpapers
    def add_paper(self, paper: Paper) -> None:
        if not paper.databases:
            raise ValueError(
                "Paper cannot be added to search without at least one defined database."
            )

        for database in paper.databases:
            if self.databases and database.lower() not in self.databases:
                raise ValueError(f"Database {database} isn't in databases list.")
            if self.reached_its_limit(database):
                raise OverflowError(
                    "When the papers limit is provided, you cannot exceed it."
                )

        if database not in self.papers_by_database:
            self.papers_by_database[database] = set()

        if paper.publication:
            publication_key = self.get_publication_key(
                paper.publication.title,
                paper.publication.issn,
                paper.publication.isbn,
            )
            already_collected_publication = self.publication_by_key.get(publication_key)

            if already_collected_publication:
                already_collected_publication.enrich(paper.publication)
                paper.publication = already_collected_publication
            else:
                self.publication_by_key[publication_key] = paper.publication

        paper_key = self.get_paper_key(paper.title, paper.publication_date, paper.doi)
        already_collected_paper = self.paper_by_key.get(paper_key)

        if (self.since is None or paper.publication_date >= self.since) and (
            self.until is None or paper.publication_date <= self.until
        ):
            if already_collected_paper is None:
                self.papers.add(paper)
                self.paper_by_key[paper_key] = paper

                if paper.doi is not None:
                    self.paper_by_doi[paper.doi] = paper

            else:
                self.papers_by_database[database].add(already_collected_paper)

            already_collected_paper.enrich(paper)

            self.papers_by_database[database].add(paper)

    def get_paper(
        self, paper_title: str, publication_date: str, paper_doi: Optional[str] = None
    ) -> Paper:
        paper_key = self.get_paper_key(paper_title, publication_date, paper_doi)
        return self.paper_by_key.get(paper_key, None)

    def get_publication(
        self, title: str, issn: Optional[str] = None, isbn: Optional[str] = None
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

    # TODO: implement this
    def merge_duplications(self):
        pass

    def reached_its_limit(self, database: str) -> bool:
        n_dbs = (
            len(self.papers_by_database.get(database))
            if bool(self.papers_by_database.get(database))
            else 0
        )

        reached_general_limit = (
            self.limit is not None and len(self.papers) >= self.limit
        )
        reached_database_limit = (
            self.limit_per_database is not None
            and database in self.papers_by_database
            and n_dbs >= self.limit_per_database
        )

        return reached_general_limit or reached_database_limit

    @classmethod
    def from_dict(cls, search_dict: dict) -> "Search":
        return cls(**search_dict)
