from tests.integration.factories.publication_factory import (
    Publication,
    PublicationFactory,
)


def create_publication_event() -> Publication:
    return PublicationFactory.build()
