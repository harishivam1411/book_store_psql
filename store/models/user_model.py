from pydantic import BaseModel, Field, EmailStr

from store.models.base.base_model import CreateUpdateSchema, CreateSchema, BookBaseSchema

class RecentReviewsSchema(CreateSchema):
    book: BookBaseSchema = Field(..., examples=[BookBaseSchema(id="6683f946ec61bfa6a3c2d7c7", title="The Great Gatsby")])
    rating: int = Field(0, examples=[5])

class UserCreate(BaseModel):
    username : str = Field(..., examples=["booklover99"])
    email : EmailStr = Field(..., examples=["newuser@example.com"])
    password : str = Field(..., examples=["password123"])
    first_name : str = Field(..., examples=["John"])
    last_name : str = Field(..., examples=["Doe"])
    
class UserUpdate(BaseModel):
    username : str = Field(None, examples=["bookworm42"])
    email : EmailStr = Field(None, examples=["updated.email@example.com"])
    first_name : str = Field(None, examples=["Jane"])
    last_name : str = Field(None, examples=["Smith-Johnson"])

class UserCreateResponse(CreateUpdateSchema):
    username : str = Field(..., examples=["booklover99"])
    email : EmailStr = Field(..., examples=["newuser@example.com"])
    first_name : str = Field(..., examples=["John"])
    last_name : str = Field(..., examples=["Doe"])
    review_count : int = Field(0, examples=[12])

class UserUpdateResponse(CreateUpdateSchema):
    username : str = Field(None, examples=["bookworm42"])
    email : EmailStr = Field(None, examples=["updated.email@example.com"])
    first_name : str = Field(None, examples=["Jane"])
    last_name : str = Field(None, examples=["Smith-Johnson"])
    review_count : int = Field(None, examples=[12])

class UserResponse(CreateUpdateSchema):
    username : str = Field(..., examples=["booklover99"])
    email : EmailStr = Field(..., examples=["newuser@example.com"])
    first_name : str = Field(..., examples=["John"])
    last_name : str = Field(..., examples=["Doe"])
    review_count : int = Field(0, examples=[12])
    recent_reviews : list[RecentReviewsSchema] = Field([], examples=[
        RecentReviewsSchema(id="6683f946ec61bfa6a3c2d7c7", book= BookBaseSchema(id="6683f946ec61bfa6a3c2d7c7", title="The Great Gatsby"), rating=5, created_at= "2023-02-15T10:20:00Z"),
        RecentReviewsSchema(id="6683f946ec61bfa6a3c2d7c7", book= BookBaseSchema(id="6683f946ec61bfa6a3c2d7c7", title="The Great Gatsby"), rating=5, created_at= "2023-02-15T10:20:00Z")
    ])

class UsersResponse(CreateUpdateSchema):
    username : str = Field(..., examples=["booklover99"])
    email : EmailStr = Field(..., examples=["newuser@example.com"])
    first_name : str = Field(..., examples=["John"])
    last_name : str = Field(..., examples=["Doe"])
    review_count : int = Field(0, examples=[12])