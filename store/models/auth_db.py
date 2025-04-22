from pydantic import Field
from store.models.base.base_db import CreateSchema

class UserAuth(CreateSchema):
    username: str = Field(...)
    password: str = Field(...)