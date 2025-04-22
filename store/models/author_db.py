from typing import Optional
from pydantic import Field
from store.models.base_db import CreateUpdateSchema
from store.models.base_model import BaseSchema
from store.models.author_model import AuthorBooksSchema

class Author(CreateUpdateSchema):
    name: str = Field(...)
    biography: str = Field(...)
    birth_date: str = Field(...)
    death_date: Optional[str] = Field(None)
    country: str = Field(...)
    book_count : int = Field(0)
    books : list[AuthorBooksSchema] = Field([])