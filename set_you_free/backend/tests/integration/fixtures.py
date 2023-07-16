import pytest

from set_you_free.backend.findpapers.models.paper import Paper
from set_you_free.backend.findpapers.models.publication import Publication
from set_you_free.backend.findpapers.models.search import Search
from set_you_free.backend.tests.integration.utils.paper_utils import create_paper_event
from set_you_free.backend.tests.integration.utils.publication_utils import create_publication_event
from set_you_free.backend.tests.integration.utils.search_utils import create_search_event


@pytest.fixture
def publication() -> Publication:
    return create_publication_event()


@pytest.fixture
def paper() -> Paper:
    return create_paper_event()


@pytest.fixture
def search() -> Search:
    return create_search_event()
