from random import choice

from polyfactory.factories.pydantic_factory import ModelFactory, Use
from faker import Faker

from findpapers.models.publication import Publication

faker = Faker("en_US")


class PublicationFactory(ModelFactory):
    __model__ = Publication
    title = faker.text(max_nb_chars=20)
    isbn = faker.sbn9(separator="")
    issn = faker.ean(length=8)
    publisher = Use(faker.company)
    category = choice(
        ["journal", "conference", "proceeding", "book", "preprint", "thesis"]
    )
