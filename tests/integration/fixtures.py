import pytest

from findpaper.models.publication import Publication
from tests.integration.utils.publication_utils import create_publication_event

@pytest.fixture
def publication() -> Publication:
    return create_publication_event()