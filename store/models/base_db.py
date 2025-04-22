from datetime import datetime, timezone
from pydantic import BaseModel, Field

class CreateSchema(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CreateUpdateSchema(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BaseSchema(BaseModel):
    id: str = Field(...)
    name: str = Field(...)

class BookBaseSchema(BaseModel):
    id: str = Field(...)
    title: str = Field(...)

class UserBaseSchema(BaseModel):
    id: str = Field(...)
    username: str = Field(...)