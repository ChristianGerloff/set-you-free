from decimal import Decimal
from typing import Optional, Union

from pydantic import BaseModel, Field, validator


class Publication(BaseModel):
    title: str = Field(..., examples="Fake title")
    isbn: Optional[str] = Field(None, examples="1234567890")
    issn: Optional[str] = Field(None, examples="12345678", max_length=8, min_length=8)
    publisher: Optional[str] = Field(None, examples="Fake publisher")
    category: Optional[str] = Field(None, examples="journal")
    cite_score: Optional[Decimal] = Field(None, examples=[1.0], ge=0.0, decimal_places=1)
    sjr: Optional[Decimal] = Field(None, examples=[2.0], ge=0.0, decimal_places=1)
    snip: Optional[Decimal] = Field(None, examples=[3.0], ge=0.0, decimal_places=1)
    subject_areas: Optional[set[str]] = Field(None, examples=["Fake subject area"])
    is_potentially_predatory: Optional[bool] = Field(None, examples=True)
    
    @validator("title")
    def check_title(cls, value: str) -> str:
        if not value:
            raise(ValueError("Publication's title is missing."))
        return value
    
    # TODO: is this useful?
    @validator("issn")
    def check_issn(cls, value: str) -> str:
        if value and len(value) != 8:
            raise(ValueError("Publication's ISSN is not 8 characters long."))
        return value
    
    @validator("category")
    def check_category(cls, value):
        if value is not None:
            if 'journal' in value.lower():
                value = 'Journal'
            elif any(s in value.lower() for s in ['conference', 'proceeding']):
                value = 'Conference Proceedings'
            elif 'book' in value.lower():
                value = 'Book'
            elif 'preprint' in value.lower():
                value = 'Preprint'
            elif 'thesis' in value.lower():
                value = 'Thesis'
            else:
                value = None
        return value
    
    @validator("category")
    def set_category(cls, value, values) -> str:
        return value if value is not None else values["title"]
    
    @validator("subject_areas")
    def set_subject_areas(cls, value) -> Union[set, None]:
        return value if value is not None else set()
    
    
    def enrich(self, publication: 'Publication') -> 'Publication':
        self.title = publication.title if self.title is None or len(self.title) < len(publication.title) else self.title
        self.isbn = publication.isbn if self.isbn is None else self.isbn
        self.issn = publication.issn if self.issn is None else self.issn
        self.publisher = publication.publisher if self.publisher is None else self.publisher
        self.category = publication.category if self.category is None and publication.category is not None else self.category
        self.cite_score = publication.cite_score if self.cite_score is None else self.cite_score
        self.sjr = publication.sjr if self.sjr is None else self.sjr
        self.snip = publication.snip if self.snip is None else self.snip
        if publication.subject_areas is not None:
            self.subject_areas.update([subject_area.strip() for subject_area in publication.subject_areas if subject_area is not None and len(subject_area.strip()) > 0])
        self.is_potentially_predatory = publication.is_potentially_predatory if not self.is_potentially_predatory and publication.is_potentially_predatory else self.is_potentially_predatory
    
    @classmethod
    def from_dict(cls, publication_dict: dict) -> 'Publication':
        return cls(**publication_dict)
