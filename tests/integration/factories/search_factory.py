from random import choice

from pydantic_factories import ModelFactory
from faker import Faker

from findpapers.models.search import Search

faker = Faker("en_US")


class SearchFactory(ModelFactory):
    __model__ = Search
    query = '"this" AND ("that thing" OR "something") AND NOT "anything"'
    since = faker.date()
    until = faker.date()
    paper_by_key: dict = {}
    publication_by_key: dict = {}
    paper_by_doi: dict = {}
    papers_by_database: dict = {}
