import logging
from dataclasses import dataclass, fields

import pandas as pd

from set_you_free.backend.findpapers.models.search import Search


@dataclass
class RayyanPaper:
    key: int
    title: str
    authors: list[str]
    databases: list[str]
    journal: str
    issn: str
    day: int
    month: int
    year: int
    volume: int = None
    issue: int = None
    pages: str = None
    publisher: str = None
    pmc_id: str = None
    pubmed_id: str = None
    url: list[str] = None
    abstract: str = None
    notes: str = None


class RayyanExport:
    def __init__(self, search_results: Search) -> None:
        self.search = search_results

    @property
    def rayyan(self) -> list:
        """List of rayyan papers.

        Returns:
            list: pandas compatible search results
        """
        return self.__rayyan

    @property
    def search(self) -> Search:
        """Results of literature search.

        Returns:
            Search: search results
        """
        return self.__search

    @search.setter
    def search(self, search_results) -> None:
        if len(search_results.papers) > 0:
            self.__search = search_results
            self._convert_to_rayyan()

    def _convert_to_rayyan(self) -> None:
        """Convert findpapers results for rayyan."""
        papers = self.search.papers
        try:
            rayyan = [
                RayyanPaper(
                    key=i,
                    title=p.title,
                    authors=p.authors,
                    databases=list(p.databases),
                    journal=p.publication.title,
                    issn=p.publication.issn,
                    day=p.publication_date.day,
                    month=p.publication_date.month,
                    year=p.publication_date.year,
                    pages=p.pages,
                    publisher=p.publication.publisher,
                    url=list(p.urls),
                    abstract=p.abstract,
                    notes=f"doi: {p.doi}",
                )
                for i, p in enumerate(papers, 1)
            ]  # start key from 1
        except Exception:
            logging.warning("Results can not be converted to rayyan", exc_info=True)
        else:
            self.__rayyan = rayyan

    def generate_rayyan_csv(self, filename: str = None) -> tuple[bytes | None, pd.DataFrame | None]:
        """Convert and save search results in a rayyan compatibe csv.

        Args:
            filename (str, optional): filename of csv. Defaults to None.

        Returns:
            csv: a rayyan compatible and encoded csv obj. Defaults to None.
            papers: pamdas dataframe of rayyan objects. Defaults to None.
        """
        if hasattr(self, "rayyan"):
            papers = pd.DataFrame(self.rayyan)

            # convert lists to strings
            list_names = [field.name for field in fields(RayyanPaper) if field.type == list[str]]

            csv_content = papers.copy()
            for f in list_names:
                csv_content[f] = [", ".join(l) for l in papers[f]]

            csv = csv_content.to_csv(index=False).encode("utf-8")
            if filename is not None:
                csv_content.to_csv(filename, index=False)
        else:
            papers = None
            csv = None
            logging.info("Empty results")
        return csv, papers
