from pydantic import Field
from store.models.base.base_db import CreateUpdateSchema, UserBaseSchema

class Review(CreateUpdateSchema):
    book_id : str = Field(...)
    user: UserBaseSchema = Field({"id": "6683f946ec61bfa6a3c2d7c7", "username": "Unknown user", "first_name": "Jane", "last_name": "Smith-Johnson"})
    rating: float = Field(...)
    title: str = Field(...)
    content: str = Field(...)
    