from set_you_free.backend.tests.integration.factories.paper_factory import Paper, PaperFactory


def create_paper_event() -> Paper:
    return PaperFactory.build()
