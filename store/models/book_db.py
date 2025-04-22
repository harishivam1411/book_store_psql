from pydantic import Field
from store.models.base.base_db import CreateUpdateSchema, BaseSchema

class Book(CreateUpdateSchema):
    title : str = Field(...)
    isbn : str = Field(...)
    publication_date : str = Field(...)
    description : str = Field(...)
    page_count : int = Field(...)
    language : str = Field(...)
    author_id : str = Field(...)
    category_ids : list[str] = Field([])
    author: BaseSchema = Field({"id": "6683f946ec61bfa6a3c2d7c7", "name": "Unknown Author"})
    categories: list[BaseSchema] = Field([])
    average_rating : float = Field(0)
