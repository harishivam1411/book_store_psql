from pydantic import Field, EmailStr
from store.models.base.base_db import CreateUpdateSchema
from store.models.user.user_model import RecentReviewsSchema

class User(CreateUpdateSchema):
    username: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)
    review_count: int = Field(0)
    recent_reviews: list[RecentReviewsSchema] = Field([])