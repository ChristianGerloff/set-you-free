from random import choice

from faker import Faker
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.fields import Use

from findpapers.models.paper import Paper
from tests.integration.factories.publication_factory import PublicationFactory

faker = Faker("en_US")


class PaperFactory(ModelFactory):
    __model__ = Paper
    title = faker.text(max_nb_chars=20)
    abstract = faker.text(max_nb_chars=75)
    authors = [faker.name() for _ in range(5)]
    publication_date = faker.date_object()
    urls = {faker.url()}
    citations = faker.random_int(min=1, max=100)
    keywords = {faker.word() for _ in range(2)}
    number_of_pages = faker.random_int(min=1, max=10)
    pages = f"1-{number_of_pages - 1}"
    databases = {"IEEE", "PubMed", "Scopus"}
    selected = True
    # TODO: add the correct categories
    categories = choice([True, False])  # {"Facet A": ["Category A", "Category B"]}
    source = choice(["primary", "references", "cites"])
    # TODO: why isn't it generating the correct values as defined in the factory?
    publication: Use(PublicationFactory.build)
