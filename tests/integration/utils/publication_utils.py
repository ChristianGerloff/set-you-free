from tests.integration.factories.publication_factory import PublicationFactory, Publication


def create_publication_event() -> Publication:
    return PublicationFactory.build()