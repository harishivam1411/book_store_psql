from typing import Optional
from pydantic import BaseModel, Field

from store.models.base.base_model import CreateUpdateSchema, BookBaseSchema
   
class AuthorBooksSchema(BookBaseSchema):
    isbn: str = Field(..., examples=["9780547928227"])
    publication_date: str = Field(..., examples=["1937-09-21"])

class AuthorCreate(BaseModel):
    name: str = Field(..., examples=["Stephen King"])
    biography: str = Field(..., examples=["Stephen Edwin King is an American author of horror, supernatural fiction, suspense, crime, science-fiction, and fantasy novels."])
    birth_date: str = Field(..., examples=["1947-09-21"])
    country: str = Field(None, examples=["United States"])

class AuthorUpdate(BaseModel):
    name: str = Field(..., examples=["Stephen King"])
    biography: str = Field(..., examples=["Stephen Edwin King is an American author of horror, supernatural fiction, suspense, crime, science-fiction, and fantasy novels."])
    birth_date: str = Field(..., examples=["1947-09-21"])
    death_date: Optional[str] = Field(None, examples=["1973-09-02"])
    country: str = Field(None, examples=["United States"])

class AuthorCreateResponse(CreateUpdateSchema):
    name: str = Field(..., examples=["Stephen King"])
    biography: str = Field(..., examples=["Stephen Edwin King is an American author of horror, supernatural fiction, suspense, crime, science-fiction, and fantasy novels."])
    birth_date: str = Field(..., examples=["1947-09-21"])
    death_date: Optional[str] = Field(None, examples=["1947-09-21"])
    country: str = Field(None, examples=["United States"])
    book_count : int = Field(0, examples=[12])

class AuthorUpdateResponse(CreateUpdateSchema):
    name: str = Field(..., examples=["Stephen King"])
    biography: str = Field(..., examples=["Stephen Edwin King is an American author of horror, supernatural fiction, suspense, crime, science-fiction, and fantasy novels."])
    birth_date: str = Field(..., examples=["1947-09-21"])
    death_date: Optional[str] = Field(None, examples=["1973-09-02"])
    country: str = Field(None, examples=["United States"])
    book_count : int = Field(0, examples=[12])

class AuthorResponse(CreateUpdateSchema):
    name: str = Field(..., examples=["Stephen King"])
    biography: str = Field(..., examples=["Stephen Edwin King is an American author of horror, supernatural fiction, suspense, crime, science-fiction, and fantasy novels."])
    birth_date: str = Field(..., examples=["1947-09-21"])
    death_date: Optional[str] = Field(None, examples=["1973-09-02"])
    country: str = Field(None, examples=["United States"])
    book_count : int = Field(0, examples=[12])
    books : list[AuthorBooksSchema] = Field([], examples=[[
        AuthorBooksSchema(id="6683f946ec61bfa6a3c2d7c7", title="The Hobbit", isbn="9780547928227", publication_date="1937-09-21"),
        AuthorBooksSchema(id="6683f946ec61bfa6a3c2d7c7", title="The Hobbit", isbn="9780547928227", publication_date="1937-09-21")]])
    
class AuthorsResponse(CreateUpdateSchema):
    name: str = Field(..., examples=["Stephen King"])
    biography: str = Field(..., examples=["Stephen Edwin King is an American author of horror, supernatural fiction, suspense, crime, science-fiction, and fantasy novels."])
    birth_date: str = Field(..., examples=["1947-09-21"])
    death_date: Optional[str] = Field(None, examples=["1973-09-02"])
    country: str = Field(None, examples=["United States"])
    book_count : int = Field(0, examples=[12])
