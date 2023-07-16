from datetime import date

# from random import choice
from faker import Faker
from polyfactory.factories.pydantic_factory import ModelFactory

from set_you_free.backend.findpapers.models.search import Search

faker = Faker("en_US")


class SearchFactory(ModelFactory):
    __model__ = Search
    query = '"this" AND ("that thing" OR "something") AND NOT "anything"'
    since = date(1969, 1, 30)  # faker.date()
    until = date(1970, 4, 8)  # faker.date()
    limit = 2
    databases = {"IEEE", "PubMed", "Scopus", "arXiv"}
    papers: set = set()
    paper_by_key: dict = {}
    publication_by_key: dict = {}
    paper_by_doi: dict = {}
    papers_by_database: dict = {}
