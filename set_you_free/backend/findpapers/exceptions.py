class PublicationTitleMissingError(Exception):
    def __init__(self) -> None:
        super().__init__("Publication's title is missing.")


class IncorrectISSNLengthError(Exception):
    def __init__(self) -> None:
        super().__init__("Publication's ISSN must be only 8 characters long.")


class MissingSearchQueryError(Exception):
    def __init__(self) -> None:
        super().__init__("Search query is missing.")


class UnsupportedDatabaseError(Exception):
    def __init__(self, database_name: str) -> None:
        super().__init__(f"Database {database_name} is not supported.")


class DatabaseNotSelectedError(Exception):
    def __init__(self) -> None:
        super().__init__("Paper cannot be added to search without at least one defined database.")


class PaperTitleMissingError(Exception):
    def __init__(self) -> None:
        super().__init__("Paper's title is missing.")


class PaperPublicationDateMissingError(Exception):
    def __init__(self) -> None:
        super().__init__("Paper's publication_date is missing.")


class InvalidSourceError(Exception):
    def __init__(self, sources: list[str]) -> None:
        super().__init__(f"Source of the paper is invalid. Valid sources are {sources}.")
