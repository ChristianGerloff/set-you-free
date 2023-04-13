from tests.integration.factories.paper_factory import PaperFactory, Paper


def create_paper_event() -> Paper:
    return PaperFactory.build()
