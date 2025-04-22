from fastapi import HTTPException
from bson import ObjectId
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

from store.utils.util import get_hashed_password
from store.models.user.user_db import User
from store.models.user.user_model import UserCreate, UserUpdate, UserCreateResponse, UserUpdateResponse, UserResponse, UsersResponse

class UserService:
    def __init__(self, db : AsyncIOMotorClient):
        self.db = db
        self.collection = db.user
        self.book_collection = db.book
        self.author_collection = db.author
        self.review_collection = db.review
        self.category_collection = db.category

    async def retrieve_users(self) -> list[UsersResponse]:
        result = self.collection.find()
        users = []
        async for user in result:
            user = self.__replace_id(user)
            user["recent_reviews"] = user.get("recent_reviews") or []
            users.append(UserResponse(**user))
        return users

    async def create_user(self, user_create: UserCreate) -> UserCreateResponse:
        # Check if username or email already exists
        existing_user = await self.collection.find_one({
            "$or": [
                {"username": user_create.username},
                {"email": user_create.email}
            ]
        })
        
        if existing_user:
            if existing_user.get("username") == user_create.username:
                raise HTTPException(status_code=400, detail="Username already exists")
            else:
                raise HTTPException(status_code=400, detail="Email already exists")
        
        # Hash the password
        user_dict = user_create.model_dump()
        user_dict["password"] = get_hashed_password(user_dict["password"])
        user_dict["review_count"] = 0
        user_dict["recent_reviews"] = []
        
        user = User(**user_dict)
        result = await self.collection.insert_one(user.model_dump())
        
        return await self.retrieve_user(str(result.inserted_id))

    async def retrieve_user(self, user_id: str) -> UserResponse:
        try:
            user = await self.collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            user = self.__replace_id(user)
   
            # Get recent reviews
            if not user.get("recent_reviews"):
                user["recent_reviews"] = []
                
            return UserResponse(**user)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def update_user(self, user_id: str, user_update: UserUpdate) -> UserUpdateResponse:
        # Check if user exists
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update only provided fields
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Check if username or email are being updated and if they already exist
        if "username" in update_data:
            existing = await self.collection.find_one({
                "username": update_data["username"],
                "_id": {"$ne": ObjectId(user_id)}
            })
            if existing:
                raise HTTPException(status_code=400, detail="Username already exists")
        
        if "email" in update_data:
            existing = await self.collection.find_one({
                "email": update_data["email"],
                "_id": {"$ne": ObjectId(user_id)}
            })
            if existing:
                raise HTTPException(status_code=400, detail="Email already exists")
        
        # Update timestamp
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        # Update user
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        # Return updated user
        return await self.retrieve_user(user_id)
    @staticmethod
    def __replace_id(document):
        document['id'] = str(document.pop('_id'))
        return document