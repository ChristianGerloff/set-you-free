import pytest

from findpapers.models.paper import Paper
from findpapers.models.search import Search
from findpapers.models.publication import Publication
from tests.integration.utils.paper_utils import create_paper_event
from tests.integration.utils.search_utils import create_search_event
from tests.integration.utils.publication_utils import create_publication_event


@pytest.fixture
def publication() -> Publication:
    return create_publication_event()


@pytest.fixture
def paper() -> Paper:
    return create_paper_event()


@pytest.fixture
def search() -> Search:
    return create_search_event()
