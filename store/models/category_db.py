from pydantic import Field
from store.models.base.base_db import CreateUpdateSchema

class Category(CreateUpdateSchema):
    name: str = Field(...)
    description: str = Field(None)
    book_count: int = Field(0)
    