from tests.integration.factories.search_factory import Search, SearchFactory


def create_search_event() -> Search:
    return SearchFactory.build()
